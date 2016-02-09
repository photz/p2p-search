#!/usr/bin/env python3

from random import choice, sample
import logging, argparse
from gnutella import Gnutella
import config

logging.basicConfig(level=logging.DEBUG)

class IPPortPair(object):
    def __init__(self, spec):
        self.ip, self.port = spec.split(':', 1)

        if not self.port.isdigit():
            raise ValueError('port must be numeric')

        self.port = int(self.port)


def get_args():
    arg_parser = argparse.ArgumentParser(description=u'',
                                         epilog=u"Example:\
p2psearch --dest-port 6000 --proxy-port=3128 --peers 123.321.552.123:4000 849.345.543.344:61300")

    arg_parser.add_argument('--peers',
                            nargs='+',
                            type=IPPortPair,
                            help='list of IP:port pairs separated by a blank',
                            default=[])

    arg_parser.add_argument('--dest-port',
                            type=int,
                            help='the port on which we will listen for new incoming connections from other peers, will be chosen at random if not specified',
                            default=None)

    arg_parser.add_argument('--diagnosis',
                            help='optional IP:port pair of the diagnosis tool',
                            type=IPPortPair,
                            default=None)

    arg_parser.add_argument('--proxy-port',
                            help='the TCP port that will be used by the '\
                            'HTTP proxy server',
                            type=int,
                            default=3128)
                            

    return arg_parser.parse_args()

        

def main():

    args = get_args()

    config.dest_port = args.dest_port

    known_peers = ((p.ip, p.port) for p in args.peers)

    master = Gnutella(dest_port=args.dest_port,
                    known_peers=known_peers,
                    diagnosis_service=args.diagnosis,
                    proxy_port=args.proxy_port)

    master.run()

if __name__ == "__main__":
    main()
