import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.client.WebClient import WebClient
from src.client.InputParser import InputParser

input_file = os.path.abspath(os.path.join(os.path.dirname(__file__), sys.argv[1]))
with open(input_file, 'r') as f:
    commands = f.read()

client = WebClient()
requests = InputParser.parse_input(commands)
print(f"Input file contains {len(requests)} request(s).")

for request in requests:
    print(f"Sending '{request.method.name}' request to '{request.host_name}:{request.port_number}' for '{request.file_name}'.")
    client.send_request(request)
