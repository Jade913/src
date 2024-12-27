# # -*- coding: utf-8 -*-

import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

def deal_new_greet(driver):
  """
  处理向我们打招呼的人
  """
  msg = "开始处理新招呼"

  try:
    driver.get(
      "https://rd6.zhaopin.com/app/recommend?tab=recommend#sortType=recommend")

    element = WebDriverWait(driver, 10).until(
      EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'人才管理')]"))
    )
    element.click()
    msg += "\n成功点击【人才管理】"

    # -----筛选学历-----
    # 点击学历按钮
    edu_selector = WebDriverWait(driver, 10).until(
      EC.element_to_be_clickable((By.CLASS_NAME, 'edu-selector')))
    edu_selector.click()

    dropdown = WebDriverWait(driver, 10).until(
      EC.visibility_of_element_located((By.CLASS_NAME, 'km-select__dropdown')))
    options = dropdown.find_elements(By.CLASS_NAME, 'condition-selector__item')
    msg += f'\n{options}'

    # 定位并选择大专和本科选项
    for option2 in options:
      edu = option2.find_element(By.CLASS_NAME, 'condition-selector__item-label').text.strip()
      if edu in ['大专', '本科', '硕士']:
        option2.click()
        # print(f"已选择学历：{edu}")
        msg += f'\n已选择学历：{edu}'

    # 确定按钮的父级元素
    footer = WebDriverWait(driver, 10).until(
      EC.visibility_of_element_located((By.CLASS_NAME, 'km-select__dropdown-footer'))
    )

    # 定位确定按钮并点击
    confirm_button = footer.find_element(By.XPATH, ".//button[contains(@class, 'km-button--primary')]")
    confirm_button.click()
    # print("筛选学历成功")
    msg += f'\n筛选学历成功'



    # 循环，直到找不到'全选'元素
    while True:
      try:


        # 等待 page-action-bar 元素出现
        page_action_bar = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CLASS_NAME, 'page-action-bar'))
        )

        time.sleep(4)


        # 定位“全选”复选框并勾选上
        select_all_checkbox = page_action_bar.find_element(By.XPATH,
                                                           ".//div[contains(@class, 'footer-action-bar__inner')]//div[@class='km-checkbox__icon']")
        select_all_checkbox.click()

        # 等待“可以聊”按钮出现并点击
        can_chat_button = WebDriverWait(driver, 10).until(
          EC.element_to_be_clickable(
            (By.XPATH, ".//div[contains(@class, 'footer-action-bar__end')]//div[contains(@class, 'is-ml-12')]//button[contains(@class, 'km-button--filled')]"))
        )
        can_chat_button.click()

        try:
        # 等待 'km-popover setting-greet' 模态框出现
          setting_greet_popover = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'setting-greet'))
          )

          if setting_greet_popover:
            # 查找并点击“发送”按钮
            send_button = setting_greet_popover.find_element(By.XPATH,
                                                             "//button[@type='button' and contains(., '发送')]")
            send_button.click()

            print("点击了发送按钮")
            time.sleep(1)

        except Exception as e:
          print(f"没有模态框出现: {e}")

        # actions = ActionChains(driver)
        #
        # # 模拟Ctrl + R 刷新页面
        # actions.key_down(Keys.CONTROL).send_keys('r').key_up(Keys.CONTROL).perform()
        # 等待复选框元素出现
        checkbox_container = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CLASS_NAME, 'not-read'))
        )

        if checkbox_container:
          # 查找复选框元素并点击
          checkbox = checkbox_container.find_element(By.XPATH, ".//div[@class='km-checkbox__icon']")
          checkbox.click()

      except:
        print("找不到'全选'复选框，退出循环")
        break

    # # 获取简历列表
    # # resume_items = driver.find_elements_by_class_name("resume-item")
    # resume_items = WebDriverWait(driver, 10).until(
    #   EC.visibility_of_all_elements_located((By.CLASS_NAME, "resume-item")))
    #
    # # 遍历简历列表
    # for i in range(min(len(resume_items), 3)):
    #   # 遍历的人数
    #   greet_count = 0
    #
    #   resume_buttons = resume_items[i].find_elements(By.CLASS_NAME, "resume-button")
    #
    #   for button in resume_buttons:
    #     # 判断按钮是否可见
    #     if not button.is_displayed():
    #       # 如果按钮不可见，则先滚动页面
    #       driver.execute_script("arguments[0].scrollIntoView(true);", button)
    #       time.sleep(1)  # 等待页面滚动完成
    #     else:
    #       # 点击【可以聊】按钮
    #       if button.text == "可以聊":
    #         # 获取招聘者姓名
    #         candidate_name = resume_items[i].find_element(By.CLASS_NAME, "talent-basic-info__name--inner").text
    #
    #         # 点击打招呼按钮
    #         button.click()
    #         # print("向", candidate_name, "回复了【可以聊】")
    #         msg += f'\n向{candidate_name}回复了【可以聊】'
    #
    #         try:
    #           # 等待 'km-popover setting-greet' 模态框出现
    #           setting_greet_popover = WebDriverWait(driver, 2).until(
    #             EC.presence_of_element_located((By.CLASS_NAME, 'setting-greet'))
    #           )
    #
    #           if setting_greet_popover:
    #             # 查找并点击“发送”按钮
    #             send_button = setting_greet_popover.find_element(By.XPATH,
    #                                                              "//button[@type='button' and contains(., '发送')]")
    #             send_button.click()
    #
    #             print("点击了发送按钮")
    #             time.sleep(1)
    #
    #         except Exception as e:
    #           print(f"出现错误: {e}")
    #
    #
    #         # 增加可以聊的人数计数
    #         greet_count += 1
    #
    #         # 如果已经向三个人点击可以聊，则跳出内部循环
    #         if greet_count >= 3:
    #           break
    #
    #         # 等待一段时间，确保打招呼操作完成
    #         time.sleep(1)
    #
    # msg += f'\n完成{len(resume_items)}份简历的处理'


    return msg

  except Exception as e:
    return False
  # finally:
  #   driver.close()

# if __name__ == '__main__':
#   user_data_dir = r'/private/var/folders/hx/l75c67m978g9zks9crwb78pc0000gn/T/.org.chromium.Chromium.QR8AUf'

#   deal_new_greet(user_data_dir)
