#!/usr/bin/env python

import socket
import sys
import select

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', 4132))
sock.listen(5)

while True:
	(client_sock, client_address) = sock.accept()
	print '{} connected'.format(client_address)

	stop = False
	while not stop:
		response = client_sock.recv(255)
		if response.rstrip() == 'q':
			print 'End connection with {}'.format(client_address)
			client_sock.close()
			break
		if response != "":
			client_sock.send(response)
			print response

print 'Finished'
