import sys
sys.path.insert(0,'.')

from src.client.WebClient import WebClient
from src.client.HttpMethod import HttpMethod
from src.client.HttpRequest import HttpRequest

client = WebClient()
client.send_request(HttpRequest(HttpMethod.GET, "/dotnet/docs", "github.com", 80))
