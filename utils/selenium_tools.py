# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
import platform
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from .kltrpa_path import base_dir, download_path
def get_driver():
  # 谷歌目录
  os_platform = platform.system()
  if os_platform == "Windows":
    chrome_binary_path = base_dir + f"\ext_tools\chrome\win\chrome-win32\chrome.exe"
    chrome_driver_path = base_dir + f"\ext_tools\chrome\win\chromedriver-win32\chromedriver.exe"
  elif os_platform == "Darwin":  # macOS
    os_type = 'mac-x64'
    chrome_binary_path = base_dir + f"/ext_tools/chrome/mac/chrome-{os_type}/Google.app/Contents/MacOS/Google"
    chrome_driver_path = base_dir + f"/ext_tools/chrome/mac/chromedriver-{os_type}/chromedriver"

  user_data_dir = base_dir + r"ext_tools/chrome-data"

  # 创建文件夹用于存放下载的PDF文件
  if not os.path.exists(download_path):
    os.makedirs(download_path)

  # 设置 ChromeOptions
  chrome_options = webdriver.ChromeOptions()
  chrome_options.binary_location = chrome_binary_path
  # 添加选项：
  chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
  # 设置下载路径
  prefs = {"download.default_directory": download_path}
  chrome_options.add_experimental_option("prefs", prefs)
  # 实例化
  service = Service(chrome_driver_path)
  driver = webdriver.Chrome(service=service, options=chrome_options)

  # 放大窗口
  driver.maximize_window()
  return driver

# 判断岗位对应什么课程
def get_course(job_title):
  fico_keywords = ['财务', '会计', '审计', '出纳']
  mm_keywords = ['物流', '物料', '采购', '供应链', '仓储', '仓库', '供应商']
  sd_keywords = ['销售', '统计', '订单', '数据', '商务', '运营']
  course_keywords ={'FICO':['财务', '会计', '审计', '出纳'],
  'MM': ['物流', '采购', '供应链', '仓储', '仓库', '供应商'],
  'SD':['销售', '统计', '订单', '数据', '商务', '运营'],
  }

  for keyword_list, regit_course in [(fico_keywords, 'FICO'), (mm_keywords, 'MM'), (sd_keywords, 'SD')]:
    pattern = '|'.join(keyword_list)
    if re.search(pattern, job_title):
      return regit_course
  return '待填写'

