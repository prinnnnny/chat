#!/usr/bin/python

import socket, select, argparse, sys, ssl, time, curses, os, traceback, threading, messages, time
from client import Client
from logger import Logger

class ChatServer(object):
	def __init__(self, port):
		#Grab port from args
		self.port = int(port)

		#Init client and chat room dicts
		self.clients = []
		self.client_dict = {}
		self.chat_rooms = {'default':[]}

		#Set the pointer when drawing to screen
		self.win_pointer = 12

		#Message types to be used
		self.normal = 0
		self.join = 1
		self.user = 2
		self.PASS = 3
		self.direct = 4
		self.command = 5
		self.server = 6

		self.chat_log = 'chat_log.txt'

		#Initially set this to false as server has yet to be started
		self.started = False

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

			#Set up thread for the main listener
			self.listen_thread = threading.Thread(target=self.listener)
			self.listen_thread.daemon = True
			self.listen_thread.start()

			self.started = True

		except:
			print(traceback.format_exc())
			self.screen.addstr(10, 4, "Server failed to start!")
			self.screen.refresh()

	def listener(self):
		#Create new logger object
		logger = Logger()
		while True:
			#Loop through each socket, either the main server socket or client sockets
			read, write, err = select.select(self.inputs, [], [])
			for s in read:
				if s is self.sock:
					#Accept new client
					client, address = s.accept()

					self.clients.append(address)
					self.inputs.append(client)

					#Log connection request
					logger.log_client_connection(address[0], address[1])

					#Create a new dict entry for client socket, username, chat room, password, ip, port and auth status
					self.client_dict[client] = [None, 'default', None, address[0], address[1], False]

					#Append the socket to the room so we can later send them messages in self.broadcast
					self.chat_rooms['default'].append(client)
					self.screen.addstr(self.win_pointer, 4, "Client connected from %s" % str(address))

					#Update screen
					self.win_pointer +=1
					self.screen.addstr(self.win_pointer, 4, "")
					self.screen.refresh()
					self.win_pointer +=1
				else:
					try:
						#Get message type and length
						msg_type, msg_len = messages.raw_recv(s)

						#Get message
						msg = messages.recv_msg(msg_len, s)

						self.screen.addstr(self.win_pointer, 4, "Msg received from %s" % self.client_dict[s][0])

						#Pass the message to the main handler function
						self.msg_handler(msg_type, msg, s)

						self.win_pointer += 1
						self.screen.refresh()

						#Logs type, ip, port, message and time stamp of received message
						logger.log_server_message(msg_type, self.client_dict[s][0], self.client_dict[s][3], self.client_dict[s][4], msg)
					except:
						pass

	def msg_handler(self, msg_type, msg, sock_obj):
		'''Main message handler. Takes a message type and passes the message and the socket object
		to the correct function to handle that message type'''

		if msg_type == self.normal:
			#Prepend username to message and broadcast it out to all clients in chat room
			msg = str(self.client_dict[sock_obj][0]) + ': ' + msg
			self.broadcast_msg(msg, sock_obj)

		elif msg_type == self.join:
			self.join_new_room(msg, sock_obj)

		elif msg_type == self.user:
			username = msg
			self.client_dict[sock_obj][0] = username
			print username
			messages.raw_send('ACK', self.user, sock_obj)
			msg_type, msg_len = messages.raw_recv(sock_obj)
			password = messages.recv_msg(msg_len, sock_obj)
			print password
			with open('passwords.txt', 'r') as pass_file:
				user_exists = False
				for line in pass_file.readlines():
					if username == line.split(':')[0]:
						user_exists = True
						if password == line.split(':')[1].strip():
							messages.raw_send('ACK', self.user, sock_obj)
							self.client_dict[sock_obj][5] = True
							print 'ACK'
							break
						else:
							messages.raw_send('FAIL', self.user, sock_obj)
							print 'Fail'
							break
				if user_exists == False:
					self.add_user(username, password, sock_obj)
					messages.raw_send('REGISTERED', self.user, sock_obj)
					print 'REGISTERED'

		elif msg_type == self.PASS:
			pass

		elif msg_type == self.direct:
			pass

		elif msg_type == self.server:
			if msg == 'list_clients':
				list_users(sock_obj)

	def broadcast_msg(self, msg, sock_obj):
		'''Takes a message and sends it to every client that is a member of the same chat room'''
		room = self.client_dict[sock_obj][1] #Get room from client dict
		for client in self.chat_rooms[str(room)]:
			if client is sock_obj: #Don't echo the same message back to the client
				pass
			else:
				messages.raw_send(msg, self.normal, client) #Broadcast the msg to every client in the room

	def add_user(self, username, password, sock_obj):
		self.client_dict[sock_obj][0] = str(username)
		self.client_dict[sock_obj][2] = str(password)
		with open('passwords.txt', 'a') as pass_file:
			#Append username and password to text file for reading when authing
			pass_file.write(str(username) + ':' + str(password) + '\n')

	def display_clients(self):
		'''Displays all active clients on the server side'''
		users = []
		try:
			client_screen = curses.initscr()
			client_screen.clear()
			client_screen.keypad(1)
			client_screen_size = client_screen.getmaxyx()
			x = 0
			while x != ord('q'):
				pos = 6
				client_screen.addstr(2, 2, "Press q to quit or k to kick a client")
				client_screen.addstr(4, 2, "Connected clients:")

				#Grab username from client dict
				for client in self.client_dict:
					users.append(self.client_dict[client][0])
					#return users
					client_screen.addstr(pos, 6, self.client_dict[client][0])
					pos += 1
				client_screen.refresh()

				x = client_screen.getch()
				if x == ord('q'):
					curses.endwin()
					self.draw_menu()
				elif x == ord('k'):
					win = curses.newwin(3,client_screen_size[0]/2, 1,1) #Box to be used to accept input when kicking a client but will remain hidden untl calle    d with 'k' key press
					client_screen.clear()
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
		except:
			print(traceback.format_exc())
			curses.endwin()

	def display_chat_rooms(self):
		'''Displays all the chat rooms that are active'''
		rooms = []
		try:
			screen = curses.initscr()
			screen.clear()
			screen.keypad(1)
			screen_size = screen.getmaxyx()
			x = 0
			while x != ord('q'):
				pos = 6
				screen.addstr(2, 2, "Rooms:")

				for room in self.chat_rooms:
					screen.addstr(pos, 6, room)
					pos += 1
				screen.refresh()

				x = screen.getch()
				if x == ord('q'):
					curses.endwin()
					self.draw_menu()
		except:
			print(traceback.format_exc())
			curses.endwin()

	def list_rooms(self, sock_obj):
		'''Returns a list of rooms to the client'''
		rooms = []
		for room in self.chat_rooms:
			rooms.append(room)
		messages.raw_send(rooms, self.command, sock_obj)

	def list_users(self, sock_obj):
		'''Returns a list of users to the client'''
		clients = []
		chat_room = self.client_dict[sock_obj][1]
		for client in chat_room:
			clients.append(client)
		messages.raw_send(clients, self.command, sock_obj)

	def join_new_room(self, msg, sock_obj):
		'''Takes a room name and either creates a room based on the name or
		adds the client to the existing room'''
		room_to_join = msg
		if room_to_join not in self.chat_rooms:
			#Create new key in chat rooms and append client socket to list
			self.chat_rooms[room_to_join] = []
			self.self.chat_rooms[room_to_join].append(sock_obj)
		else:
			self.client_dict[sock_obj][1] = room_to_join
			self.chat_rooms[room_to_join].append(sock_obj)

	def draw_menu(self):
		'''This draws the main menu and wiats for key presses, same as the client side'''
		self.screen = curses.initscr()
		curses.noecho() #Remove echoing of the password to screen
		self.screen.keypad(1)
		scr_size = self.screen.getmaxyx()
		self.screen.clear()
		self.screen.border(0)
		if self.started:
			self.screen.addstr(2, 2, "Server started!")
		else:
			self.screen.addstr(2, 2, "Server not started!")
		self.screen.addstr(4, 2, "Please choose an option below")
		self.screen.addstr(5, 4, "[1] Start server")
		self.screen.addstr(6, 4, "[2] List connected clients")
		self.screen.addstr(7, 4, "[3] List active chat rooms")
		self.screen.addstr(8, 4, "[4] Exit")
		self.screen.refresh()
		try:
			x = 0
			while x != ord('4'):
				#Get key press
				x = self.screen.getch()
				if x == ord('1'):
					self.start(self.port)
					self.draw_menu()
				elif x == ord('2'):
					self.display_clients()
				elif x == ord('3'):
					self.display_chat_rooms()
					pass
				elif x == ord('4'):
					curses.endwin()
		except KeyboardInterrupt:
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
