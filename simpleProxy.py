#!/usr/bin/env python3
import socketserver
import http.server
import urllib.request
import urllib.error
PORT = 8088

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


opener = urllib.request.build_opener(NoRedirect)
urllib.request.install_opener(opener)

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url=self.path.lstrip('/?')
        headers=self.headers
        del headers['Host']
        req = urllib.request.Request(url, headers=headers)
        try:
            res = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            res = e
        self.log_request(res.status)
        self.send_response_only(res.status)
        for key, val in res.getheaders():
            self.send_header(key, val)
        self.end_headers()
        self.copyfile(res, self.wfile)

    def do_HEAD(self):
        url=self.path.lstrip('/?')
        headers=self.headers
        del headers['Host']
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        try:
            res = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            res = e
        self.log_request(res.status)
        self.send_response_only(res.status)
        for key, val in res.getheaders():
            self.send_header(key, val)
        self.end_headers()
        self.copyfile(res, self.wfile)

httpd = socketserver.ForkingTCPServer(('', PORT), Proxy)
print ("Now serving at", str(PORT))
httpd.serve_forever()
