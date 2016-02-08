from signalslot.signal import Signal
import urllib, logging, json
from urllib import request

user_poses_query_signal = Signal(args=['query'])

class UnknownRequest(Exception):
    pass



class Webinterface(object):

    WEBINTERFACE = 'p2psearch.com'
    
    WEBINTERFACE_FILE = './webinterface.html'

    def __init__(self, index):

        self._index = index
        self._cached_results = list()
        
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



    def got_results(self, results):
        self._cached_results.extend(results)



    def _handle_query(self, path, requesthandler):
        _, _, _, query, _ = \
                urllib.parse.urlsplit(requesthandler.path)

        q = urllib.parse.parse_qs(query, strict_parsing=True)

        continued_query = q.get('continued_query', [False])[0]

        if continued_query == 'false':
            continued_query = False
        elif continued_query == 'true':
            continued_query = True
        else:
            continued_query = False

        if 'query' in q:

            results_arr = list()

            search_query = q['query'][0]

            if not continued_query:

                results_docs = list(self._index.query(search_query))

                for doc in results_docs:
                    results_arr.append({
                        'title' : doc.title,
                        'url' : doc.url
                    })

                user_poses_query_signal.emit(query=search_query)

                # clear the results cache
                self._cached_results.clear()

            else:
                logging.debug('CONTINUED_QUERY=TRUE')
                for doc in self._cached_results:
                    results_arr.append({
                        'title' : doc.title,
                        'url' : doc.url
                    })

                self._cached_results.clear()
                
                    
            logging.debug(results_arr)

            logging.info('searching for ... %s' % search_query)

            requesthandler.send_response(200)
            requesthandler.send_header('Content-type',
                                       'Content-Type: application/json; charset=utf-8')
            requesthandler.end_headers()

            requesthandler.wfile.write(
                json.dumps(results_arr).encode('utf-8'))

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
