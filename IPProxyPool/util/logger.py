# coding:utf-8
import logging

__author__ = 'qiye'

logger = logging.getLogger()


def logger_proxy(proxy):
    """
    Sets a logger.

    Args:
        proxy: (todo): write your description
    """
    logger.setLevel(logging.INFO)
    logger.info(proxy)
