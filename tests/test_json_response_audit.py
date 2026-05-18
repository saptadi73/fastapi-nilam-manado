from scripts.audit_json_response import SCAN_FILES, audit_files


def test_all_route_handlers_use_json_response_handler():
    issues = audit_files(SCAN_FILES)
    assert issues == [], "\n".join(issues)
