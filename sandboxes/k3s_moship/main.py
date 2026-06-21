import http.server
import socketserver
import redis

# Connect to the Redis Service using Kubernetes' internal CoreDNS name
r = redis.Redis(host='state-db-svc', port=6379, db=0, decode_responses=True)

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            # Increment the atomic hit counter stored in Redis
            count = r.incr('api_hits')
            response_text = f"Sovereign Python Backend Active!\nTotal Fleet Hits: {count}\n"
        except Exception as e:
            response_text = f"Backend active, but Redis connection failed: {e}\n"

        # Construct raw HTTP stream headers
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response_text.encode('utf-8'))

if __name__ == '__main__':
    with socketserver.TCPServer(("", 8000), CustomHandler) as httpd:
        print("Custom Python Server listening on port 8000...")
        httpd.serve_forever()