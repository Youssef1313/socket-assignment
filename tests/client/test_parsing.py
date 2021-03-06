from src.common.HttpMethod import HttpMethod
from src.client.HttpRequest import HttpRequest
from src.client.parse_input import parse_input


def test_minimal_allowed():
    requests = parse_input("""GET file host""")
    assert len(requests) == 1
    assert_request("/file", "host", 80, HttpMethod.GET, requests[0])


def test_minimal_allowed_with_port():
    requests = parse_input("""GET file host 8080""")
    assert len(requests) == 1
    assert_request("/file", "host", 8080, HttpMethod.GET, requests[0])


def assert_request(expected_filename: str,
                   expected_hostname: str,
                   expected_portnumber: int,
                   expected_method: HttpMethod,
                   request: HttpRequest):
    assert request.file_name == expected_filename
    assert request.host_name == expected_hostname
    assert request.port_number == expected_portnumber
    assert request.method == expected_method
