from random import randint
import logging, xdrlib, json, string
from enum import Enum
import document

PayloadType = Enum('PayloadType', 'ping pong query queryhit hello accept')

class MessageTransferIncomplete(Exception):
    pass

class InvalidHeader(Exception):
    pass

class InvalidPayload(Exception):
    pass

class QueryHitPayload(object):

    payload_type = PayloadType.queryhit

    def __init__(self, docs):
        self.docs = docs

    @staticmethod
    def parse(payload_source):
        unpacker = xdrlib.Unpacker(payload_source)

        docs = unpacker.unpack_array(
            lambda: QueryHitPayload.__unpack_doc(unpacker))

        query_hit_payload = QueryHitPayload(docs)

        return query_hit_payload

    @staticmethod
    def __unpack_doc(unpacker):
        title = unpacker.unpack_string().decode('utf-8')
        url = unpacker.unpack_string().decode('utf-8')

        doc = document.Document()
        doc.title = title
        doc.url = url

        return doc
        

    @staticmethod
    def __pack_doc(packer, doc):
        packer.pack_string(doc.title.encode('utf-8'))
        packer.pack_string(doc.url.encode('utf-8'))

    def serialize(self):
        packer = xdrlib.Packer()

        packer.pack_array(self.docs,
                          lambda doc: \
                          QueryHitPayload.__pack_doc(
                              packer, doc))

        return packer.get_buffer()
        


class QueryPayload(object):

    payload_type = PayloadType.query

    def __init__(self, query):
        self.query = query

    @staticmethod
    def parse(payload_source):
        unpacker = xdrlib.Unpacker(payload_source)
        query = unpacker.unpack_string().decode('utf-8')
        query_payload = QueryPayload(query)
        return query_payload

    def serialize(self):
        packer = xdrlib.Packer()
        packer.pack_string(self.query.encode('utf-8'))
        return packer.get_buffer()



class AcceptPayload(object):

    payload_type = PayloadType.accept

    @staticmethod
    def parse(payload_source):
        return AcceptPayload()

    def serialize(self):
        return b""

    

class HelloPayload(object):

    payload_type = PayloadType.hello

    def __init__(self, dest_port):
        self.dest_port = dest_port

    @staticmethod
    def parse(payload_source):
        unpacker = xdrlib.Unpacker(payload_source)

        dest_port = unpacker.unpack_uint()

        unpacker.done()

        return HelloPayload(dest_port)


    def serialize(self):
        packer = xdrlib.Packer()

        packer.pack_uint(self.dest_port)

        return packer.get_buffer()




class PingPayload(object):

    payload_type = PayloadType.ping

    @staticmethod
    def parse(payload_source):
        return PingPayload()

    def serialize(self):
        return bytes()

    

class PongPayload(object):

    payload_type = PayloadType.pong

    def __init__(self, ip_port_pairs):
        self.ip_port_pairs = ip_port_pairs




    def serialize(self):
        packer = xdrlib.Packer()

        packer.pack_array(self.ip_port_pairs,
                          lambda item: \
                          self.__pack_ip_port_pair(packer, item))

        return packer.get_buffer()

    @staticmethod
    def str_ip_to_binary(str_ip):

        if str_ip == 'localhost':
            str_ip = '127.0.0.1'

        constituents = str_ip.split('.')

        if 4 != len(constituents):
            raise ValueError('%s violates format for valid IP address'
                             % str_ip)

        ip_bin = 0

        BITS_PER_BYTE = 8

        for i, value in enumerate(constituents):
            ip_bin |= int(value) << (i * BITS_PER_BYTE)

        return ip_bin

    @staticmethod
    def binary_ip_to_str(ip_bin):

        constituents = []

        BITS_PER_BYTE = 8

        for i in range(0, 4):
            constituent = ip_bin >> (i * BITS_PER_BYTE)
            constituent %= 1 << 8

            constituents.append(str(constituent))

        return '.'.join(constituents)


    @staticmethod
    def __pack_ip_port_pair(packer, item):

        if type(item[0]) is str:
            ip = PongPayload.str_ip_to_binary(item[0])
        else:
            ip = item[0]

        packer.pack_uint(ip)
        packer.pack_uint(item[1])

    @staticmethod
    def parse(payload_source):

        try:
            unpacker = xdrlib.Unpacker(payload_source)

            ip_port_pairs = unpacker.unpack_array(
                lambda: PongPayload.__unpack_ip_port_pair(unpacker))
        except xdrlib.ConversionError:
            raise InvalidPayload('cannot unpack the array of ip/port pairs')

        return PongPayload(ip_port_pairs)

    @staticmethod
    def __unpack_ip_port_pair(unpacker):

        ip = unpacker.unpack_uint()

        port = unpacker.unpack_uint()

        if port not in range(0, 1 << 16):
            raise InvalidPayload('invalid port')

        return PongPayload.binary_ip_to_str(ip), port

class Message(object):

    payload_types = {
        PayloadType.ping : PingPayload,
        PayloadType.pong : PongPayload,
        PayloadType.hello : HelloPayload,
        PayloadType.accept : AcceptPayload,
        PayloadType.query : QueryPayload,
        PayloadType.queryhit : QueryHitPayload
    }

    VALID_TTL_RANGE = range(1, 40)
    VALID_HOPS_RANGE = range(0, 40)
    VALID_PAYLOAD_LENGTH_RANGE = range(0, 100)

    DEFAULT_TTL = 2


    def __init__(self, message_id=None, ttl=None, hops=None, sender=None, payload=None):
        self.ttl = ttl or self.DEFAULT_TTL
        self.hops = hops or 0
        self.message_id = message_id or randint(0, (1 << 32) - 1)
        self.payload = payload
        self.sender = sender
        

    def serialize(self):
        packer = xdrlib.Packer()

        packer.pack_uint(self.message_id)
        packer.pack_uint(self.payload.payload_type.value)
        packer.pack_uint(self.ttl)
        packer.pack_uint(self.hops)

        serialized_payload = self.payload.serialize()

        packer.pack_uint(len(serialized_payload))

        return packer.get_buffer() + serialized_payload
        

    def dec_ttl(self):
        self.ttl -= 1

    def inc_hops(self):
        self.hops += 1

    def sent_by_us(self):
        return self.sender is None

    @staticmethod
    def parse(source, sender=None):

        # 4 bytes for the id, the payload type, the ttl,
        # the hop counter and the payload length, respectively
        UINT_BYTES = 4
        header_length = 5 * UINT_BYTES

        if len(source) < header_length:
            raise MessageTransferIncomplete()

        header_source = source[:header_length]

        p = xdrlib.Unpacker(header_source)

        message_id = p.unpack_uint()

        try:
            payload_type = PayloadType(p.unpack_uint())
        except:
            raise InvalidHeader('invalid payload type')

        ttl = p.unpack_uint()

        if ttl not in Message.VALID_TTL_RANGE:
            raise InvalidHeader('invalid ttl')

        hops = p.unpack_uint()

        if hops not in Message.VALID_HOPS_RANGE:
            raise InvalidHeader('invalid hops counter')

        payload_length = p.unpack_uint()

        if payload_length not in Message.VALID_PAYLOAD_LENGTH_RANGE:
            raise InvalidHeader('invalid paylength length')

        if len(source) < header_length + payload_length:
            raise MessageTransferIncomplete()

        payload_source = \
            source[header_length:header_length+payload_length]


        payload = Message.payload_types[payload_type].parse(payload_source)
        
        message = Message(message_id=message_id,
                          ttl=ttl,
                          hops=hops,
                          payload=payload,
                          sender=sender)

        # we return a tuple consisting of the length of the message
        # in bytes (in its serialized form) and the Message object
        # we do so because the caller may need this to know where
        # the next message begins in the stream
        return header_length + payload_length, message

        
