#!/usr/bin/python

import socket, argparse, sys, ssl, hashlib, os, curses

class ChatClient(object):
	def __init__(self, server, port, username):

		#Create master socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setblocking(0)
		self.inputs = [self.sock, sys.stdin] #Inputs to read from	

		#Create SSL wrapper for socket
		self.ssl_key = "ssl_key"
		self.ssl_cert = "ssl_cert"
		self.sock = ssl.wrap_socket(self.sock,server_side=False,certfile=self.ssl_cert,keyfile=self.ssl_key, ssl_version=ssl.PROTOCOL_TLSv1)
		
		#Grab server details from the args
		self.server = server
		self.port = port
		self.username = username

		try:
			self.sock.connect((self.server, int(self.port))) #Connect to server on specified port
			print 'Connected to %s on port %d' % (self.server, self.port)
		except socket.error as err:
			print 'Failed to connect to server'
			sys.exit(0)

	def start(self):
		self.draw_menu()

	def join_room(self):
		print 'Requesting rooms from server...'
		self.sock.send('join_room')
		while True:
			resp = self.sock.recv(1024)
			if not resp:
				break
			else:
				resp += resp
		print resp + '\n'
		
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
			
	def draw_menu(self):
		try:
			x = 0
			while x != ord('4'):
				self.screen = curses.initscr()
				self.screen.keypad(1)
				scr_size = self.screen.getmaxyx()
				self.screen.clear()
				self.screen.border(0)
				self.screen.addstr(2, 2, "Please choose an option below")
				self.screen.addstr(4, 4, "[1] Join chat room")
				self.screen.addstr(5, 4, "[2] Start new private chat")
				self.screen.addstr(6, 4, "[3] List chat rooms")
				self.screen.addstr(7, 4, "[4] List connected users")
				self.screen.addstr(8, 4, "[5] Exit")
				self.screen.refresh()
				x = self.screen.getch() #Get key press
				if x == ord('1'):
					pass
					#self.join_room()
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
					curses.endwin()
					sys.exit()
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--username', help='Specify username', action='store', dest='username', required=True)
	parser.add_argument('-s', '--server', help='Specify server IP address', action='store', dest='server', required=True)
	parser.add_argument('-p', '--port', help='Specify server port', action='store', dest='port', required=True)
	args = parser.parse_args()
	client = ChatClient(args.server, args.port, args.username)
	client.draw_menu()
