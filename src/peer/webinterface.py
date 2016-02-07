import urllib, logging
from urllib import request

class UnknownRequest(Exception):
    pass

class Webinterface(object):

    WEBINTERFACE = 'p2psearch.com'
    
    def __init__(self, index):

        self._index = index


    @staticmethod
    def _format_html_entry(doc):
        return '<li><a href="#">%s</a></li>' % doc.title

    def _show_stats(self, path, requesthandler):
        requesthandler.send_response(200)
        requesthandler.send_header('Content-type', 'Content-Type: text/html; charset=utf-8')
        requesthandler.end_headers()

        docs = map(Webinterface._format_html_entry,
                   self._index.docs)

        requesthandler.wfile.write(('<html><body><h1>P2P Search</h1>\
        <div>\
        <h1>stats</h1>\
        <ul>\
        %s\
        </ul>\
        </div>\
        </body></html>' % ''.join(docs)).encode('utf-8'))
        requesthandler.wfile.close()        
    

    def _serve_webinterface(self, path, requesthandler):
        requesthandler.send_response(200)
        requesthandler.send_header('Content-type', 'Content-Type: text/html; charset=utf-8')
        requesthandler.end_headers()

        requesthandler.wfile.write('<html><body><h1>P2P Search</h1>\
        <div>\
        <input type="text">\
        <button type="submit">\
        </div>\
        <pre>hi</pre>\
        </body></html>'.encode('utf-8'))
        requesthandler.wfile.close()


    def process_request(self, requesthandler):
        _, netloc, path, _, _ = \
                urllib.parse.urlsplit(requesthandler.path)

        if netloc == self.WEBINTERFACE:

            logging.info('path: %s' % path)

            if path == '/stats':
                self._show_stats(path, requesthandler)
            else:
                self._serve_webinterface(path, requesthandler)
        else:
            raise UnknownRequest()
