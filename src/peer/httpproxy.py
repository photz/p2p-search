from http import server
import urllib, logging
from urllib import request
from urllib.request import URLError
import document
from webinterface import UnknownRequest



class HttpProxy(server.HTTPServer):

    def __init__(self, proxy_port, webinterface, index):
        super(server.HTTPServer, self).__init__(('', proxy_port), HttpProxyRequestHandler)

        self.handle = self.fileno()
        self.webinterface = webinterface
        self.index = index

    def readable_callback(self):
        self.handle_request()



class HttpProxyRequestHandler(server.SimpleHTTPRequestHandler):


    def do_GET(self):

        try:
            self.server.webinterface.process_request(self)
        except UnknownRequest:
            self._serve_remote()

    def _serve_remote(self):

        try:
            page = request.urlopen(self.path)

        except URLError as urlerr:
            self.send_response(404)
            self.end_headers()
            #self.wfile.close()
            
        else:

            if page.headers.get_content_type() == 'text/html':
                logging.info('indexing %s' % self.path)
                
                html_as_bytes = page.read()

                new_doc = document.Document.from_html(html_as_bytes,
                                                      self.path)

                self.server.index.add(new_doc)

                self.send_response(200)
                self.send_header('Content-type',
                                 'Content-Type: text/html; charset=utf-8')
                self.end_headers()

                self.wfile.write(html_as_bytes)
                #self.wfile.close()


            else:
                
                self.copyfile(page, self.wfile)
