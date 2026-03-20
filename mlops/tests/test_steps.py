from mlops.src.handler import (
    step1_add_flag,
    step2_count_keys,
    step3_add_timestamp,
)


def test_step1_add_flag():
    payload = {"a": 1}
    result = step1_add_flag(payload)
    assert result["step1"] == "completed"


def test_step2_count_keys():
    payload = {"a": 1, "b": 2}
    result = step2_count_keys(payload)
    assert "step2_key_count" in result


def test_step3_add_timestamp():
    payload = {"a": 1}
    result = step3_add_timestamp(payload)
    assert "processed_at_utc" in result
