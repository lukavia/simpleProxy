#!/usr/bin/env python3
import socketserver
import http.server
import urllib.request
import urllib.error
import urllib.parse
import re
import os.path

# Do not follow redirect just return whatever the other server returns
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(NoRedirect)
urllib.request.install_opener(opener)

class Proxy(http.server.SimpleHTTPRequestHandler):
    server_version = "simpleProxy"
    def do_GET(self):
        res = self.do_request(method='GET')
        if isinstance(res, http.client.HTTPResponse) and res.status == 200:
            length = 64 * 1024
            os.makedirs(os.path.dirname(res.cache_file), exist_ok=True)
            f = open(res.cache_file, mode='wb')
            while True:
                buf = res.read(length)
                if not buf:
                    break
                self.wfile.write(buf)
                f.write(buf)
            f.close()
        else:
            self.copyfile(res, self.wfile)

    def do_HEAD(self):
        self.do_request(method='HEAD')

    def do_request(self, method='GET'):
        # remove the separator so it only leaves http....
        url=self.path.lstrip('/?')

        path = '.cache/'

        parts = urllib.parse.urlsplit(url)

        # Todo make those configurable
        # just 2 level domain, no port
        path = path + '.'.join(parts.netloc.split('.')[-2:]).split(':')[0]
        # remove session/XXXXXX from path
        path = path + re.sub(r'/session/[^/]*', '', parts.path)

        if os.path.isfile(path):
            self.path = path
            return self.send_head()
        else:
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
            # So we can write it later
            res.cache_file = path
            for key, val in res.getheaders():
                self.send_header(key, val)
            self.end_headers()

            # return the result for further processing
            return res

if __name__ == '__main__':
    PORT = 8088

    httpd = socketserver.ForkingTCPServer(('', PORT), Proxy)
    print ("Now serving at", str(PORT))
    httpd.serve_forever()
