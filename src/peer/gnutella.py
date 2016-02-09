from random import choice, sample
import logging, datetime


from httpproxy import HttpProxy
from dispatcher import EventDispatcher
import peer, server, config, message, diagnosis, webinterface, index



class Gnutella(object):

    MIN_PEERS = 2
    MAX_PEERS = 10

    def __init__(self, dest_port=None, known_peers=None,
                 diagnosis_service=None,
                 proxy_port=None):
        self._peers = set()
        self.__dispatcher = EventDispatcher()
        self.__server = server.Server(dest_port=dest_port)
        self.__messages = {}

        config.dest_port = self.__server.get_port()

        self.__dispatcher.register(self.__server)
        logging.info('using port %d' % self.__server.get_port())

        # connect signals

        peer.new_message_signal.connect(self.new_message_callback)
        peer.quit_signal.connect(self._peer_quits_callback)
        server.new_peer_signal.connect(self._new_peer_callback)
        peer.connection_to_peer_established_signal.connect(
            self._connection_to_peer_established_callback)
        webinterface.user_poses_query_signal.connect(
            self._user_poses_query_callback)
        
        if known_peers:
            self._connect_to_peers(known_peers)

        # diagnosis service
        if diagnosis_service:
            d = diagnosis.Diagnosis(diagnosis_service.ip,
                                    diagnosis_service.port,
                                    self)

            self.__dispatcher.register(d)

        # set up the index
        self._index = index.Index()

        # set up the webinterface
        self._webinterface = webinterface.Webinterface(self._index)

        # set up the HTTP proxy server
        self.__proxy = HttpProxy(proxy_port,
                                 self._webinterface,
                                 self._index)
        self.__dispatcher.register(self.__proxy)


    def run(self):
        # enter the event loop

        last_update = datetime.datetime.now()
        CHECK_FOR_NEW_PEERS_IF_NECESSARY_EVERY_S = 10.0
        while True:
            self.__dispatcher.handle_events(
                CHECK_FOR_NEW_PEERS_IF_NECESSARY_EVERY_S)

            if len(self._peers) > 0 \
               and len(self._peers) <= self.MIN_PEERS \
               and (datetime.datetime.now() - last_update) > datetime.timedelta(seconds=CHECK_FOR_NEW_PEERS_IF_NECESSARY_EVERY_S):

                self._find_new_peers()

                last_update = datetime.datetime.now()

                

    def _user_poses_query_callback(self, query, **kwargs):

        new_query_msg = message.Message(
            payload=message.QueryPayload(query))

        self.__messages[new_query_msg.message_id] = new_query_msg

        self._flood_message(new_query_msg)

    def _ip_port_pairs_initialized_peers(self):
        """ returns a list containing an (ip, port) tuple for every
        fully initialized neighbor """

        existing_peers = set()

        for p in self._peers:
            if p._dest_port:

                existing_peers.add((p.get_ip(), p._dest_port))

        return existing_peers


    def _connect_to_peers(self, ip_port_pairs):

        existing_peers = self._ip_port_pairs_initialized_peers()

        for ip, port in ip_port_pairs:

            if ip == '127.0.0.1' \
               and port == self.__server.get_port():
                continue

            if len(self._peers) >= self.MAX_PEERS:
                logging.debug(('we reached the limit of %d immediate ' +
                               'neighbors') % self.MAX_PEERS)
                break


            if (ip, int(port)) in existing_peers:
                logging.debug('skipping %s:%d because we are already connected' % (ip, port))
                continue

            try:
                new_peer = peer.Peer.connect(ip, port)
            except peer.ConnectionToPeerFailed:
                logging.info('could not connect to %s:%d' % (ip, port))
            else:
                logging.info('got a new neighbor')
                self._peers.add(new_peer)
                self.__dispatcher.register(new_peer)
                logging.info('we now got %d neighbors' % len(self._peers))

                
    def _find_new_peers(self):
        ''' construct a new pong message and send it to everybody
        we know '''

        ping_msg = message.Message(payload=message.PingPayload())

        
        assert ping_msg.message_id not in self.__messages

        self.__messages[ping_msg.message_id] = ping_msg

        self._flood_message(ping_msg)
        

    def _connection_to_peer_established_callback(self, peer, **kwargs):
        logging.debug('connection to peer established')

        if len(self._peers) <= self.MIN_PEERS:
            self._find_new_peers()


    def _new_peer_callback(self, peer, **kwargs):
        if len(self._peers) >= self.MAX_PEERS:
            logging.info('a peer is trying to connect to us, but ' +
                         'we already reached the limit of immediate ' +
                         'connections')
            peer.good_bye()

            return


        logging.debug('registering peer %s' % peer)
        self._peers.add(peer)
        self.__dispatcher.register(peer)

    
    def _peer_quits_callback(self, peer, **kwargs):
        if self.__dispatcher.is_registered(peer):
            self.__dispatcher.unregister(peer)
            self._peers.remove(peer)

    def _ping_handler(self, msg):
        if msg.message_id in self.__messages:
            logging.debug(('discarding ping with id %d because ' +
                          'we have seen it before') % msg.message_id)

            return

        msg.inc_hops()
        msg.dec_ttl()

        if msg.ttl == 0:
            logging.debug('discard ping because its TTL is now 0')
            return

        self.__messages[msg.message_id] = msg

        logging.info('flooding ping')

        self._flood_message(msg)

        my_peers = self._ip_port_pairs_initialized_peers()

        new_pong = message.Message(message_id=msg.message_id,
                                   payload=message.PongPayload(my_peers))

        logging.info('responding to a ping with a pong')

        self.__messages[msg.message_id].sender.send_message(new_pong)
        

    def _flood_message(self, msg):
        for peer in self._peers:

            if msg.sender is peer: continue

            peer.send_message(msg)


    def _pong_handler(self, msg):
        logging.info('got a pong')

        if msg.message_id not in self.__messages:
            logging.warning('received a pong, but its corresponding ' +
                            'ping has never been seen ' +
                            '(reverse-routing impossible)')
            return

        original_msg = self.__messages[msg.message_id]



        if original_msg.sent_by_us():
            # we received this pong in response to a ping from us,
            # so no reverse-routing is necessary

            logging.info('received a pong in response to a ping ' +
                         'from us')

            k = min(Master.MIN_PEERS, len(msg.payload.ip_port_pairs))

            subset_ip_port_pairs = sample(msg.payload.ip_port_pairs,
                                          k)

            self._connect_to_peers(subset_ip_port_pairs)
        else:
            # reverse-route this pong message to the peer we got it
            # from first

            logging.info('reverse-routing a pong')

            msg.inc_hops()
            msg.dec_ttl()

            # forward the message to the peer the corresponding ping
            # came from originally
            original_msg.sender.send_message(msg)
            
            
    def _query_handler(self, msg):
        if msg.message_id in self.__messages:
            logging.debug('discarding query message because its id ' +
                          'has been seen before')
            return
        

        msg.inc_hops()

        msg.dec_ttl()

        if msg.ttl == 0:
            logging.debug('discarding query because its TTL is now 0')
            return

        self.__messages[msg.message_id] = msg

        # replicate the query message to other peers
        self._flood_message(msg)

        # check whether our local index contains any relevant documents
        # for the query we received from our peer
        results = self._index.query(msg.payload.query)

        # if matching documents have been found, prepare a QueryHit
        # message
        if len(results) > 0:

            new_queryhit = message.Message(
                message_id=msg.message_id,
                payload=message.QueryHitPayload(results))

            msg.sender.send_message(new_queryhit)


    def _queryhit_handler(self, msg):
        logging.info('got a QueryHit')

        if msg.message_id not in self.__messages:
            logging.warning('we received a QueryHit message, but ' +
                            'its message ID has never been seen before')

            return

        original_query = self.__messages[msg.message_id]

        logging.debug('contents of the queryhit message')
        for doc in msg.payload.docs:
            logging.debug('TITLE: %s' % doc.title)
                      


        if original_query.sent_by_us():

            # we make the results known to the webinterface
            # so it can display them
            self._webinterface.got_results(msg.payload.docs)

        else:
            # the QueryHit message we received was sent to us
            # in response to a Query from another peer
            # so we'll reverse-route to the peer we first got it from

            logging.info('reverse-routing a QueryHit')

            original_query.sender.send_message(msg)

    def new_message_callback(self, msg, **kwargs):
        logging.info('new incoming message: %s' % msg.payload.payload_type)

        if msg.payload.payload_type is message.PayloadType.ping:
            self._ping_handler(msg)

        elif msg.payload.payload_type is message.PayloadType.pong:
            self._pong_handler(msg)

        elif msg.payload.payload_type is message.PayloadType.query:
            self._query_handler(msg)

        elif msg.payload.payload_type is message.PayloadType.queryhit:
            self._queryhit_handler(msg)

        else:
            logging.error('received an unknown message')
