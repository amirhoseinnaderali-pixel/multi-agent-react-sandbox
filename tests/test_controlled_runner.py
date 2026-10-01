from scripts.run_controlled import extract_code, feedback_text


def test_extract_code():
    fence = chr(96) * 3
    source = fence + "python\nprint(1)\n" + fence
    assert extract_code(source) == "print(1)"


def test_feedback_text():
    rows = [{
        "passed": False,
        "expected": "2",
        "actual": "3",
        "stderr": "wrong",
    }]
    text = feedback_text(rows)
    assert "FAIL" in text
    assert "expected='2'" in text
