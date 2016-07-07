#!/usr/bin/python

import socket, argparse, sys, ssl, hashlib, os, curses, readline, traceback

class ChatClient(object):
	def __init__(self):
		#Create master socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.inputs = [self.sock, sys.stdin] #Inputs to read from	

		#Create SSL wrapper for socket
		self.ssl_key = "../ssl_key"
		self.ssl_cert = "../ssl_cert"
		self.sock = ssl.wrap_socket(self.sock,server_side=False,certfile=self.ssl_cert,keyfile=self.ssl_key, ssl_version=ssl.PROTOCOL_TLSv1)

	def start(self):
		self.draw_menu()

	def join_room(self):
		pass

	def start_room(self):
		print 'Create a new chat room'
		room_name = raw_input('Please enter room name: ')
		choice = raw_input('Do you want to protect the room with a password? y/n: ')
		if choice.lower() == 'y':
			password = raw_input('Please enter a password: ')
			pass_hash = hashlib.sha224(password).hexdigest() #Create secure password for chat room
			self.sock.send()
		else:
			self.sock.send() #place holder for room name and password

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
		username = tbox.getstr(1, len('Username: ')+1, 20)
		return username

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
			return
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
			return
		except:
			curses.endwin()

	def server_connect(self, ip, port):
		try:
			self.sock.connect((str(ip), int(port))) #Connect to server on specified port
			self.screen.addstr(15, 4, "Connected to server!")
			self.screen.refresh()
		except socket.error:
			curses.endwin()
			print(traceback.format_exc())
			sys.exit(0)

	def draw_menu(self):
		'''This draws the main menu'''

		self.screen = curses.initscr()
		self.screen.keypad(1)
		self.scr_size = self.screen.getmaxyx()
		self.screen.clear()
		self.screen.border(0)
		self.screen.addstr(2, 2, "Please choose an option below")
		self.screen.addstr(4, 4, "[1] Connect to server")
		self.screen.addstr(5, 4, "[2] Join chat room")
		self.screen.addstr(6, 4, "[3] Start new private chat")
		self.screen.addstr(7, 4, "[4] List chat rooms")
		self.screen.addstr(8, 4, "[5] List connected users")
		self.screen.addstr(9, 4, "[6] Enter username")
		self.screen.addstr(10, 4, "[7] Exit")
		self.screen.refresh()
		try:
			x = 0
			while x != ord('7'):
				x = self.screen.getch() #Get key press
				if x == ord('1'):
					self.get_server_ip()
					self.get_server_port()
					self.server_connect(self.server_ip, self.server_port)
				elif x == ord('2'):
					#self.start_chat()
					pass
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
					self.username = self.select_username()
				elif x == ord('7'):
					curses.endwin()
					sys.exit()
		except:
			#curses.endwin()
			print(traceback.format_exc())

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--username', help='Specify username', action='store', dest='username', required=False)
	parser.add_argument('-s', '--server', help='Specify server IP address', action='store', dest='server', required=False)
	parser.add_argument('-p', '--port', help='Specify server port', action='store', dest='port', required=False)
	args = parser.parse_args()
	client = ChatClient()
	client.draw_menu()
