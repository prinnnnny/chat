#!/usr/bin/python

class Client(object):
	def __init__(self, username, socket):
		self.username = username
		self.socket = socket
		self.chat_room = 'default'
		self.password = None
