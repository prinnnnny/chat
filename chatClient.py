#!/usr/bin/python

import socket, sys, ssl, hashlib, os, curses, readline, traceback, messages, threading, select
from logger import Logger

class ChatClient(object):
	def __init__(self):
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
		self.password = 3
		self.direct = 4
		self.command = 5
		self.server = 6

		self.msg_queue = []

		self.listen_thread = threading.Thread(target=self.listener)
		self.listen_thread.daemon = True

		self.message_print_thread = threading.Thread(target=self.message_print)
		self.message_print_thread.daemon = True

		self.connection_active = False

	def listener(self):
		while True:
			read, write, err = select.select(self.inputs, [], [])
			if self.sock in read:
				msg_type, msg_len = messages.raw_recv(self.sock)
				msg = messages.recv_msg(msg_len, self.sock)
				self.msg_handler(msg_type, msg, self.sock)

	def paint_window(self):
		screen = curses.initscr()
		screen.clear()
		screen.border(1)
		scr_size = screen.getmaxyx()
		return screen, scr_size

	def start(self):
		self.draw_menu()

	def start_chat(self):
		screen, scr_size = self.paint_window()
		screen.addstr(2, 2, "You will be placed into the default chat room to begin unless you provide a room name")
		screen.addstr(4, 2, "Would you like to enter a room name? y/n")
		x = screen.getch()
		if x == ord('y'):
			self.join_room()
		elif x == ord('n'):
			self.chat_window()
			self.chat_room = 'default'
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

	def select_username(self):
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
		self.creds = self.username + ':' + self.password
		curses.echo()
		#messages.raw_send(self.username, self.user, self.sock)
		curses.endwin()

	def msg_handler(self, msg_type, msg, sock_obj):
		if msg_type == self.normal:
			self.msg_queue.append(msg)
		elif msg_type == self.join:
			pass
		elif msg_type == self.user:
			pass
		elif msg_type == self.password:
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
		self.send_msg(self.construct_msg(self.command, 'list_users'))

	def server_connect(self, ip, port):
		try:
			self.sock.connect((str(ip), int(port))) #Connect to server on specified port
		except socket.error:
			print(traceback.format_exc())

	def chat_window(self):
		username = 'test'
		try:
			#Counters used to guage where to insert new lines into boxes
			self.ctr = 2
			user_ctr = 1

			screen = curses.initscr() #Init screen
			screen.keypad(1) #Accept special keys i.e up and down arrows
			scr_size = screen.getmaxyx() #Get height and width of main screen

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

			#Input window
			self.win3.box()
			self.win3.addstr(1,1,self.username + ': ')
			self.win3.timeout(0)

			#Refresh screen with updated changes
			screen.refresh()
			self.win.refresh()
			self.win2.refresh()
			self.win3.refresh()

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
						self.win2.refresh()

				#Redraw input window
				self.win3 = curses.newwin(10, scr_size[1], scr_size[0]-(10), 0)
				self.win3.box()
				self.win3.addstr(1,1,self.username + ': ')

				#Refresh all boxes
				screen.refresh()
				self.win.refresh()
				self.win2.refresh()
				self.win3.refresh()

		except:
			print(traceback.format_exc())
			#curses.endwin()

	def message_print(self):
		while True:
			#Grab text and ship it to messages to send to server
			text = self.win3.getstr(1,len(self.username + ': ')+1,500)
			if text == '':
				pass
			#self.msg_queue.append(self.username + ': ' + text)
			messages.raw_send(text, self.normal, self.sock)
			self.win2.addstr(self.ctr,1,(self.username + ': ' + text))
			self.ctr += 1
			#self.win3 = curses.newwin(10, scr_size[1], scr_size[0]-(10), 0)
			#self.win3.box()
			#self.win3.addstr(1,1,self.username + ': ')

			self.win2.refresh()
			self.win3.refresh()

	def draw_menu(self):
		'''This draws the main menu'''

		self.screen = curses.initscr()
		#curses.noecho()
		self.screen.keypad(1)
		self.screen.border(1)
		self.scr_size = self.screen.getmaxyx()
		self.screen.clear()
		if self.connection_active == True:
			self.screen.addstr(2, 2, "Connected to server!")
		else:
			self.screen.addstr(2, 2, "No active connection!")
		self.screen.addstr(4, 2, "Welcome, %s!" % str(self.username))
		self.screen.addstr(6, 2, "Please choose an option below")
		self.screen.addstr(8, 4, "[1] Connect to server")
		self.screen.addstr(9, 4, "[2] Enter chat room")
		self.screen.addstr(10, 4, "[3] Start new private chat")
		self.screen.addstr(11, 4, "[4] List chat rooms")
		self.screen.addstr(12, 4, "[5] List connected users")
		self.screen.addstr(13, 4, "[6] Exit")
		self.screen.refresh()
		try:
			x = 0
			while x != ord('6'):
				x = self.screen.getch() #Get key press
				if x == ord('1'):
					if self.connection_active == True:
						self.screen.addstr(15, 4, "Connection already established to server!")
					else:
						self.get_server_ip()
						self.get_server_port()
						self.server_connect(self.server_ip, self.server_port)
						self.connection_active = True
						self.listen_thread.start()

						#Send server our username and hashed password in format 'username:password'
						messages.raw_send(self.creds, self.user, self.sock)

						self.screen.addstr(15, 4, "Connected to server!")
						self.draw_menu()
						self.screen.refresh()
				elif x == ord('2'):
					self.start_chat()
				elif x == ord('3'):
					#self.list_rooms()
					pass
				elif x == ord('4'):
					#self.list_users()
					pass
				elif x == ord('5'):
					#self.list_rooms()
					pass
				elif x == ord('6'):
					curses.endwin()
					sys.exit()
		except KeyboardInterrupt:
			curses.endwin()
			print(traceback.format_exc())

if __name__ == '__main__':
	client = ChatClient()
	client.select_username()
	client.draw_menu()
