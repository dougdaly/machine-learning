from pathlib import Path
import json

from parse_request import write_request_json


def main() -> None:
    prompt = "Load example entitlements data for 6/2/2024-6/10/2024"

    base_dir = Path(__file__).resolve().parent
    request_path = base_dir / "request.json"

    written = write_request_json(
        prompt=prompt,
        output_path=str(request_path),
        use_llm=False,
    )

    print(f"Wrote request file to: {written}")
    print(json.dumps(json.loads(written.read_text()), indent=2))


if __name__ == "__main__":
    main()
