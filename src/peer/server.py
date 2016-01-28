from signalslot.signal import Signal

import socket, logging

import peer

new_peer_signal = Signal(args=['peer'])

class Server(object):

    Server.BACKLOG = 0

    def __init__(self, dest_port=None):
        self.__socket = self.__create_server_socket(dest_port=dest_port)
        self.handle = self.__socket.fileno()

    def get_ip(self):
        return self.__socket.getsockname()[0]

    def get_port(self):
        return self.__socket.getsockname()[1]

    @staticmethod
    def  __create_server_socket(dest_port=None):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if dest_port:
            serversocket.bind((socket.gethostname(), dest_port))


        serversocket.listen(Server.BACKLOG)
        serversocket.setblocking(0)
        return serversocket

    def readable_callback(self):
        logging.info('incoming connection')

        new_peer = peer.Peer.create_by_accepting(self.__socket)

        new_peer_signal.emit(peer=new_peer)
