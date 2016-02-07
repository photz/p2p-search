import urllib, logging
from urllib import request

class UnknownRequest(Exception):
    pass



class Webinterface(object):

    WEBINTERFACE = 'p2psearch.com'
    
    WEBINTERFACE_FILE = './webinterface.html'

    def __init__(self, index):

        self._index = index

        
        self._webinterface_html = \
    open(Webinterface.WEBINTERFACE_FILE, 'r').read().encode('utf-8')

    @staticmethod
    def _format_html_entry(doc):
        return '<li><a href="#">%s</a></li>' % doc.title

    def _show_stats(self, path, requesthandler):
        requesthandler.send_response(200)
        requesthandler.send_header('Content-type',
                                   'Content-Type: text/html; charset=utf-8')
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

        requesthandler.wfile.write(self._webinterface_html)
        requesthandler.wfile.close()


    def _handle_query(self, path, requesthandler):
        _, _, _, query, _ = \
                urllib.parse.urlsplit(requesthandler.path)

        q = urllib.parse.parse_qs(query, strict_parsing=True)

        if 'query' in q:

            search_query = q['query'][0]

            logging.info('searching for ... %s' % search_query)

            requesthandler.send_response(200)
            requesthandler.send_header('Content-type', 'Content-Type: application/json; charset=utf-8')
            requesthandler.end_headers()

            requesthandler.wfile.write('[{"title":"Example Document", "url": "http://example.com"}]'.encode('utf-8'))
            requesthandler.wfile.close()

        else:
            logging.warning('got a malformed query from the browser')
            

    def process_request(self, requesthandler):
        _, netloc, path, _, _ = \
                urllib.parse.urlsplit(requesthandler.path)

        if netloc == self.WEBINTERFACE:

            logging.info('path: %s' % path)

            if path == '/stats':
                self._show_stats(path, requesthandler)
            elif path == '/query':
                self._handle_query(path, requesthandler)
            else:
                self._serve_webinterface(path, requesthandler)

        else:
            raise UnknownRequest()
