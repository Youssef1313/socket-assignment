import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from WebServer import WebServer

print(f"Server running in '{os.getcwd()}'.")
server = WebServer(6678)
server.init_server()
