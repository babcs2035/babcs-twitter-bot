import logging
import sys
import socket
from logging.handlers import SysLogHandler

logger = logging.getLogger()


def my_handler(type, value, tb):
    global logger

    logger.exception('Uncaught exception: {0}'.format(str(value)))


def log_init():
    global logger

    syslog = SysLogHandler(address=('logs5.papertrailapp.com', 28031))
    format = '%(asctime)s logging: %(message)s'
    formatter = logging.Formatter(format, datefmt='%b %d %H:%M:%S')
    syslog.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(syslog)
    logger.setLevel(logging.INFO)
    sys.excepthook = my_handler
