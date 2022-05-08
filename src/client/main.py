import sys
sys.path.insert(0, '.')

from src.client.WebClient import WebClient
from src.client.HttpRequest import HttpRequest
from src.common.HttpMethod import HttpMethod

client = WebClient()
client.send_request(HttpRequest(HttpMethod.GET, "/dotnet/docs", "github.com", 443))
client.send_request(HttpRequest(HttpMethod.GET, "/", "www.facebook.com", 443))
client.send_request(HttpRequest(HttpMethod.GET, "/", "info.cern.ch", 80))
