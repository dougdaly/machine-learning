import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
import os
import boto3
from openai import OpenAI
from request_schema import DataGenerationRequest, DataMode, ServiceName
import argparse
import dotenv

dotenv.load_dotenv()

def resolve_llm_provider(explicit_provider: str | None = None) -> str:
    '''Determine which LLM provider to use based on the following precedence:
        1. explicit_provider argument
        2. LLM_PROVIDER environment variable
        3. PIPELINE_MODE environment variable (if "full", use "bedrock")
        4. default to "openai"'''
    if explicit_provider:
        return explicit_provider

    pipeline_mode = os.environ.get("PIPELINE_MODE", "stub").strip().lower()
    env_provider = os.environ.get("LLM_PROVIDER")
    if env_provider:
        return env_provider.strip().lower()

    if pipeline_mode == "full":
        return "bedrock"

    return "openai"


DATE_RANGE_PATTERN = re.compile(
    r"(?P<start>\d{1,2}/\d{1,2}/\d{4})\s*[-to]+\s*(?P<end>\d{1,2}/\d{1,2}/\d{4})",
    re.IGNORECASE,
)


def normalize_date(value: str) -> str:
    dt = datetime.strptime(value, "%m/%d/%Y")
    return dt.strftime("%Y-%m-%d")


def deterministic_parse(prompt: str) -> Optional[DataGenerationRequest]:
    text = prompt.strip().lower()

    if "entitlement" in text:
        service = ServiceName.entitlements
    else:
        service = ServiceName.generic

    if "existing data" in text:
        data_mode = DataMode.existing
    else:
        data_mode = DataMode.synthetic

    match = DATE_RANGE_PATTERN.search(text)
    if not match:
        return None

    start_date = normalize_date(match.group("start"))
    end_date = normalize_date(match.group("end"))

    return DataGenerationRequest(
        service=service,
        data_mode=data_mode,
        start_date=start_date,
        end_date=end_date,
    )

def openai_parse(prompt: str) -> DataGenerationRequest:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing required environment variable: OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL")
    if not model:
        raise ValueError("Missing required environment variable: OPENAI_MODEL")

    schema = {
        "name": "data_generation_request",
        "schema": {
            "type": "object",
            "properties": {
                "request_type": {"type": "string", "enum": ["load_data"]},
                "service": {"type": "string", "enum": ["entitlements", "generic"]},
                "data_mode": {"type": "string", "enum": ["synthetic", "existing"]},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "output_prefix": {"type": "string"},
            },
            "required": [
                "request_type",
                "service",
                "data_mode",
                "start_date",
                "end_date",
                "output_prefix",
            ],
            "additionalProperties": False,
        },
    }

    system_prompt = (
        "Convert the user's request into a structured pipeline request. "
        "Normalize dates to YYYY-MM-DD. "
        "If the user asks for example or demo data, use data_mode='synthetic'. "
        "If the user mentions entitlements, use service='entitlements'; otherwise use 'generic'. "
        "Use request_type='load_data'. "
        "Use output_prefix='synthetic/raw'."
    )

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": schema["name"],
                "schema": schema["schema"],
                "strict": True,
            }
        },
    )

    payload = json.loads(response.output_text)
    return DataGenerationRequest(**payload)


def bedrock_parse(prompt: str) -> DataGenerationRequest:
    region = os.environ.get("AWS_REGION", "us-west-2")
    model_id = os.environ.get("BEDROCK_MODEL_ID")
    if not model_id:
        raise ValueError("Missing required environment variable: BEDROCK_MODEL_ID")

    client = boto3.client("bedrock-runtime", region_name=region)

    schema = {
        "type": "object",
        "properties": {
            "request_type": {"type": "string", "enum": ["load_data"]},
            "service": {"type": "string", "enum": ["entitlements", "generic"]},
            "data_mode": {"type": "string", "enum": ["synthetic", "existing"]},
            "start_date": {"type": "string"},
            "end_date": {"type": "string"},
            "output_prefix": {"type": "string"},
        },
        "required": [
            "request_type",
            "service",
            "data_mode",
            "start_date",
            "end_date",
            "output_prefix",
        ],
        "additionalProperties": False,
    }

    system_prompt = (
        """Convert the user's request into a structured pipeline request.
        Normalize dates to YYYY-MM-DD.
        If the user asks for example/demo data, use data_mode="synthetic".
        If the user mentions entitlements, use service="entitlements"; otherwise use "generic".
        Use request_type="load_data".
        Use output_prefix="synthetic/raw".
        Return only the structured tool input."""
    )

    response = client.converse(
        modelId=model_id,
        system=[{"text": system_prompt}],
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "maxTokens": 300,
            "temperature": 0.0,
        },
        additionalModelResponseFieldPaths=[],
        toolConfig={
            "tools": [
                {
                    "toolSpec": {
                        "name": "emit_request_json",
                        "description": "Emit a structured request object for the pipeline.",
                        "inputSchema": {
                            "json": schema
                        },
                    }
                }
            ]
        },
    )

    content = response["output"]["message"]["content"]

    tool_use_blocks = [block for block in content if "toolUse" in block]
    if not tool_use_blocks:
        raise ValueError(f"Model did not return tool input. Raw response content: {content}")

    payload = tool_use_blocks[0]["toolUse"]["input"]
    return DataGenerationRequest(**payload)

def parse_request(prompt: str, provider: str | None = None) -> DataGenerationRequest:
    provider = resolve_llm_provider(provider)
    if provider == "openai":
        return openai_parse(prompt)
    if provider == "bedrock":
         return bedrock_parse(prompt)
    if provider == "deterministic":
        return deterministic_parse(prompt)
    raise ValueError(f"Unknown provider: {provider}")

def write_request_json(prompt: str, output_path: str, provider: str | None = None) -> Path:
    parsed = parse_request(prompt, provider=provider)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(parsed.model_dump(), indent=2))
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a natural-language request into request.json")
    parser.add_argument(
        "--prompt",
        type=str,
        default="Load example entitlements data for 6/2/2024-6/10/2024",
        help="Natural-language request to parse",
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["deterministic", "openai", "bedrock"],
        default=None,
        help="Parsing backend to use. If omitted, resolved from PIPELINE_MODE/LLM_PROVIDER.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(Path(__file__).resolve().parent / "request.json"),
        help="Output path for request JSON",
    )

    args = parser.parse_args()

    written = write_request_json(
        prompt=args.prompt,
        output_path=args.output,
        provider=args.provider,
    )

    print(f"Wrote request JSON to {written}, using provider {args.provider}")
    print(Path(written).read_text())