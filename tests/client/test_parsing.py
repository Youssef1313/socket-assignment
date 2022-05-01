from src.client.HttpMethod import HttpMethod
from src.client.HttpRequest import HttpRequest
from src.client.InputParser import InputParser


def test_minimal_allowed():
    parser = InputParser("""GET file host""")
    requests = parser.parse_input()
    assert len(requests) == 1
    assert_request("file", "host", 80, HttpMethod.GET, requests[0])

def test_minimal_allowed_with_port():
    parser = InputParser("""GET file host 8080""")
    requests = parser.parse_input()
    assert len(requests) == 1
    assert_request("file", "host", 8080, HttpMethod.GET, requests[0])

def assert_request(expected_filename: str,
                   expected_hostname: str,
                   expected_portnumber: int,
                   expected_method: HttpMethod,
                   request: HttpRequest):
    assert request.file_name == expected_filename
    assert request.host_name == expected_hostname
    assert request.port_number == expected_portnumber
    assert request.method == expected_method
