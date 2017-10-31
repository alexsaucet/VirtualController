#!/usr/bin/env python

import socket
import select
import sys
from threading import Thread

import logger as Logger
import message as Message

class SocketServer(Thread):
    """ Simple socket server. Data must be in JSON format. """

    def __init__(self, cb_read = None, host = '0.0.0.0', port = 2010, max_clients = 3):
        """ Initialize the server with a host and port to listen to.
        Provide a list of functions that will be used when receiving specific data """
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.sock.bind((host, port))
        self.sock.listen(max_clients)
        self.cb_read = cb_read
        self.sock_threads = []

    def close(self):
        """ Close the socket threads and server socket if they exists. """
        Logger.info('Closing server socket (host {}, port {})'.format(self.host, self.port))

        for thr in self.sock_threads:
            thr.stop()
            thr.join()

        if self.sock:
            self.sock.close()
            self.sock = None

    def run(self):
        """ Accept an incoming connection.
        Start a new SocketServerThread that will handle the communication. """
        Logger.info('Starting socket server (host {}, port {})'.format(self.host, self.port))

        self.__stop = False
        while not self.__stop:
            self.sock.settimeout(1)
            try:
                client_sock, client_addr = self.sock.accept()
            except socket.timeout:
                client_sock = None
                print 'Timeout waiting for accept(), this is normal'

            if client_sock:
                print 'timeout on client_sock is: {}'.format(client_sock.gettimeout())
                client_thr = SocketServerThread(client_sock, client_addr, self.cb_read)
                self.sock_threads.append(client_thr)
                client_thr.start()

    def stop(self):
        self.__stop = True

class SocketServerThread(Thread):
    def __init__(self, client_sock, client_addr, cb_read = None):
        """ Initialize the Thread with a client socket and address """
        Thread.__init__(self)
        self.client_sock = client_sock
        self.client_addr = client_addr
        self.cb_read = cb_read

    def run(self):
        Logger.info("SocketServerThread starting with client {}".format(self.client_addr))
        self.__stop = False
        while not self.__stop:
            if self.client_sock:
                # Check if the client is still connected and if data is available:
                try:
                    rdy_read, rdy_write, sock_err = select.select([self.client_sock,], [self.client_sock,], [], 5)
                except select.error as err:
                    Logger.warning('Select() failed on socket with {}'.format(self.client_addr), err)
                    self.stop()
                    return

                if len(rdy_read) > 0:
                    read_data = self.client_sock.recv(255)

                    # Check if socket has been closed
                    if len(read_data) == 0:
                        Logger.info('{} closed the socket.'.format(self.client_addr))
                        self.stop()
                    else:
                        msg = Message.Message()
                        msg.read_message(read_data)
                        if  msg.is_valid():
                            Logger.info("Message from {}:".format(self.client_addr))
                            msg.print_out()
                            if msg.is_stop():
                                Logger.info("This message is STOP from {}".format(self.client_addr))
                                #self.stop()
                            elif msg.is_error():
                                Logger.info("This message is ERROR from {}".format(self.client_addr))
                            else:
                                Logger.info("This message is OK from {}".format(self.client_addr))
                            self.cb_read(msg)
                        else:
                            Logger.warning("Received an invalid message from {}: {}".format(self.client_addr, read_data))
            else:
                Logger.warning("No client is connected, SocketServer can't receive data")
                self.stop()

        self.close()

    def stop(self):
        self.__stop = True

    def close(self):
        """ Close connection with the client socket. """
        if self.client_sock:
            Logger.info("Closing connection with {}".format(self.client_addr))
            self.client_sock.close()
