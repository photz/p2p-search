from random import randint

import message



def test1():

    pp = message.PingPayload()

    m = message.Message(message_id=1232, ttl=3, hops=2, payload=pp)

    serialized = m.serialize()


    nbytes, deserialized = message.Message.parse(serialized)

    assert deserialized.ttl == 3
    assert deserialized.hops == 2
    assert deserialized.message_id == 1232
    assert type(deserialized.payload) is message.PingPayload
    
def test2():

    pp = message.PongPayload([('127.0.0.1', 8080), ('192.168.178.1', 64000)])

    m = message.Message(message_id=101010, ttl=13, hops=23, payload=pp)

    serialized = m.serialize()

    nbytes, deserialized = message.Message.parse(serialized)

    assert deserialized.message_id == 101010
    assert deserialized.ttl == 13
    assert deserialized.hops == 23
    assert type(deserialized.payload) is message.PongPayload

    assert len(deserialized.payload.ip_port_pairs) == 2

    assert ('127.0.0.1', 8080) in deserialized.payload.ip_port_pairs

    assert ('192.168.178.1', 64000) in deserialized.payload.ip_port_pairs

def test3():

    messages = []


    m1_payload = message.PongPayload([('122.221.1.2', 8080), ('2.1.221.22', 64000)])
    m1 = message.Message(message_id=101010,
                         ttl=13,
                         hops=23,
                         payload=m1_payload)

    
    m2_payload = message.PongPayload([('78.31.9.33', 12000)])
    m2 = message.Message(ttl=10,
                         hops=3,
                         payload=m2_payload)

    
    b = m1.serialize() + m2.serialize()

    m1_len, m1_deserialized = message.Message.parse(b)

    m2_view = memoryview(b)
    m2_view = m2_view[m1_len:]

    m2_len, m2_deserialized = message.Message.parse(m2_view)


    assert m2_deserialized.ttl == m2.ttl
    assert m2_deserialized.hops == m2.hops
    assert m2_deserialized.message_id == m2.message_id

    assert ('78.31.9.33', 12000) in m2_deserialized.payload.ip_port_pairs


def test4():

    payload = message.HelloPayload(8080)

    msg = message.Message(ttl=1, hops=0, payload=payload)

    serialized = msg.serialize() + b'anything'

    nbytes, deserialized = message.Message.parse(serialized)

    assert deserialized.ttl == 1
    assert deserialized.hops == 0
    assert deserialized.payload.dest_port == 8080

def test5():
    payload = message.HelloPayload(45000)

    msg = message.Message(ttl=3, hops=2, payload=payload)

    serialized = msg.serialize()

    # remove one byte at the end
    # to simulate an icomplete transfer of the message
    serialized = serialized[:-1]

    try:
        nbytes, deserialized = message.Message.parse(serialized)
    except message.MessageTransferIncomplete:
        # this exception is what should be triggered since we removed
        # the last byte of the serialized message
        pass
    else:
        raise Exception('Expected MessageTransferIncomplete')
    

def test6():

    assert PongPayload.binary_ip_to_str(PongPayload.str_ip_to_binary('192.168.178.1')) == '192.168.178.1'

    assert PongPayload.binary_ip_to_str(PongPayload.str_ip_to_binary('123.123.123.123')) == '123.123.123.123'

    assert PongPayload.binary_ip_to_str(PongPayload.str_ip_to_binary('localhost')) == '127.0.0.1'

    


tests = [test1, test2, test3, test4, test5]


for test in tests:

    test()
