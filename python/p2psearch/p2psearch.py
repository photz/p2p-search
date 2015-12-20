import httplib
import SimpleHTTPServer
import SocketServer
import threading


# Server
def server():
    try:
        SERVERPORT = 8080
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", SERVERPORT), Handler)
        print "serving at port", SERVERPORT
        httpd.serve_forever()
    except:
        print "Problems starting Server"


# Client
def client():
    try:
        CLIENTPORT = 8080
        conn = httplib.HTTPConnection('localhost', CLIENTPORT)
        conn.request("GET", "/simpleHTTPserver.py")
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        # data1 = r1.read()
        conn.close()
    except:
        print "Problems starting Client"

threads = []

tserver = threading.Thread(target=server)
tclient = threading.Thread(target=client)
threads.append(tserver)
threads.append(tclient)
tserver.start()
tclient.start()
