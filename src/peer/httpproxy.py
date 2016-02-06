from http import server
import urllib
from urllib import request





class HttpProxy(server.HTTPServer):

    def __init__(self, proxy_port):
        super(server.HTTPServer, self).__init__(('', proxy_port), HttpProxyRequestHandler)

        self.handle = self.fileno()

    def readable_callback(self):
        self.handle_request()



class HttpProxyRequestHandler(server.SimpleHTTPRequestHandler):

    WEBINTERFACE = 'p2psearch.com'

    def serve_webinterface(self, path):
        self.send_response(200)
        self.send_header('Content-type', 'Content-Type: text/html; charset=utf-8')
        self.end_headers()

        self.wfile.write(b'<html><body><h1>P2P Search</h1>\
        <div>\
        <input type="text">\
        <button type="submit">\
        </div>\
        <pre>hi</pre>\
        </body></html>')
        self.wfile.close()


    def do_GET(self):

        print('GET ', self.path)

        _, netloc, path, _, _ = urllib.parse.urlsplit(self.path)

        if netloc == self.WEBINTERFACE:
            self.serve_webinterface(path)
        else:
            page = request.urlopen(self.path)

            if page.headers.get_content_type() == 'text/html':
                print('index %s' % self.path)
                    

            #self.copyfile(urllib.urlopen(self.path), self.wfile)
            self.copyfile(page, self.wfile)
