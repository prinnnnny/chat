#!/usr/bin/python

import argparse, socket, sys, ssl, hashlib, os, curses, readline, traceback, messages, threading, select
from logger import Logger

class ChatClient(object):
	def __init__(self):
		self.server_ip = args.host
		self.server_port = args.port

		#Create master socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		#Create SSL wrapper for socket
		self.ssl_key = "../ssl_key"
		self.ssl_cert = "../ssl_cert"
		self.sock = ssl.wrap_socket(self.sock,server_side=False,certfile=self.ssl_cert,keyfile=self.ssl_key, ssl_version=ssl.PROTOCOL_TLSv1)

		self.inputs = [self.sock]

		#Values to be used for constructing message types
		self.normal = 0
		self.join = 1
		self.user = 2
		self.PASS = 3
		self.direct = 4
		self.command = 5
		self.server = 6

		#Init message queue, a buffer used for incoming messages from the server
		self.msg_queue = []

		#Init blank username as a placeholder
		self.username = ''

		#Init thread to be used for listening for incoming messages
		self.listen_thread = threading.Thread(target=self.listener)
		self.listen_thread.daemon = True

		#Init thread for getting chat input
		self.message_print_thread = threading.Thread(target=self.message_print)
		self.message_print_thread.daemon = True

		#Initally set the auth flag to false, only set to True when we get an ACK from server upon login
		self.auth = False

		self.connection_active = False

	def listener(self):
		'''This is the main methid that listens for incoming server responses and passes the messages to the message handler'''

		while True:
			#Read off every socket in the inputs list
			read, write, err = select.select(self.inputs, [], [])
			if self.sock in read:
				#Grab message type and length
				msg_type, msg_len = messages.raw_recv(self.sock)
				msg = messages.recv_msg(msg_len, self.sock)
				#Pass everything off to message handler
				self.msg_handler(msg_type, msg, self.sock)

	def paint_window(self):
		'''This creates a new screen which we can write on'''
		screen = curses.initscr()
		screen.clear()
		screen.border(1)
		scr_size = screen.getmaxyx()
		return screen, scr_size

	def start(self):
		'''Draws the main menu'''
		self.draw_menu()

	def start_chat(self):
		'''We ask a client here if they want to specify a new room or stay a member of the default room'''
		screen, scr_size = self.paint_window()
		screen.addstr(2, 2, "You will be placed into the default chat room to begin unless you provide a room name")
		screen.addstr(4, 2, "Would you like to enter a room name? y/n")
		x = screen.getch()
		if x == ord('y'):
			self.join_room()
		elif x == ord('n'):
			self.chat_room = 'default'
			self.chat_window()
		else:
			self.start_chat()

	def join_room(self):
		screen, scr_size = self.paint_window()
		screen.addstr(2, 2, "Please enter name of chat you wish to join:")
		tbox = curses.newwin(3,scr_size[1]-4, 4,4)
		tbox.box()
		tbox.addstr(1,1, 'Room name: ')
		screen.refresh()
		tbox.refresh()
		room_name = tbox.getstr(1, len('Room name: ')+1, 20)
		self.chat_room = room_name
		messages.raw_send(room_name, self.join, self.sock)
		curses.endwin()
		self.chat_window()

	def register(self):
		username, password = self.login_screen()
		self.send_user_pass(username, password)

	def login_screen(self):
		'''Grab the username and password from input and send it to the server for auth or registration'''
		screen = curses.initscr()
		scr_size = screen.getmaxyx()
		screen.clear()
		screen.addstr(2, 2, "Please enter a username below (Max len 10 chars)")
		tbox = curses.newwin(3,scr_size[1]-4, 4,4)
		tbox.box()
		tbox.addstr(1,1, 'Username: ')
		screen.refresh()
		tbox.refresh()
		self.username = tbox.getstr(1, len('Username: ')+1, 20)
		print self.username
		tbox.clear()
		screen.clear()

		screen.addstr(2, 2, "Please enter a password below (Max len 15 chars)")
		tbox.addstr(1,1, 'Password: ')
		tbox.box()
		screen.refresh()
		tbox.refresh()
		curses.noecho()

		self.password = tbox.getstr(1, len('Password: ')+1, 20)
		self.password = hashlib.sha224(self.password).hexdigest()

		return self.username, self.password

		curses.echo()

	def send_user_pass(self, username, password):
		messages.raw_send(self.username, self.user, self.sock)
		msg_type, msg_len = messages.raw_recv(self.sock)
		response = messages.recv_msg(msg_len, self.sock)
		#Get 1st response which should be an ACK regardless of username
		if response == 'ACK':
			messages.raw_send(self.password, self.PASS, self.sock)
			msg_type, msg_len = messages.raw_recv(self.sock)
			response = messages.recv_msg(msg_len, self.sock)
			#If we get a second ACK, the user is considred legit and authd on client and server
			if response == 'ACK':
				self.auth = True
			else:
				self.auth = False
		#If user is not valid, we register a new user
		if response == 'REGISTERED':
			self.screen.addstr(16, 4, "REGISTERED - Please login")

	def msg_handler(self, msg_type, msg, sock_obj):
		'''Grabs message type from incoming message on the socket and we handle it here'''
		if msg_type == self.normal:
			self.msg_queue.append(msg)
		elif msg_type == self.join:
			pass
		elif msg_type == self.user:
			pass
		elif msg_type == self.PASS:
			pass
		elif msg_type == self.direct:
			pass
		elif msg_type == self.command:
			pass
		elif msg_type == self.server:
			pass
		else:
			pass

	def get_server_ip(self):
		'''Draw a box to get the server IP to connect to'''
		try:
			screen = curses.initscr()
			scr_size = screen.getmaxyx()
			screen.clear()

			#Get server IP info from input
			screen.addstr(2, 2, "Please enter server IP")
			tbox = curses.newwin(3,scr_size[1]-4, 4,4)
			tbox.box()
			tbox.addstr(1,1, 'Server IP: ')
			screen.refresh()
			tbox.refresh()
			self.server_ip = tbox.getstr(1, len('Server IP: ')+1, 20)
		except:
			curses.endwin()

	def get_server_port(self):
		'''Draw a box to get the port number to use'''
		try:
			screen = curses.initscr()
			scr_size = screen.getmaxyx()
			screen.clear()

			#Get server port info from input
			screen.addstr(2, 2, "Please enter port to connect")
			tbox = curses.newwin(3,scr_size[1]-4, 4,4)
			tbox.box()
			tbox.addstr(1,1, 'Port: ')
			screen.refresh()
			tbox.refresh()
			self.server_port = tbox.getstr(1, len('Port: ')+1, 5)
			curses.endwin()
		except:
			curses.endwin()

	def get_active_users(self):
		'''This will be used to grab a list of active clients on the server'''
		messages.raw_send('list_users', self.server, self.sock)
		msg_type, msg_len = messages.raw_recv(self.sock)
		response = messages.recv_msg(msg_len, self.sock)
		print response

	def server_connect(self, ip, port):
		''''Connect to server using specified IP and port'''
		try:
			#Connect to server on specified port
			self.sock.connect((str(ip), int(port)))
		except socket.error:
			print(traceback.format_exc())

	def chat_window(self):
		'''This is the main chat window. It takes text input and sends it to the server without ever knowing which chat room
		we are actually a member of, that is all handled server side so this can handle any chat room/private chat'''
		username = 'test'
		try:
			#Counters used to guage where to insert new lines into boxes
			self.ctr = 2
			user_ctr = 1

			screen = curses.initscr() #Init screen
			screen.keypad(1) #Accept special keys i.e up and down arrows
			scr_size = screen.getmaxyx() #Get height and width of main screen

			#Initthe boxes we are going to be writing to
			self.win = curses.newwin(scr_size[0]-10, scr_size[1]/5, 0, 0)
			self.win2 = curses.newwin(scr_size[0]-10, 10000 - scr_size[1]/5, 0, scr_size[1]/5)
			self.win3 = curses.newwin(10, scr_size[1], scr_size[0]-(10), 0)

			#User box
			self.win.box()
			self.win.addstr(user_ctr,1,'Users', curses.A_BOLD)
			user_ctr += 1
			self.win.addstr(user_ctr,1,username)

			#Main chat window
			self.win2.box()
			self.win2.addstr(1,1,'Room: ', curses.A_BOLD)
			screen.scrollok(1)
			screen.idlok(1)

			#Input window
			self.win3.box()
			self.win3.addstr(1,1,self.username + ': ')
			self.win3.timeout(0)

			#Refresh screen with updated changes
			screen.refresh()
			self.win.refresh()
			self.win2.refresh()
			self.win3.refresh()

			#Start the thread to grab user input and write it to screen
			self.message_print_thread.start()

			while True:
			#	#Grab text and ship it to messages to send to server
			#	text = self.win3.getstr(1,len(self.username + ': ')+1,500)
			#	self.msg_queue.append(self.username + ': ' + text)
			#	if text == '':
			#		pass
			#	else:
			#		messages.raw_send(text, self.normal, self.sock)

				#Update chat window with new message from local user
				#self.win2.addstr(self.ctr,1,(self.username + ': ' + text))
				#elf.ctr += 1

				#Check for any new messages received on socket
				if len(self.msg_queue) > 0:
					for msg in self.msg_queue:
						self.win2.addstr(self.ctr,1,str(msg))
						self.ctr += 1
						self.msg_queue.remove(msg)

				#Redraw input window
				self.win3 = curses.newwin(10, scr_size[1], scr_size[0]-(10), 0)
				self.win3.box()
				self.win3.addstr(1,1,self.username + ': ')

				#Refresh all boxes
				screen.refresh()
				self.win.refresh()
				self.win2.refresh()
				self.win3.refresh()

		except curses.error:
			print(traceback.format_exc())
			#curses.endwin()

	def message_print(self):
		while True:
			#Grab text and ship it to messages to send to server
			text = self.win3.getstr(1,len(self.username + ': ')+1,500)
			if text == '':
				pass
			messages.raw_send(text, self.normal, self.sock)
			self.win2.addstr(self.ctr,1,(self.username + ': ' + text))
			self.ctr += 1
			#self.win3 = curses.newwin(10, scr_size[1], scr_size[0]-(10), 0)
			#self.win3.box()
			#self.win3.addstr(1,1,self.username + ': ')

			#self.win2.refresh()
			#self.win3.refresh()

	def draw_menu(self):
		'''This draws the main menu and takes key presses as input'''

		self.screen = curses.initscr()
		#Don't echo key press to screen
		self.screen.keypad(1)
		self.screen.border(1)
		self.scr_size = self.screen.getmaxyx()
		self.screen.clear()
		#Check we haven't already authenticate to server
		if self.connection_active == True:
			self.screen.addstr(2, 2, "Connected to server!")
		else:
			self.screen.addstr(2, 2, "Not connected to server!")
		if self.auth == True:
			self.screen.addstr(4, 2, "Logged in!")
		else:
			self.screen.addstr(4, 2, "Not logged in!")

		#Draw the options onto the screen
		self.screen.addstr(6, 2, "Welcome, %s!" % str(self.username))
		self.screen.addstr(8, 2, "Please choose an option below")
		self.screen.addstr(9, 4, "[1] Login to server")
		self.screen.addstr(10, 4, "[2] Register new user")
		self.screen.addstr(11, 4, "[3] Enter chat room")
		self.screen.addstr(12, 4, "[4] Start new private chat")
		self.screen.addstr(13, 4, "[5] List chat rooms")
		self.screen.addstr(14, 4, "[6] List connected users")
		self.screen.addstr(15, 4, "[7] Exit")
		self.screen.refresh()
		try:
			x = 0
			while x != ord('7'):
				#Get key press
				x = self.screen.getch()
				if x == ord('1'):
					#if self.connection_active == True:
					#	self.screen.addstr(15, 4, "Connection already established to server!")
					if self.auth == True:
						self.screen.addstr(15, 4, "Connection already established to server!")
					else:
						#If we have specified cmd line args, use these
						if args.host and args.port:
							self.server_ip = args.host
							self.server_port = args.port
						else:
							#If not, draw boxes to get user input
							self.get_server_ip()
							self.get_server_port()

						#Connect to server
						self.server_connect(self.server_ip, self.server_port)
						#Draw the login screen and garb username and password
						self.login_screen()
						#Send user/pass to server for validation
						self.send_user_pass(self.username, self.password)
						self.connection_active = True
						#Start the listening thread
						self.listen_thread.start()

						self.screen.addstr(15, 4, "Connected to server!")
						self.draw_menu()
						self.screen.refresh()

				elif x == ord('2'):
					if self.auth == True:
						self.screen.addstr(15, 4, "Connection already established to server!")
					else:
						self.server_connect(self.server_ip, self.server_port)
						self.register()
						self.draw_menu()
				elif x == ord('3'):
					self.start_chat()
				elif x == ord('4'):
					#self.list_rooms()
					pass
				elif x == ord('5'):
					#self.list_rooms()
					pass
				elif x == ord('6'):
					self.get_active_users()
					pass
				elif x == ord('7'):
					curses.endwin()
					sys.exit()
		except KeyboardInterrupt:
			curses.endwin()
			print(traceback.format_exc())

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	#Here we can specify the IP and port we can use to connect to the server on these are not mandatory
	parser.add_argument('-p', '--port', help='Specify port to connect', action='store', dest='port', required=False)
	parser.add_argument('-t', '--host', help='Specify host IP', action='store', dest='host', required=False)
	args = parser.parse_args()
	try:
		#Validate the IP is valid
		socket.inet_aton(args.host)
	except socket.error:
		print 'Please enter a valid IP address'
		sys.exit(0)
	client = ChatClient()
	client.draw_menu()
