#!/usr/bin/env python

###
# Logging functions for the controller simulator.
###

import sys
import os
import time
from colors import Colors

DATE_TIME_FORMAT = '%d/%m/%Y-%H:%M:%S'

### Debugging functions
def print_err_msg(msg, err):
	exc_type, exc_value, exc_tb = sys.exc_info()
	file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	err_line = exc_tb.tb_lineno
	tb_msg = exc_value.message
	print '|\tDate: ' + time.strftime(DATE_TIME_FORMAT)
	print '|\tIn: ' + file_name
	print '|\tLine: {0}'.format(err_line)
	print '|\tType: ' + exc_type.__name__
	print '|\tMessage: ' + msg
	print '|\tDetails: {0}'.format(err)

def fatal(msg, err):
	if err is not None:
		print '[ ' + Colors.RED_BOLD + 'FATAL ERROR' + Colors.RESET + ' ]'
		print_err_msg(msg, err)
	else:
		print '[ ' + Colors.RED_BOLD + 'FATAL ERROR' + Colors.RESET + ' ] ' + msg
	exit()

def warning(msg, err = None):
	if err is not None:
		print '[ ' + Colors.YELLOW_BOLD + 'WARNING' + Colors.RESET + ' ]'
		print_err_msg(msg, err)
	else:
		print '[ ' + Colors.YELLOW_BOLD + 'WARNING' + Colors.RESET + ' ] ' + msg

def success(msg):
	print '[ ' + Colors.GREEN_BOLD + 'OK' + Colors.RESET + ' ] ' + msg

def info(msg):
	print '[ ' + Colors.WHITE_BOLD + 'INFO' + Colors.RESET + ' ] ' + msg
