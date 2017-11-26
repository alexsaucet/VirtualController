#!/usr/bin/env python

"""
Virtual controller based on python-uinput
(https://github.com/tuomasjjrasanen/python-uinput)
A VCClient can send keyboard events, causing this Controller to emit
the events on the uinput driver.
Input messages must be in the JSON format specified in message.py; other messages
will be ignored.
"""

import sys
import time
import fcntl
from threading import Thread

from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from VCCommon import message
from VCCommon import VCLogger

import bus_types
import socket_server

try:
    import uinput
except ImportError as err:
    logger.fatal('Failed to import uinput. Are you sure it is installed?', err)

logger = VCLogger.Logger(VCLogger.Level.ALL)
logger.success('Imported module uinput.')

class Controller(Thread):
    """ This class handles the uinput device """
    def __init__(
        self,
        name = 'Controller',
        device_name = 'virtual_controller',
        device_bus_type = bus_types.BusTypes.USB,
        device_version = 1,
        keys = None,
    ):
        """ Set the uinput device settings, and define the list of keys the controller will support """
        Thread.__init__(self)
        self.name = name
        self.device = None
        self.device_name = device_name
        self.device_bus_type = device_bus_type
        self.device_version = device_version
        if keys is None:
            self.keys = Keys.KEYS_JOYSTICK
        else:
            self.keys = keys
        self.server_sock = socket_server.SocketServer(cb_read = self.on_client_event, port = 2011)

    def run(self):
        self.__stop = False
        """ Start the Controller. Start the TCP socket server and open the uinput device. """
        logger.info('Starting Controller {}.'.format(self.name))
        self.open_device()
        self.start_tcp_server()

        while not self.__stop:
            time.sleep(1)

        # Stop socket server
        logger.info('Stopping Controller {}...'.format(self.name))
        self.stop_tcp_server()
        self.close_device()

    def stop(self):
        """ Stop the Controller. Closes the TCP socket server, and closes the uinput device. """
        self.__stop = True

    def is_running(self):
        return not self.__stop

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
            logger.event_info('Sending uinput event: click key {} ({}).'.format(key, sekf.keys[key]))

    def press_key(self, key):
        """ Press down on a key. The key must be defined in Controller.keys. """
        if not self.has_key(key):
            raise ValueError('Key {0} is not supported by this Controller.'.format(key))
        else:
            self.device.emit(self.keys[key], 1)
            logger.event_info('Sending uinput event: press key {} ({}).'.format(key, self.keys[key]))

    def release_key(self, key):
        """ Release a key. The key must be defined in Controller.keys. """
        if not self.has_key(key):
            raise ValueError('Key {0} is not supported by this Controller.'.format(key))
        else:
            self.device.emit(self.keys[key], 0)
            logger.event_info('Sending uinput event: release key {} ({}).'.format(key, self.keys[key]))

    def on_client_event(self, msg):
        """ Callback function called by the SocketServer when it receives a valid
        Message. Will trigger the uinput event if the Message is supported by this
        Cotroller. """
        logger.info('Controller received message: {}'.format(msg.format_json()))
        if msg.is_valid():
            if msg.is_ok():
                if msg.title == message.Titles.CONTROL:
                    if msg.action == message.Actions.RELOAD_DEVICE:
                        logger.info('Reloading device...')
                        self.close_device()
                        self.open_device()
                        logger.info('Device reloaded!')
                    elif msg.action == message.Actions.STOP_SERVER:
                        logger.info('Stopping server...')
                        self.stop()
                        return

                elif msg.title == message.Titles.EVENT:
                    # Convert to upper case to ignore case of input
                    in_key = msg.value.upper()

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
        'A': uinput.KEY_A,
        'Z': uinput.KEY_B,
        'S': uinput.KEY_X,
        'D': uinput.KEY_Y,
        '1': uinput.KEY_1, # Player 1
        '2': uinput.KEY_2, # Player 2
        'KEY.ENTER': uinput.KEY_ENTER, # start
        'KEY.SPACE':uinput.KEY_SPACE, # select
        'C': uinput.KEY_C, # insert coin
        'KEY.LEFT': uinput.KEY_LEFT, # left
        'KEY.RIGHT': uinput.KEY_RIGHT, # right
        'KEY.UP': uinput.KEY_UP, # up
        'KEY.DOWN': uinput.KEY_DOWN, # down
        'KEY.F4': uinput.KEY_F4, # F4
        'KEY.SHIFT': uinput.KEY_LEFTSHIFT,  # Left shoulder to load a save
        'KEY.SHIFT_R': uinput.KEY_RIGHTSHIFT,  # Right shoulder to save game
    }

    KEYS_TEST_2 = {
        'A': uinput.BTN_A,
        'Z': uinput.BTN_B,
        'S': uinput.BTN_X,
        'D': uinput.BTN_Y,
        'KEY.SHIFT': uinput.BTN_TL,
        'KEY.CAPS_LOCK': uinput.BTN_TL2,
        'KEY.SHIFT_R': uinput.BTN_TR,
        '`': uinput.BTN_TR2,
        '1': uinput.BTN_1, # Player 1
        '2': uinput.BTN_2, # Player 2
        'KEY.ENTER': uinput.BTN_START, # start
        'KEY.SPACE':uinput.BTN_SELECT, # select
        'M': uinput.BTN_MODE,
        'KEY.CMD': uinput.BTN_THUMBL,
        'KEY.CMD_R': uinput.BTN_THUMBR,
        'C': uinput.BTN_C, # insert coin
        'Z': uinput.BTN_Z, # Dont know
        'KEY.LEFT': uinput.BTN_DPAD_LEFT, # left
        'KEY.RIGHT': uinput.BTN_DPAD_RIGHT, # right
        'KEY.UP': uinput.BTN_DPAD_UP, # up
        'KEY.DOWN': uinput.BTN_DPAD_DOWN, # down
        'KEY.F4': uinput.KEY_F4, # F4
    }

    KEYS_TEST = {
        'A': uinput.BTN_A,
        'Z': uinput.BTN_B,
        'C': uinput.BTN_C,
        'S': uinput.BTN_X,
        'D': uinput.BTN_Y,
        'W': uinput.BTN_Z,
        'KEY.SHIFT':        uinput.BTN_TL,  # Trigger Left
        'KEY.SHIFT_R':      uinput.BTN_TR,  # Trigger Right
        'KEY.CAPS_LOCK':    uinput.BTN_TL2, # Trigger Left 2
        '`':            uinput.BTN_TR2,     # Trigger Right 2
        'KEY.CMD':      uinput.BTN_SELECT,  # Select
        'KEY.CMD_R':    uinput.BTN_START,   # Start
        'M':            uinput.BTN_MODE,    # Mode
        'KEY.ALT':      uinput.BTN_THUMBL,  # Thumb Left
        'KEY.ALT_R':    uinput.BTN_THUMBR,  # Thumb Right
    }

    #KEY_STOP_CONTROLLER = 'KEY.ESC'
