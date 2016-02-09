import logging, socket, json, string, config
from os import getpid

class DiagnosisServiceUnreachable(Exception):
    pass

class Diagnosis(object):
    def __init__(self, ip, port, gnutella):

        self.__gnutella = gnutella

        self.__socket = self.__create_socket(ip, port)
        self.__buffer = bytes()

        self.handle = self.__socket.fileno()


    @staticmethod
    def __create_socket(ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.settimeout(5)

        try:
            sock.connect((ip, port))
        except socket.error:
            sock.close()

            raise DiagnosisServiceUnreachable()
        else:
            sock.setblocking(0)

            return sock

    def __transmit_status_update(self):
        peers = list()

        for p in self.__gnutella._peers:
            peers.append({
                'ip' : p.get_ip(),
                'port' : p._dest_port
            })

        status_update = StatusUpdate(peers=peers,
                                     dest_port=config.dest_port)

        self.__socket.send((status_update.serialize() + "\n").encode('ASCII'))

    def readable_callback(self):
        self.__buffer = self.__socket.recv(1 << 12)

        self.__transmit_status_update()

    def error_callback(self):
        pass

    def hangup_callback(self):
        pass


class StatusUpdate(object):

    def __init__(self, peers, dest_port):
        self.__peers = peers
        self.__dest_port = dest_port

    def serialize(self):

        return json.dumps({
            'peers' : self.__peers,
            'dest_port' : self.__dest_port,
            'pid' : getpid()
        })

    @staticmethod
    def deserialize(serialized):
        pass
