import http.server
import os


server_address = ("", int(os.environ.get("PORT", 5000)))
handler_class = http.server.CGIHTTPRequestHandler
server = http.server.HTTPServer(server_address, handler_class)
server.serve_forever()
