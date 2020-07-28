import logging

logger = None


def get_logger(name):
    global logger
    if logger is None:
        logging.basicConfig()
        logger = logging.getLogger(name)
        # logger.setLevel(logging.INFO)
        logger.setLevel(logging.DEBUG)
    return logger
