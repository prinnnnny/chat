#!/usr/bin/python

import socket, select, argparse, sys, ssl, time, curses, os, traceback, threading
from client import Client

class ChatServer(object):
	def __init__(self, port):
		self.port = int(port)
		self.clients = []
		self.chat_rooms = {}
		self.win_pointer = 12

		#Values to be used for struct
		''' a = struct.Struct('>ii') 2 ints for type and len
			normal = a.pack('>ii', 0, msg_len)
			join = a.pack('>ii', 1)
 			user = a.pack('>ii', 2)
 			pass = a.pack('>ii', 3)
 			direct = a.pack('>ii', 4)
 			command = a.pack('>ii', 5)
 			server = a.pack('>ii', 6) '''

	def start(self, port):
		try:
			#Create master socket
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.setblocking(0)

			#Create SSL wrapper
			self.ssl_key = "../ssl_key"
			self.ssl_cert = "../ssl_cert"
			self.sock = ssl.wrap_socket(self.sock,server_side=True,certfile=self.ssl_cert,keyfile=self.ssl_key, ssl_version=ssl.PROTOCOL_TLSv1)
				
			#Bind socket and start listening
			self.sock.bind(('', self.port)) #Listen on all interfaces on port 54321
			self.sock.listen(1000)
			self.inputs = [self.sock, sys.stdin] #Inputs to read from

			self.listen_thread = threading.Thread(target=self.listener)
			self.listen_thread.daemon = True
			self.listen_thread.start()

		except:
			print(traceback.format_exc())
			self.screen.addstr(10, 4, "Server failed to start!")
			self.screen.refresh()

	def listener(self):
		while True:
			read, write, err = select.select(self.inputs, [], [])
			for s in read:
				if s is self.sock:
					client, address = s.accept()
					self.screen.refresh()
					self.clients.append(address)
					self.screen.addstr(self.win_pointer, 4, "Client connected")
					self.screen.refresh()
					self.win_pointer +=1
				else:
					self.message_parser(s)
					
	def packer(self, msg_type, message):
		#pack = struct.Struct('>ii')
		#msg_len = len(message)
		#full_msg = binascii.hexlify(pack.pack(msg_type, msg_len) + message)
		#return full_msg
		pass

	def unpacker(self, data):
		#pack = struct.Struct('>ii')
		#packed_data = binascii.unhexlify(data)
		#unpacked = pack.unpack(packed_data)
		#msg_type = unpacked[0]
		#msg_len = unpacked[1]
		pass

	def message_parser(self,socket):
		msg_type = self.unpacker(s.recv(100))	

	def broadcast_message(self, chat_room):
		pass

	def list_clients(self):
		self.screen.clear()
		client_screen = curses.initscr()
		client_screen.keypad(1)
		client_screen_size = client_screen.getmaxyx()
		x = 0
		while x != ord('q'):
			pos = 6
			client_screen.addstr(2, 2, "Press q to quit or k to kick a client")
			client_screen.addstr(4, 2, "Connected clients:")
			for client in self.clients:
				client_screen.addstr(pos, 4, str(client))
				pos += 1
			client_screen.refresh()
			x = client_screen.getch()
			if x == ord('q'):
				curses.endwin()
				self.draw_menu()
			elif x == ord('k'):
				win = curses.newwin(3,client_screen_size[0]/2, 1,1) #Box to be used to accept input when kicking a client but will remain hidden untl calle    d with 'k' key press
				client_creen.clear()
				win.addstr(1,1,'Enter user to kick: ')
				win.box()
				client_screen.refresh()
				win.refresh()
				client_to_kick = win.getstr(1, len('Enter user to kick: ')+1, 20) 
				#self.clients.remove(client_to_kick)
				if not client_to_kick in self.clients:
					win.addstr(1,1,'User does not exist!')
					time.sleep(1)
					self.list_clients()

	def list_rooms(self):
		#return [room, users for room,users in self.chat_rooms.iteritems()]
		pass

	def draw_menu(self):
		self.screen = curses.initscr()
		self.screen.keypad(1)
		scr_size = self.screen.getmaxyx()
		self.screen.clear()
		self.screen.border(0)
		self.screen.addstr(2, 2, "Please choose an option below")
		self.screen.addstr(4, 4, "[1] Start server")
		self.screen.addstr(5, 4, "[2] List connected clients")
		self.screen.addstr(6, 4, "[3] List active chat rooms")
		self.screen.addstr(7, 4, "[4] Exit")
		self.screen.refresh()
		try:
			x = 0
			while x != ord('4'):
				x = self.screen.getch() #Get key press
				if x == ord('1'):
					self.start(self.port)
					self.screen.addstr(10, 4, "Server started on port %s" % self.port)
					self.screen.refresh()
				elif x == ord('2'):
					#Place holder to draw clients
					self.list_clients()
					pass
				elif x == ord('3'):
					#Place holder to draw chat rooms
					#self.list_rooms()
					pass
				elif x == ord('4'):
					curses.endwin()
					sys.exit()
		except:
			print(traceback.format_exc())
			#curses.endwin()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--port', help='Specify port to listen', action='store', dest='port', required=True)
	args = parser.parse_args()
	if not args.port.isdigit() and args.port >= 1 and args.port <=65535:
		print 'Please specify a correct port number'
		sys.exit(0)
	else:
		server = ChatServer(args.port)
		server.draw_menu()
