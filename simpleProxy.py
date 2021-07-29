import socketserver
import http.server
import urllib.request
PORT = 8089

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url=self.path.lstrip('/?')
        self.send_response(200)
        self.end_headers()
        headers=self.headers
        del headers['Host']
        req = urllib.request.Request(url, headers=headers)
        self.copyfile(urllib.request.urlopen(req), self.wfile)

httpd = socketserver.ForkingTCPServer(('', PORT), Proxy)
print ("Now serving at", str(PORT))
httpd.serve_forever()
