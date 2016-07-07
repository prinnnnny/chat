#!/usr/bin/python

import socket, select, argparse, sys, ssl, time, curses, os, traceback, threading
from client import Client

class ChatServer(object):
	def __init__(self, port):
		self.port = int(port)
		self.clients = []
		self.chat_rooms = {}

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
			self.listen_thread.setDaemon(True)
		except:
			print(traceback.format_exc())
			self.screen.addstr(10, 4, "Server failed to start!")
			self.screen.refresh()

	def listener(self):
		while True:
			read, write, err = select.select(self.inputs, [], []);
			for s in read:
				if s is self.sock:
					client, address = s.accept()
					self.screen.addstr(15, 4, "Client connected" )
					self.screen.refresh()
					self.clients.append(address)
				else:
					while True:
						pass
	
	def broadcast_message(self, chat_room):
		pass

	def list_clients(self):
		self.client_screen = curses.initscr()
		self.client_screen.keypad(1)
		self.client_screen_size = self.client_screen.getmaxyx()
		win = curses.newwin(3,self.client_screen.getmaxyx()/2, 1,1) #Box to be used to accept input when kicking a client but will remain hidden untl called with 'k' key press
		win.addstr(1,1,'Enter user to kick: ')
		x = 0
		while x != ord('q'):
			pos = 4
			#self.client_screen.clear()
			self.client_screen.addstr(2, 2, "Press q to quit or k to kick a client")
			self.client_screen.addstr(4, 2, "Connected clients:")
			for client in self.clients.values():
				self.client_screen.addstr(pos, 2, client)
				pos += 1
			x = self.client_screen.getch()
			if x == ord('q'):
				self.draw_menu()
			elif x == ord('k'):
				win.box()
				self.client_screen.refresh()
				win.refresh()
				client_to_kick = win.getstr(1, len('Enter user to kick: ')+1, 20) 
				#self.clients.remove(client_to_kick)
				if not client_to_kick in self.clients.values:
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
					#self.list_clients()
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
