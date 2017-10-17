import socket
import sys
import select

HOST = 'localhost'
PORT = 9128

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = (HOST, PORT)
sock.bind(server_address)
sock.listen(1)

while True:
	connection, client_address = sock.accept()
	
	while True:
		try:
			read_rdy, write_rdy, in_error = select.select([connection,], [connection,], [], 5)
		except select.error:
			connection.shutdown(2)
			connection.close()
			print 'Connection error'
			break
		
		if len(read_rdy) > 0:
			recv = connection.recv(2048)
			print 'received: {0}'.format(recv)
			if recv.rstrip() == 'q':
				connection.shutdown(2)
				connection.close()
				print 'Exiting'
				exit()
		#if len(write_rdy) > 0:
		#	connection.send('I am talking')
	
print 'Finished'
