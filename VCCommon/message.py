#!/usr/bin/env python

import json
import VCLogger

""" JSON format for ALL messages:
{
    "title": "EVENT",
    "value": "KEY_A",
    "action": "PRESSED",
    "status": 0
}

Possible values for each field are specified in subclasses of Messages.
"""

logger = VCLogger.Logger(VCLogger.Level.ALL)

class Message:
    """ Represent a message received from, or sent to and socket.
    Transferred messages are formated in JSON """

    def __init__(self, title = None, value = None, action = None, status = None):
        self.title = title
        self.value = value
        self.action = action
        self.status = status

    def read_message(self, msg):
        """ Convert a message from JSON to Message """
        try:
            json_parsed = json.loads(msg)
        except ValueError as err:
            logger.warning('Message is not in JSON format.', err)
            return

        if json_parsed['title'] is None:
            logger.warning("This message doesn't contain a title: \n{}".format(msg))
            return
        if json_parsed['value'] is None:
            logger.warning("This message doesn't contain a value: \n{}".format(msg))
            return
        if json_parsed['action'] is None:
            logger.warning("This message doesn't contain an action: \n{}".format(msg))
            return
        if json_parsed['status'] is None:
            logger.warning("This message doesn't contain a status: \n{}".format(msg))
            return

        self.title = json_parsed['title']
        self.value = json_parsed['value']
        self.action = json_parsed['action']
        self.status = json_parsed['status']

    def is_valid(self):
        """ Return True if all fields are set """
        if (self.title is not None
            and self.value is not None
            and self.action is not None
            and self.status is not None):
            return True
        return False

    def is_error(self):
        """ Return True if this message contains a status ERROR """
        return (self.status == StatusCodes.ERROR)

    def is_ok(self):
        """ Return True if this message contains a status OK """
        return (self.status == StatusCodes.OK)

    def is_stop(self):
        """ Return True if this message contains a status STOP """
        return (self.status == StatusCodes.STOP)

    def format_json(self):
        """ Stringify this json message """
        if not self.is_valid():
            logger.warning('Attempting to format an invalid message:')
            return ''
        data = {}
        data['title'] = self.title
        data['value'] = self.value
        data['action'] = self.action
        data['status'] = self.status
        return json.dumps(data)

    def __str__(self):
        return "Title: {}\n\
                Value: {}\n\
                Action: {}\n\
                Status: {}\n".format(self.title, self.value, self.action, self.status)

class Titles:
    EVENT = "EVENT"
    CONTROL = "CONTROL"

class Actions:
    PRESSED = "PRESSED"
    RELEASED = "RELEASED"
    RELOAD_DEVICE = "RELOAD_DEVICE"
    STOP_SERVER = "STOP_SERVER"
    STOP_CONTROLLER = "STOP_CONTROLLER"

class StatusCodes:
    ERROR = -1
    OK = 0
    STOP = 1 # Asks the server to close the connection
