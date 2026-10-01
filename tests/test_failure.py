from vmar_ps.failure import classify_failure

def test_syntax_error_classification():
    assert classify_failure({"compiled": False, "error": "invalid syntax"}) == "syntax_error"

def test_wrong_output_classification():
    result = {"compiled": True, "execution_success": True, "tests_failed": 1, "error": "Output mismatch"}
    assert classify_failure(result) == "wrong_output"
