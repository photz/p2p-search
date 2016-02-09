import logging, socket, json, datetime, random
from signalslot.signal import Signal

servlet_disconnected_signal = Signal(args=['disconnected_servlet'])

class ServletNotAlive(Exception):
    pass

class Servlet(object):

    def __init__(self, sock):

        self.__socket = sock
        self.handle = sock.fileno()
        self.pid = None
        self.__buffer = bytes()
        self.__peers = list()
        self.__alive = True
        self.__dest_port = None
        self.__created_at = datetime.datetime.now()

        
        self.color = {
            'h' : random.random(),
            's' : random.random(),
            'v' : 1
        }

    def get_created_at(self):
        return self.__created_at

    def get_peers(self):
        return self.__peers

    @staticmethod
    def create_by_accepting(sock):
        new_sock, _ = sock.accept()
        new_sock.setblocking(0)
        return Servlet(new_sock)


    def get_dest_port(self):
        return self.__dest_port

    def get_ip(self):
        
        return self.__socket.getsockname()[0]

    
    def hangup_callback(self):
        self.__alive = False
        self.__socket.close()
        servlet_disconnected_signal.emit(disconnected_servlet=self)

    def error_callback(self):
        logging.warning('peer has disappeared')

        self.__alive = False
        self.__socket.close()
        servlet_disconnected_signal.emit(disconnected_servlet=self)

    def is_alive(self):
        return self.__alive

    def request_status_update(self):
        if not self.__alive:
            raise ServletNotAlive('trying to send a message to a ' +
                                  'servlet that is not alive')
        
        self.__socket.send(b"\n")
    
    def __process_line(self, line):
        try:
            data = json.loads(line)
        except ValueError as value_error:
            logging.error('received an invalid message from a servlet: %s' % str(value_error))
        else:

            if 'peers' in data:
                self.__peers = data['peers']
            else:
                logging.warning('status update from peer was ' +
                                'missing a list of peers')

            if 'pid' in data:
                self.pid = data['pid']
            else:
                logging.warning('status update from peer missing pid')

            if 'dest_port' in data:
                self.__dest_port = data['dest_port']
                logging.debug('peer is using port %d' % data['dest_port'])
            else:
                logging.warning('status update from peer did not ' +
                                'contain its destination port')

    def readable_callback(self):
        if not self.__alive: return

        try:
            self.__buffer += self.__socket.recv(1 << 12)
        except ConnectionResetError:
            self.error_callback()
        else:

            logging.debug('buffer contents: %s' % self.__buffer)

            while True:
                linebreak_index = self.__buffer.find(b"\n")

                if linebreak_index >= 0:
                    first_line = self.__buffer[:linebreak_index]

                    self.__buffer = self.__buffer[linebreak_index+1:]

                    self.__process_line(first_line.decode('ASCII'))
                else:
                    break


    def __str__(self):
        if self.__dest_port:
            return '<%s:%d>' % (self.get_ip(), self.__dest_port)
        else:
            return '<%s:unknown port>' % self.get_ip()
            

    
    
