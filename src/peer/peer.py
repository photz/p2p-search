from signalslot.signal import Signal

import socket, logging, string

import message, config

new_message_signal = Signal(args=['msg'])
quit_signal = Signal(args=['peer'])
connection_to_peer_established_signal = Signal(args=['peer'])

class ConnectionToPeerFailed(Exception):
    pass

class DeferProcessing(Exception):
    pass

class WeWantToConnectState(object):
    def __init__(self, peer):
        self.__peer = peer

        self._initialize()

    def _initialize(self):
        logging.info('entering state %s' % type(self))
        assert type(self.__peer._socket) is socket.socket
        hello_msg = message.Message(ttl=1, hops=0,
                                    payload=message.HelloPayload(config.dest_port))
        
        self.__peer.send_message(hello_msg)



        self.__peer._state = InitializedState(self.__peer)

    def process_message(self, msg):
        new_message_signal.emit(msg=msg)


class TheyWantToConnectState(object):
    def __init__(self, peer):
        logging.info('entering state %s' % type(self))
        self.__peer = peer

    def process_message(self, msg):
        # a message has been received
        if msg.payload.payload_type == message.PayloadType.hello:
            self.__peer._dest_port = msg.payload.dest_port
            self.__peer._state = InitializedState(self.__peer)
            
            logging.info('the peer informed us that his destination ' +
                         'port is %d' % self.__peer._dest_port)

        else:
            # we expected a hello message but got something else
            logging.warning('expected hello message from peer, ' +
                            'but received something else')





class InitializedState(object):
    def __init__(self, peer):
        logging.info('entering state %s' % type(self))
        self.__peer = peer
        connection_to_peer_established_signal.emit(peer=self.__peer)


    def process_message(self, msg):
        new_message_signal.emit(msg=msg)
        

class Peer(object):

    SOCKET_TIMEOUT_S = 5

    def __init__(self, socket, dest_port=None, state=None):
        self._socket = socket
        self._dest_port = dest_port
        self._state = state(self)

        self.handle = socket.fileno()
        self.__buffer = bytes()
        self._closed = False

    def get_ip(self):
        return self._socket.getsockname()[0]
    
    @staticmethod
    def create_by_accepting(sock):
        connection, address = sock.accept()
        connection.setblocking(0)
        return Peer(connection, state=TheyWantToConnectState)

    @staticmethod
    def connect(ip, dest_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.settimeout(Peer.SOCKET_TIMEOUT_S)

        try:
            sock.connect((ip, dest_port))
        except socket.error as exc:
            sock.close()

            raise ConnectionToPeerFailed('could not connect to %s:%d'
                                         % (ip, dest_port))

        sock.setblocking(0)

        new_peer = Peer(sock, dest_port=dest_port,
                        state=WeWantToConnectState)

        return new_peer
            

    def send_message(self, message):
        """Sends a message to the peer represented by the Peer object"""

        sent_bytes = self._socket.send(message.serialize())

        logging.info('%s - sent %d bytes'
                     % (message.payload.payload_type, sent_bytes))

    def get_dest_port(self):
        return self._dest_port


    def readable_callback(self):
        """This method is meant to be called whenever the 
        socket pointed to by the _socket attribute becomes readable
        without blocking"""

        MAX_READ = 1 << 12

        if self._closed:
            logging.debug('received some data, but the connection ' +
                          'has been marked as closed')
            return

        logging.debug('incoming data')

        try:
            self.__buffer += self._socket.recv(MAX_READ)
        except ConnectionResetError:
            self._closed = True
            self.hangup_callback()
            return

        while len(self.__buffer) > 0:
            try:
                nbytes, msg = message.Message.parse(self.__buffer,
                                                    sender=self)

            except message.MessageTransferIncomplete:
                # the buffer does not contain the entire message,
                # so we'll do nothing and wait until this callback
                # gets called again
                return
            except message.InvalidHeader:
                logging.error('received a message with an invalid header')
            except message.InvalidPayload:
                logging.error('received a message with an invalid payload')
            else:
                # a message has been received
                logging.debug('incoming msg')

                try:
                    self._state.process_message(msg)
                    
                except DeferProcessing:
                    logging.info('processing of the message deferred')
                    return
                else:
                    self.__buffer = self.__buffer[nbytes:]

                logging.debug('%d bytes remaining in buffer' % len(self.__buffer))


    def good_bye(self):
        self._closed = True
        self._socket.shutdown(socket.SHUT_RDWR)


    def error_callback(self):
        logging.error('error callback called')

        self._closed = True

        quit_signal.emit(peer=self)

    def hangup_callback(self):
        logging.info('hangup_callback called')

        self._closed = True

        quit_signal.emit(peer=self)


        self._socket.close()

    def __str__(self):
        if self._dest_port:
            return '<%s:%d>' % (self.get_ip(), self._dest_port)
        else:
            return '<%s:unknown port>' % self.get_ip()
