#!/usr/bin/python

import socket, select, argparse, sys, ssl, time, curses, os, traceback, threading, messages
from client import Client
from logger import Logger

class ChatServer(object):
	def __init__(self, port):
		self.port = int(port)
		self.clients = []
		self.client_dict = {}
		self.chat_rooms = {'default':[]}
		self.win_pointer = 12

		self.normal = 0
		self.join = 1
		self.user = 2
		self.password = 3
		self.direct = 4
		self.command = 5
		self.server = 6

		self.header_len = 8

		self.chat_log = 'chat_log.txt'

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
			self.inputs = [self.sock] #Inputs to read from

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
					self.inputs.append(client)
					#Create a new dict key/value pair for the socket and the hostname and room name
					self.client_dict[client] = ['Anon', 'default', None]
					#Append the socket to the room so we can later send them messages in self.broadcast
					self.chat_rooms['default'].append(client)
					self.screen.addstr(self.win_pointer, 4, "Client connected from %s" % str(address))
					self.win_pointer +=1
					self.screen.addstr(self.win_pointer, 4, "")
					self.screen.refresh()
					self.win_pointer +=1
				else:
					try:
						msg_type, msg_len = messages.raw_recv(s)
						msg = messages.recv_msg(msg_len, s)
						self.screen.addstr(self.win_pointer, 4, "Msg received")
						self.msg_handler(msg_type, msg, s)
						self.win_pointer += 1
						self.screen.refresh()
					except:
						pass

	def msg_handler(self, msg_type, msg, sock_obj):
		if msg_type == self.normal:
			print msg
			self.broadcast_msg(msg, sock_obj)
		elif msg_type == self.join:
			self.join_new_room(msg, sock_obj)
		elif msg_type == self.user:
			self.add_user(msg, sock_obj)
			self.screen.addstr(self.win_pointer, 4, "Client connected and updated with username and password")
			self.win_pointer += 1
			self.screen.refresh()
		elif msg_type == self.password:
			pass
		elif msg_type == self.direct:
			pass
		elif msg_type == self.command:
			pass
		elif msg_type == self.server:
			pass
		else:
			try:
				if hasattr(self, msg):
					getattr(self, msg)(sock_obj)
			except:
				pass

	def broadcast_msg(self, msg, sock_obj):
		room = self.client_dict[sock_obj][1] #Get room from client dict
		for client in self.chat_rooms[room]:
			if client is sock_obj: #Don't echo the same message back to the client
				pass
			else:
				messages.raw_send(msg, self.normal, client) #Broadcast the msg to every client in the room

	def add_user(self, msg, sock_obj):
		pair = msg
		username = pair.split(':')[0]
		password = pair.split(':')[1]
		self.client_dict[sock_obj][0] = str(username)
		self.client_dict[sock_obj][1] = str(password)

	def list_clients(self):
		users = []
		#try:
			#client_screen = curses.initscr()
			#client_screen.clear()
			#client_screen.keypad(1)
			#client_screen_size = client_screen.getmaxyx()
			#x = 0
			#while x != ord('q'):
			#	pos = 6
			#	client_screen.addstr(2, 2, "Press q to quit or k to kick a client")
			#	client_screen.addstr(4, 2, "Connected clients:")

				#Grab username from client dict
		for client in self.client_dict:
			users.append(self.client_dict[client][0])
		return users
					#client_screen.addstr(pos, 6, self.client_dict[client][0])
					#pos += 1
				#client_screen.refresh()

				#x = client_screen.getch()
				#if x == ord('q'):
				#	curses.endwin()
				#	self.draw_menu()
				#elif x == ord('k'):
				#	win = curses.newwin(3,client_screen_size[0]/2, 1,1) #Box to be used to accept input when kicking a client but will remain hidden untl calle    d with 'k' key press
				#	client_screen.clear()
				#	win.addstr(1,1,'Enter user to kick: ')
				#	win.box()
				#	client_screen.refresh()
				#	win.refresh()
				#	client_to_kick = win.getstr(1, len('Enter user to kick: ')+1, 20)
				#	#self.clients.remove(client_to_kick)
				#	if not client_to_kick in self.clients:
				#		win.addstr(1,1,'User does not exist!')
				#		time.sleep(1)
				#		self.list_clients()
		#except:
			#print(traceback.format_exc())
			#curses.endwin()

	def list_rooms(self, sock_obj):
		rooms = []
		for room in self.chat_rooms:
			rooms.append(room)
		return rooms

	def list_users(self, sock_obj):
		clients = []
		chat_room = self.client_dict[sock_obj][1]
		for client in chat_room:
			clients.append(client)
		return clients

	def join_new_room(self, msg, sock_obj):
		room_to_join = msg
		if room_to_join not in self.chat_rooms:
			self.chat_rooms[room_to_join] = []
			self.self.chat_rooms[room_to_join].append(sock_obj)
		else:
			self.client_dict[sock_obj][1] = room_to_join
			self.chat_rooms[room_to_join].append(sock_obj)

	def draw_menu(self):
		self.screen = curses.initscr()
		curses.noecho()
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
					self.screen.addstr(11, 4, "")
					self.screen.refresh()
				elif x == ord('2'):
					self.list_clients()
				elif x == ord('3'):
					#Place holder to draw chat rooms
					#self.list_rooms()
					pass
				elif x == ord('4'):
					curses.endwin()
		except:
			print(traceback.format_exc())
			curses.endwin()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	#Here we specify the port number we are going to be listening on
	parser.add_argument('-p', '--port', help='Specify port to listen', action='store', dest='port', required=True)
	args = parser.parse_args()
	if not args.port.isdigit() and args.port >= 1 and args.port <=65535:
		print 'Please specify a correct port number'
		sys.exit(0)
	else:
		server = ChatServer(args.port)
		server.draw_menu()
