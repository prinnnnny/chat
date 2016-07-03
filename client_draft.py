#!/usr/bin/env python

from os import system
import sys, curses, hashlib

class chatClient(object):

	def __init__(self, server, port, username):

		#Create master sock		        
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
	
	def chat_window(self):
		self.screen.clear()
		clients_win = curses.newwin(self.scr_size[0], (self.scr_size[1] / 3, 0, 0)

	def get_param(self, prompt_string):
		#self.screen.clear()
		self.screen.border(0)
		self.screen.addstr(2, 2, prompt_string)
		self.screen.refresh()
		input = self.screen.getstr(10, 10, 60)
		if input == 'q':
			self.draw_menu()
		else:
			return input

	def execute_cmd(self, cmd_string):
		system("clear")
		#Going to add in "self.sock.send" here and send the server the command

	def start_room(self):
		room_name = get_param("Enter new room name")
		password = get_param("Enter the password to be used for joining the room")
		password = hashlib.sha224(password).hexdigest()
		curses.endwin()
	
	def join_room(self):
		room_name = get_param("Enter the name of the room you wish to join")
		password = hashlib.sha224(password).hexdigest()
		curses.endwin()

	def start_chat(self):
		selected_user = get_param("Enter username of client you wish to send a message")

	def draw_menu(self):
		x = 0
		while x != ord('5'):
			self.self.screen = curses.initscr()
			self.screen.keypad(1)
			self.scr_size = screen.getmaxyx()
			self.screen.clear()
			self.screen.border(0)
			self.screen.addstr(2, 2, "Please enter a number...")
			self.screen.addstr(4, 4, "[1] - Start chat room")
			self.screen.addstr(5, 4, "[2] - Join chat room")
			self.screen.addstr(6, 4, "[3] - Start new chat")
			self.screen.addstr(7, 4, "[4] - List available chat rooms")
			self.screen.addstr(8, 4, "[5] - Exit")
			self.screen.refresh()

			x = self.screen.getch()

			if x == ord('1'):
				self.start_room()
			elif x == ord('2'):
				#curses.endwin()
				self.join_room()
			elif x == ord('3'):
				#curses.endwin()
				self.start_chat()
			elif x == ord('4'):
				self.list_rooms()
			elif x == ord('5'):
				sys.exit()

		curses.endwin()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--username', help='Specify username', action='store', dest='username', required=True)
	parser.add_argument('-s', '--server', help='Specify server IP address', action='store', dest='server', required=True)
	parser.add_argument('-p', '--port', help='Specify server port', action='store', dest='port', required=True)
	args = parser.parse_args()
	client = ChatClient(args.server, args.port, args.username)
	client.start()
