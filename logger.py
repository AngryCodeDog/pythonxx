#! encoding=utf-8
__author__ = 'zyp'
import logging

formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)s] - %(levelname)s %(message)s')

_logger_dict = {}



def create_logger(name):
    logger = logging.Logger(name)

    handle = logging.StreamHandler()
    fh = logging.FileHandler('log.log')

    handle.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(handle)
    logger.addHandler(fh)


    return logger


logger = create_logger("app")
