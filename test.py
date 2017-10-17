import os

FIFO = 'named_pipe'

os.mkfifo(FIFO)

print('Opening FIFO...')

with open(FIFO) as fifo:
	print ('FIFO opened!')
	while True:
		data = fifo.read()
		if len(data) > 0:
			print('Read: {0}'.format(data))
			if data == 'q':
				break
			
