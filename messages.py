import struct, binascii

#Header len is 16 as we are sending a string and not byte array
header_len = 16

#Init struct, packing
pack = struct.Struct('>ii')

def raw_recv(sock_obj):
	'''Grab first 16 chars from socket (8 bytes)'''
	header = sock_obj.recv(header_len)
	msg_type, msg_len = unpacker(header)
	return msg_type, msg_len

def recv_msg(msg_len, sock_obj):
	'''Grab the message by reading the remaining bytes off the socket'''
	msg = sock_obj.recv(msg_len*2)
	return binascii.unhexlify(msg)

def raw_send(msg, msg_type, sock_obj):
	msg_to_send = packer(msg_type, msg)
	sock_obj.send(msg_to_send)

def packer(msg_type, message):
	'''Pack two integers and append plain text message'''
	msg_len = len(message)
	full_msg = binascii.hexlify(pack.pack(msg_type, msg_len) + message)
	return full_msg

def unpacker(data):
	'''Grab message type and length and return it'''
	packed_data = binascii.unhexlify(data)
	header = pack.unpack(packed_data)
	return header
