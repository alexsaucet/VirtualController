#!/usr/bin/env python

import time

import controller
import socket_server

def main():
    try:
        ctrl = controller.Controller(name = 'Player 1')
        ctrl.start()
        while True: ctrl.join(5)
    except KeyboardInterrupt:
        print 'Received keyboard interrupt, terminating VirtualController...'
        ctrl.stop()

    ctrl.join()

    print 'Done'

if __name__ == "__main__":
    main()
