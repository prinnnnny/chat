import struct, binascii

header_len = 8

#Values to be used for constructing message types with struct
normal = 0 
join = 1
user = 2
password = 3
direct = 4
command = 5
server = 6 

def raw_recv(sock_obj):
	header = sock_obj.recv(header_len)
	msg_type = header[0:4]
	msg_len = header[4::]
	message = sock_obj.recv(msg_len)

def packer(msg_type, message):
	pack = struct.Struct('>ii')
	msg_len = len(message)
	full_msg = binascii.hexlify(pack.pack(msg_type, msg_len) + message)
	return full_msg

def unpacker(data):
	pack = struct.Struct('>ii')
	packed_data = binascii.unhexlify(data)
	header = pack.unpack(packed_data[0:8])
	msg_type = header[0]
	msg_len = header[1]
	msg = packed_data[8:8+msg_len]
	return (msg_type, msg)
