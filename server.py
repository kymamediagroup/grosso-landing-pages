import os
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get('PORT', 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(BASE_DIR, 'pages')
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

class LandingPageRouter(SimpleHTTPRequestHandler):
    def do_GET(self):
        url_path = self.path.split('?')[0].strip('/')
        
        # 1. Health check
        if url_path in ('health', '_health', 'api/health'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'OK')
            return

        # 2. Root dashboard
        if url_path == '':
            index_path = os.path.join(PUBLIC_DIR, 'index.html')
            if os.path.exists(index_path):
                self.serve_file(index_path)
                return
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'<h1>Grosso University Landing Pages</h1>')
                return

        parts = url_path.split('/')
        slug = parts[0]
        slug_dir = os.path.join(PAGES_DIR, slug)

        # 3. Dynamic slug routing: /<slug> or /<slug>/...
        if os.path.isdir(slug_dir):
            if len(parts) == 1:
                target_file = os.path.join(slug_dir, 'index.html')
            else:
                target_file = os.path.join(slug_dir, *parts[1:])

            if os.path.isfile(target_file):
                self.serve_file(target_file)
                return

        # 4. Fallback: If browser requests /assets/... without /<slug> prefix, search across pages/top-500/assets or pages/*
        if parts[0] == 'assets':
            # Check pages/top-500/assets/...
            top500_asset = os.path.join(PAGES_DIR, 'top-500', *parts)
            if os.path.isfile(top500_asset):
                self.serve_file(top500_asset)
                return
            # Or public/assets
            pub_asset = os.path.join(PUBLIC_DIR, *parts)
            if os.path.isfile(pub_asset):
                self.serve_file(pub_asset)
                return

        # 5. Check public directory directly
        public_file = os.path.join(PUBLIC_DIR, *parts)
        if os.path.isfile(public_file):
            self.serve_file(public_file)
            return

        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(f'<h1>404 - Page /{url_path} Not Found</h1><p><a href="/">Back to Dashboard</a></p>'.encode('utf-8'))

    def serve_file(self, filepath):
        ctype, _ = mimetypes.guess_type(filepath)
        if not ctype:
            ctype = 'application/octet-stream'
        if ctype.startswith('text/') or ctype in ('application/javascript', 'application/json'):
            ctype += '; charset=utf-8'

        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

def run():
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, LandingPageRouter)
    print(f'Router running on port {PORT}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run()
