#!/usr/bin/env python

"""
Virtual controller based on python-uinput
(https://github.com/tuomasjjrasanen/python-uinput)
A TCP Client can send input keyboard events, causing this Controller to emit
the events on the uinput driver.
Input messages must be in the JSON format specified in message.py; other messages
will be ignored.
"""

import sys
import time
import fcntl

import logger
import bus_types
import socket_server
import message

try:
    import uinput
except ImportError as err:
    logger.fatal('Failed to import uinput. Are you sure it is installed?', err)

logger.success('Imported module uinput.')

class Controller:
    """ This class handles the uinput device """
    def __init__(
        self,
        name = 'Controller',
        device_name = 'virtual_controller',
        device_bus_type = bus_types.BusTypes.VIRTUAL,
        device_version = 1,
        keys = None,
    ):
        """ Set the uinput device settings, and define the list of keys the controller will support """
        self.name = name
        self.device = None
        self.device_name = device_name
        self.device_bus_type = device_bus_type
        self.device_version = device_version
        if keys is None:
            self.keys = Keys.KEYS_JOYSTICK
        else:
            self.keys = keys
        self.server_sock = socket_server.SocketServer(cb_read = self.on_client_event)

    def start(self):
        """ Start the Controller. Start the TCP socket server and open the uinput device. """
        logger.info('Starting Controller {}.'.format(self.name))
        self.open_device()
        self.start_tcp_server()
        self.is_active = True

    def stop(self):
        """ Stop the Controller. Closes the TCP socket server, and closes the uinput device. """
        logger.info('Stopping Controller {}...'.format(self.name))
        self.stop_tcp_server()
        self.close_device()
        self.is_active = False

    def start_tcp_server(self):
        """ Start the SocketServer thread. """
        self.server_sock.start()

    def stop_tcp_server(self):
        """ Stop the SocketServer thread. """
        self.server_sock.stop()
        self.server_sock.close()
        self.server_sock.join()

    def open_device(self):
        """ Open the uinput device for this Controller
        This will exit the program if it fails """
        try:
            self.device = uinput.Device(
                events = self.keys.values(),
                name = self.device_name,
                bustype	= self.device_bus_type,
                vendor = 0,
                product	= 0,
                version = self.device_version,
            )
        except Exception as err:
            Logger.fatal('Failed to open a uinput device. Have you loaded the module (sudo modprobe uinput)? Are you running this script as root?', err)
        logger.success('Opened uinput device for controller ' + self.name)

    def close_device(self):
        """ Close the uinput device for this Controller. """
        try:
            self.device.destroy()
        except Exception as err:
            logger.fatal('Failed to destroy a uinput device.', err)
        logger.success('Destroyed uinput device for controller ' + self.name)

    def list_keys(self):
        """ Print a list of keys supported by this controller. """
        print 'Controller ' + self.name + ' supports the following keys:'
        print self.keys.keys()

    def has_key(self, key):
        """ Check if this Controller has a given key. """
        return key in self.keys

    def click_key(self, key):
        """ Emit a click for a key. The key must be defined in Controller.keys. """
        if not self.has_key(key):
            logger.warning('Key {0} is not supported by this Controller.'.format(key))
        else:
            self.device.emit_click(self.keys[key])
            logger.log('Sending uinput event: click key {} ({}).'.format(key, sekf.keys[key]))

    def press_key(self, key):
        """ Press down on a key. The key must be defined in Controller.keys. """
        if not self.has_key(key):
            #Logger.warning('Key {0} is not supported by this Controller.'.format(key))
            raise ValueError('Key {0} is not supported by this Controller.'.format(key))
        else:
            self.device.emit(self.keys[key], 1)
            logger.log('Sending uinput event: press key {} ({}).'.format(key, self.keys[key]))

    def release_key(self, key):
        """ Release a key. The key must be defined in Controller.keys. """
        if not self.has_key(key):
            #Logger.warning('Key {0} is not supported by this Controller.'.format(key))
            raise ValueError('Key {0} is not supported by this Controller.'.format(key))
        else:
            self.device.emit(self.keys[key], 0)
            logger.log('Sending uinput event: release key {} ({}).'.format(key, self.keys[key]))

    def on_client_event(self, msg):
        """ Callback function called by the SocketServer when it receives a valid
        Message. Will trigger the uinput event if the Message is supported by this
        Cotroller. """
        logger.info('Controller received message: {}'.format(msg.format_json()))
        if msg.is_valid():
            if msg.is_ok():
                if msg.title == message.Titles.EVENT:
                    in_key = msg.value

                    # if in_key == Keys.KEY_STOP_CONTROLLER:
                    #     logger.info('Received STOP key! Exiting.')
                    #     self.stop()
                    #     logger.info('Done stopping controller')
                    #     return

                    if msg.action == message.Actions.PRESSED:
                        try:
                            self.press_key(in_key)
                        except ValueError as e:
                            logger.warning(str(e))
                    elif msg.action == message.Actions.RELEASED:
                        try:
                            self.release_key(in_key)
                        except ValueError as e:
                            logger.warning(str(e))
                    else:
                        logger.warning('Invalid action: {}. Ignoring message.'.format(msg.action))
                else:
                    logger.info('Message not supported: {}. Ignoring it.'.format(msg.title))
            else:
                logger.warning('Message status is not OK, ignoring it.')
        else:
            logger.warning("This message is not valid. Shouldn't have called on_client_event...")

class Keys:
    """ This class lists the keys used on controllers """
    KEYS_JOYSTICK = {
    'A':		uinput.KEY_A,
    'B':		uinput.KEY_B,
    'X':		uinput.KEY_X,
    'Y':		uinput.KEY_Y,
    'P1':		uinput.KEY_1,
    'P2':		uinput.KEY_2,
    'START':	uinput.KEY_ENTER,
    'SELECT':	uinput.KEY_SPACE,
    'COIN':		uinput.KEY_C,
    'LEFT':		uinput.KEY_LEFT,
    'RIGHT':	uinput.KEY_RIGHT,
    'UP':		uinput.KEY_UP,
    'DOWN':		uinput.KEY_DOWN,
    }

    KEY_STOP_CONTROLLER = 'Key.esc'
