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
                "id": 1,
                "user_id": 1,
                "bundle_id": '',
                "linked_job_queue_id": '',
                "count": 1,
                "count_finished": 0,
                "metadata": [
                    {
                        "command": "python demos/demo_cpu_app.py",
                        "cpus": 1,
                        "memory": 1024,
                        "gpus": 0
                    }
                ],
                "created_at": "2025-10-31T19:50:56.000000Z",
                "updated_at": "2025-10-31T19:50:56.000000Z"
            }
        ]
        self.wfile.write(json.dumps(response_data).encode("utf-8"))

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()