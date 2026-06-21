import http.server
import socketserver

HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Sovereign Cluster Dashboard</title>
    <style>
        body { background: #0f172a; color: #38bdf8; font-family: monospace; padding: 40px; }
        .card { background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 8px; }
        span { color: #4ade80; }
    </style>
    <script>
        async function fetchMetrics() {
            try {
                let res = await fetch('http://192.168.56.50:8000/get-data');
                let data = await res.json();
                document.getElementById('db-content').innerText = JSON.stringify(data, null, 2);
            } catch(e) { document.getElementById('db-content').innerText = 'Database offline...'; }
        }
        setInterval(fetchMetrics, 2000);
    </script>
</head>
<body onload="fetchMetrics()">
    <div class="card">
        <h2>Active Microservices Log Dashboard</h2>
        <p>Polling Debian API Database Layer [192.168.56.50]...</p>
        <pre id="db-content">Connecting...</pre>
    </div>
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(HTML.encode())

with socketserver.TCPServer(("0.0.0.0", 8800), Handler) as httpd:
    print("Alpine Static Server running on Port 8800...")
    httpd.serve_forever()