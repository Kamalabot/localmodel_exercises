import http.server
import sqlite3
import json

# Setup minimal file-backed SQLite tracking database
conn = sqlite3.connect('/opt/db/cluster.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY, msg TEXT, ts TEXT)')
conn.commit()
conn.close()

class APIHandler(http.server.BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == '/add-data':
            length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(length).decode())
            
            conn = sqlite3.connect('/opt/db/cluster.db')
            c = conn.cursor()
            c.execute('INSERT INTO metrics (msg, ts) VALUES (?, ?)', (body['msg'], body['ts']))
            conn.commit()
            conn.close()
            
            self.send_response(201)
            self.end_headers()

    def do_GET(self):
        if self.path == '/get-data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            conn = sqlite3.connect('/opt/db/cluster.db')
            c = conn.cursor()
            c.execute('SELECT msg, ts FROM metrics ORDER BY id DESC LIMIT 5')
            rows = c.fetchall()
            conn.close()
            
            data = [{"msg": r[0], "timestamp": r[1]} for r in rows]
            self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', 8000), APIHandler)
    print("Debian DB Engine listening on Port 8000...")
    server.serve_forever()