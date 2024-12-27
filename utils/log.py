# # -*- coding: utf-8 -*-

import logging
import time
import os
from logging.handlers import TimedRotatingFileHandler

from .kltrpa_path import log_path

def get_logger(text_edit):
    # 创建logger
    logger = logging.getLogger('kltrpa')
    logger.setLevel(logging.INFO)

    # 创建file handler，用于写入日志文件
    log_folder = log_path
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    # 日志文件路径
    log_file_path = os.path.join(log_folder, "app.log")

    # 文件处理器，按天滚动
    file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1,
                                                             backupCount=7,
                                                             encoding='utf-8')
    qt_handler = QtLogHandler(text_edit)

    # 创建formatter，用于设定输出格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    qt_handler.setFormatter(formatter)

    # 添加handler到logger
    logger.addHandler(file_handler)
    logger.addHandler(qt_handler)
    return logger


class QtLogHandler(logging.Handler):
    def __init__(self, text_edit):
        super(QtLogHandler, self).__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg) 
        self.flush()