import logging

__author__ = 'Tharun M Paul (tmpaul06@gmail.com)'

NAME = __name__
FORMAT = '%(asctime)s %(name)s %(levelname)s: %(message)s'
DEFAULT_LEVEL = logging.INFO
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_logger(name=NAME, level=DEFAULT_LEVEL, format=FORMAT, date_format=DATE_FORMAT):
    """Return a logger with appropriate settings from config"""
    # Use given name for logger
    logger = logging.getLogger(name)

    # Set level
    logger.setLevel(level)

    # Get console channel
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Set formatter
    ch.setFormatter(logging.Formatter(fmt=format, datefmt=date_format))

    # Add the handler to logger
    logger.addHandler(ch)
    return logger
