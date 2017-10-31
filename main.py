#!/usr/bin/env python

import time
import controller as Controller
import socket_server as SocketServer

import threading

def main():
	controller = Controller.Controller(name = 'Player 1')
	controller.open_device()

	controller.list_keys()

	controller.start_tcp_server()

	time.sleep(15)

	controller.stop_tcp_server()

	# controller.press_key('A')
	# time.sleep(2)
	# controller.release_key('A')
	# controller.press_key('X')
	# time.sleep(3)
	# controller.release_key('Y')
	# controller.release_key('X')
	#
	# time.sleep(10000)

	# controller.click_key('X')

	controller.close_device()

	threading.enumerate()



if __name__ == "__main__":
	main()
