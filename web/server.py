import log
import http.server
import os
import sys
sys.path.append("../")

server_address = ("", int(os.environ.get("PORT", 5000)))
handler_class = http.server.CGIHTTPRequestHandler
server = http.server.HTTPServer(server_address, handler_class)
server.serve_forever()
