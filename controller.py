#!/usr/bin/env python

import sys
import time
import fcntl

import logger as Logger
import bus_types as BusTypes
import socket_server as SocketServer

try:
	import uinput
except ImportError as err:
	Logger.fatal('Failed to import uinput. Are you sure it is installed?', err)

Logger.success('Imported module uinput.')

class Controller:
	""" This class handles the uinput device """
	def __init__(
		self,
		name = 'Controller',
		device_name = 'virtual_controller',
		device_bus_type = BusTypes.BusTypes.VIRTUAL,
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
		self.socket_server = SocketServer.SocketServer(cb_read = self.on_event)

	def start_tcp_server(self):
		self.socket_server.start()

	def stop_tcp_server(self):
		self.socket_server.stop()
		self.socket_server.close()
		self.socket_server.join()

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
		Logger.success('Opened uinput device for controller ' + self.name)

	def close_device(self):
		""" Close the uinput device for this Controller """
		try:
			self.device.destroy()
		except Exception as err:
			Logger.fatal('Failed to destroy a uinput device.', err)
		Logger.success('Destroyed uinput device for controller ' + self.name)

	def list_keys(self):
		""" Print a list of keys supported by this controller. """
		print 'Controller ' + self.name + ' supports the following keys:'
		print self.keys.keys()

	def has_key(self, key):
		""" Check if this Controller has a given key. """
		return key in self.keys

	def click_key(self, key):
		""" Emit a click for a key. The key must be a key in Controller.keys. """
		if not self.has_key(key):
			Logger.warning('Key {0} is not supported by this Controller.'.format(key))
		else:
			self.device.emit_click(self.keys[key])

	def press_key(self, key):
		""" Press down on a key. The key must be in Controller.keys. """
		if not self.has_key(key):
			Logger.warning('Key {0} is not supported by this Controller.'.format(key))
		else:
			self.device.emit(self.keys[key], 1)

	def release_key(self, key):
		""" Release a key. The key must be in Controller.keys. """
		if not self.has_key(key):
			Logger.warning('Key {0} is not supported by this Controller.'.format(key))
		else:
			self.device.emit(self.keys[key], 0)

	def on_event(self, msg):
		print 'CONTROLLER RECEIVED MSG: {}'.format(msg)

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
