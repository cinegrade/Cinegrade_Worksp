import http.server
import socketserver
import json
import os

PORT = 8765
INBOUND_DIR = "dist/clips/"

class ShortcutHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            filename = data.get("filename", "airdropped_clip.mp4")
            filepath = os.path.join(INBOUND_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(b'')
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "SUCCESS", "routed_to": filepath}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            print(f"[SHORTCUT BRIDGE] Received inbound AirDrop drop -> {filename}")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            print(f"[ERROR] Shortcut bridge failed: {e}")

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    os.makedirs(INBOUND_DIR, exist_ok=True)
    with ReusableTCPServer(("", PORT), ShortcutHandler) as httpd:
        print(f"[SHORTCUT BRIDGE] Listening on port {PORT} for Apple Shortcuts / AirDrop ingress...")
        httpd.serve_forever()
