#!/usr/bin/env python

###
# Logging functions for the controller simulator.
###

import sys
import os
import time
from colors import Colors

DATE_TIME_FORMAT = '%d/%m/%Y-%H:%M:%S'

class Level:
    """ Definition of different levels of logging """
    ERRORS      = 0     # Fatal errors only
    WARNINGS    = 1     # Add warnings
    CONNECTIONS = 2     # Add socket connection/disconnection log
    EVENTS      = 3     # Add log for uinput events generated
    SUCCESSES   = 4     # Add success log
    ALL         = 10    # Print all log messages

class Logger:
    def __init__(self, level = Level.ALL):
        self.level = level

    def print_err_msg(self, msg, err):
        """ Print details about an error message """
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

    def fatal(self, msg, err):
        """ Messages related to fatal erros; will exit the program """
        if err is not None:
            print '[ ' + Colors.RED_BOLD + 'FATAL ERROR' + Colors.RESET + ' ]'
            self.print_err_msg(msg, err)
        else:
            print '[ ' + Colors.RED_BOLD + 'FATAL ERROR' + Colors.RESET + ' ] ' + msg
        exit()

    def warning(self, msg, err = None):
        """ Messages related to important warnings, that are not fatal """
        if err is not None:
            print '[ ' + Colors.YELLOW_BOLD + 'WARNING' + Colors.RESET + ' ]'
            self.print_err_msg(msg, err)
        else:
            print '[ ' + Colors.YELLOW_BOLD + 'WARNING' + Colors.RESET + ' ] ' + msg

    def info(self, msg):
        """ Generic info message """
        print '[ ' + Colors.WHITE_BOLD + 'INFO' + Colors.RESET + ' ] ' + msg

    def success(self, msg):
        """ Generic success messages """
        print '[ ' + Colors.GREEN_BOLD + 'OK' + Colors.RESET + ' ] ' + msg

    def connection_info(self, msg):
        """ Messages related to socket connections / disconnections """
        print '[ ' + Colors.CYAN_BOLD + 'CONNECT' + Colors.RESET + ' ] ' + msg

    def event_info(self, msg):
        """ Messages related to uinput events generated """
        print '[ ' + Colors.BLUE_BOLD + 'EVENT' + Colors.RESET + ' ] ' + msg
