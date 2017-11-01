#!/usr/bin/env python

import time
import controller as Controller
import socket_server as SocketServer

import threading

def main():
	controller = Controller.Controller(name = 'Player 1')

	controller.start()

	controller.list_keys()

	time.sleep(15)

	if controller.is_active:
		controller.stop()
	else:
		print 'Controller is not active, not closing it.'


if __name__ == "__main__":
	main()
