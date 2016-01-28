from signalslot.signal import Signal

import socket, logging

import servlet

new_servlet_signal = Signal(args=['new_servlet'])

class Server(object):
    def __init__(self, dest_port=None):
        self.__socket = self.__create_server_socket(dest_port=dest_port)
        self.handle = self.__socket.fileno()

    def get_port(self):
        return self.__socket.getsockname()[1]

    @staticmethod
    def  __create_server_socket(dest_port=None):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if dest_port:
            serversocket.bind((socket.gethostname(), dest_port))


        serversocket.listen(5)
        serversocket.setblocking(0)
        return serversocket

    def readable_callback(self):
        logging.info('incoming connection')

        new_servlet = servlet.Servlet.create_by_accepting(self.__socket)

        new_servlet_signal.emit(new_servlet=new_servlet)
