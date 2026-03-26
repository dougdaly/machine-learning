import os


def env_or_default(name: str, default: str) -> str:
    return os.environ.get(name, default)


PIPELINE_MODE = env_or_default("PIPELINE_MODE", "stub")
LLM_PROVIDER = env_or_default("LLM_PROVIDER", "openai")

PROCESSING_INSTANCE_TYPE_DEFAULT = env_or_default(
    "PROCESSING_INSTANCE_TYPE_DEFAULT",
    "ml.t3.medium",
)

TRAINING_INSTANCE_TYPE_DEFAULT = env_or_default(
    "TRAINING_INSTANCE_TYPE_DEFAULT",
    "ml.t3.medium",
)

EVALUATION_INSTANCE_TYPE_DEFAULT = env_or_default(
    "EVALUATION_INSTANCE_TYPE_DEFAULT",
    "ml.t3.medium",
)
