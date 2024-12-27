# # -*- coding: utf-8 -*-

import configparser
import json
import os
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from src.utils.selenium_tools import get_driver

def test_login():
  """
  测试登录状态
  :return:True/False
  """
  driver = get_driver()

  try:
    # 登录智联后 进入主页
    url = f"https://rd6.zhaopin.com/app/recommend?tab=recommend#sortType=recommend"
    driver.get(url)

    element = WebDriverWait(driver, 80).until(
      EC.visibility_of_element_located((By.CLASS_NAME, "app-header__title"))
    )
    # 如果元素存在且可见，打印yes表示已登录
    if '推荐人才' in element.text:
      return True

  except Exception as e:
    print("未登录！请先登录！", e)
    return False
  finally:
    driver.close()


