#!/usr/bin/env python3
import socketserver
import http.server
import urllib.request
import urllib.error
PORT = 8088

# Do not follow redirect just return whatever the other server returns
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(NoRedirect)
urllib.request.install_opener(opener)

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        res = self.do_request(method='GET')
        self.copyfile(res, self.wfile)

    def do_HEAD(self):
        self.do_request(method='HEAD')

    def do_request(self, method='GET'):
        # remove the separator so it only leaves http....
        url=self.path.lstrip('/?')
        # get the headers and delete the proxy Host
        headers=self.headers
        del headers['Host']
        # Make the request to the server
        req = urllib.request.Request(url, headers=headers, method=method)
        try:
            res = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            res = e
        # Log the request and return the status and headers
        self.log_request(res.status)
        self.send_response_only(res.status)
        for key, val in res.getheaders():
            self.send_header(key, val)
        self.end_headers()

        # return the result for further processing
        return res

httpd = socketserver.ForkingTCPServer(('', PORT), Proxy)
print ("Now serving at", str(PORT))
httpd.serve_forever()
