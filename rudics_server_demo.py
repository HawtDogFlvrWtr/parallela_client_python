import http.server
import socketserver
import json

PORT = 8000

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        response_data = [
            {
                "command": "example_app\y-cruncher\y-cruncher.exe bench 250m -TD:2 -PF:none",
                "cpus": 1,
                "memory": 1024,
                "gpus": 0
            }
        ]
        self.wfile.write(json.dumps(response_data).encode("utf-8"))

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()