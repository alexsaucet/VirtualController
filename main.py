#!/usr/bin/env python

import time
import controller as Controller
import socket_server as SocketServer

def main():
	controller = Controller.Controller(name = 'Player 1')

	controller.start()

	controller.join()

	print 'Exiting'


if __name__ == "__main__":
	main()
