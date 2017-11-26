#!/usr/bin/env python

from pynput import keyboard
import socket
import sys

from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from VCCommon import message
from VCCommon import VCLogger

logger = VCLogger.Logger(VCLogger.Level.ALL)

host = '192.168.1.80'
port = 2010

if len(sys.argv) > 2:
    port = int(sys.argv[2])
if len(sys.argv) > 1:
    host = sys.argv[1]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect((host, port))
except socket.error as e:
    logger.fatal('Could not connect to host {} on port {}'.format(host, port), e)

logger.connection_info('Connected to host {} on port {}'.format(host, port))

def is_special_key(key):
    if isinstance(key, keyboard.Key):
        return True
    if isinstance(key.char, unicode):
        return False
    return True

def get_key_name(key):
    if is_special_key(key):
        return str(key)
    else:
        return key.char.encode('utf8')

def send_key(key_name, action):
    msg = message.Message(
        title = message.Titles.EVENT,
        value = key_name,
        action = action,
        status = message.StatusCodes.OK,
    )
    send_message(msg)

def send_message(message):
    json_message = message.format_json()
    logger.info('Sending json_message = {}'.format(json_message))
    if json_message:
        sock.send(json_message)

def on_press(key):
    key_name = get_key_name(key)
    send_key(key_name, message.Actions.PRESSED)

def on_release(key):
    key_name = get_key_name(key)

    if key_name == 'Key.backspace':
        logger.info('Requesting reload of VirtualController')
        msg = message.Message(
            title = message.Titles.CONTROL,
            value = '-',
            action = message.Actions.RELOAD_DEVICE,
            status = message.StatusCodes.OK,
        )
        send_message(msg)
    elif key_name == 'T':
        logger.info('Requesting termination of this connection')
        msg = message.Message(
            title = message.Titles.CONTROL,
            value = '-',
            action = message.Actions.STOP_CONTROLLER,
            status = message.StatusCodes.OK,
        )
        send_message(msg)
    elif key_name == 'Key.esc':
        logger.info('Requesting termination of VirtualController')
        msg = message.Message(
            title = message.Titles.CONTROL,
            value = '-',
            action = message.Actions.STOP_SERVER,
            status = message.StatusCodes.OK,
        )
        send_message(msg)
        return False
    else:
        send_key(key_name, message.Actions.RELEASED)

with keyboard.Listener(
    on_press = on_press,
    on_release = on_release) as listener:
    listener.join()

logger.connection_info('Closing socket')
sock.shutdown(2)
sock.close()
