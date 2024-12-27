from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.selenium_tools import get_driver


def set_quite():
  driver = get_driver()

  # 打开目标网页
  driver.get('chrome://settings/downloads')

  try:
    # 等待 cr-toggle 元素可见
    toggle_button = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, "//cr-toggle[@id='control']"))
    )

    # 检查 aria-pressed 属性
    aria_pressed = toggle_button.get_attribute('aria-pressed')

    if aria_pressed == 'true':
      toggle_button.click()
      print("已设置下载时不弹窗！")
    else:
      print("已经不弹窗")

  except Exception as e:
    print(f"出现错误: {e}")

  finally:
    # 关闭 WebDriver
    driver.quit()


