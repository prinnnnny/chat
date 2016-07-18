import struct, binascii

header_len = 16

def raw_recv(sock_obj):
	header = sock_obj.recv(header_len)
	msg_type, msg_len = unpacker(header)
	return msg_type, msg_len

def recv_msg(msg_len, sock_obj):
	msg = sock_obj.recv(msg_len*2)
	return binascii.unhexlify(msg)

def raw_send(msg, msg_type, sock_obj):
	msg_to_send = packer(msg_type, msg)
	sock_obj.send(msg_to_send)

def packer(msg_type, message):
	pack = struct.Struct('>ii')
	msg_len = len(message)
	full_msg = binascii.hexlify(pack.pack(msg_type, msg_len) + message)
	return full_msg

def unpacker(data):
	pack = struct.Struct('>ii')
	packed_data = binascii.unhexlify(data)
	header = pack.unpack(packed_data)
	return header
