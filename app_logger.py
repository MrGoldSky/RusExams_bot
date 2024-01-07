import logging
from datetime import datetime

_log_format = """%(asctime)s [%(name)s:%(levelname)s] [%(filename)s <%(lineno)s>: %(module)s.%(funcName)s] %(message)s"""

def get_file_handler():
    file_handler = logging.FileHandler(r'{0}'.format((str((datetime.now().strftime("""%d.%m.%Y_%H.%M.%S"""))  + '_Log.log'))))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler

def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger