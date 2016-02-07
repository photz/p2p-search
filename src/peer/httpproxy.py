from http import server
import urllib, logging
from urllib import request

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
            page = request.urlopen(self.path)

            if page.headers.get_content_type() == 'text/html':
                logging.info('indexing %s' % self.path)
                
                html = page.read()
                new_doc = document.Document(html.decode('utf-8'))
                self.server.index.add(new_doc)

                self.send_response(200)
                self.send_header('Content-type',
                                 'Content-Type: text/html; charset=utf-8')
                self.end_headers()

                self.wfile.write(html)
                self.wfile.close()


            else:
                self.copyfile(page, self.wfile)
