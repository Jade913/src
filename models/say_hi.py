# # -*- coding: utf-8 -*-

import time
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def say_hi(driver):
  msg = '开始处理打招呼'
  try:
    driver.get(
        "https://rd6.zhaopin.com/app/recommend?tab=recommend#sortType=recommend")
    try:
      filter_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'tr-filter-trigger'))
      )
      filter_button.click()
      msg += "\n----筛选按钮已点击"
      # 等待最近筛选区域可见并点击最近筛选后的按钮（这里假设是第一个筛选条件）
      recent_filter_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
          (By.XPATH, '//div[@class="tr-talent-filter__history-con"]//div[@class="tr-talent-filter__history-item"][1]'))
      )
      recent_filter_button.click()
      # print("最近筛选按钮已点击")
      msg += "\n----最近筛选按钮已点击"

      # 在执行完点击筛选按钮和选择筛选条件的操作后，等待确定按钮可点击并点击
      confirm_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="km-modal__footer"]//button[@zp-stat-id="rsmlist-confirm"]'))
      )
      confirm_button.click()
      # print("确定按钮已点击")
      msg += "\n----确定按钮已点击"

      #------------对每个岗位前20个人打招呼

      # 获取岗位列表的父元素
      parent_element = driver.find_element(By.CLASS_NAME, "talent-job__job-wrap")

      # 找到岗位列表中的所有岗位元素
      job_elements = parent_element.find_elements(By.CLASS_NAME, "job-pane__item")

      # 遍历岗位列表
      for job_element in job_elements:
        # 获取岗位名称
        job_title = job_element.find_element(By.CLASS_NAME, "job-pane__item-job-title").text
        # print("-------当前岗位:", job_title)
        msg += f"\n-------当前岗位:{job_title}"

        # 点击岗位元素
        job_element.click()

        # 等待页面加载完成
        time.sleep(2)

        # 获取招聘者列表
        recommend_items = driver.find_elements(By.CLASS_NAME, "recommend-item")

        # 遍历招聘者列表
        for i in range(min(len(recommend_items), 5)):
          #打招呼的人数
          greet_count = 0

          resume_buttons = recommend_items[i].find_elements(By.CLASS_NAME, "resume-button")

          for button in resume_buttons:
            # 判断按钮是否可见
            if not button.is_displayed():
              # 如果按钮不可见，则先滚动页面
              driver.execute_script("arguments[0].scrollIntoView(true);", button)
              time.sleep(1)  # 等待页面滚动完成
            else:
              if button.text == "打招呼":
                # 获取招聘者姓名
                candidate_name = recommend_items[i].find_element(By.CLASS_NAME, "talent-basic-info__name--inner").text

                # 点击打招呼按钮
                button.click()
                # print("向", candidate_name, "打了招呼")
                msg += f"\n向 {candidate_name}打了招呼"


                # 增加已打招呼的人数计数
                greet_count += 1

                # 如果已经向三个人打过招呼，则跳出内部循环
                if greet_count >= 3:
                  break

                # 等待一段时间，确保打招呼操作完成
                time.sleep(1)

        # 返回上一页，准备点击下一个岗位
        driver.back()

      #------------over



    except Exception as e:
      # print("发生异常:", e)
      msg += f"\n----发生异常:{str(e)[:50]}"

    # print("页面加载成功！")
    msg += f"\n----页面加载成功！"
  except Exception as e:
    # print("页面加载失败:", e)
    msg += f"\n----页面加载失败:{str(e)[:50]}"
  return msg

  # finally:
  #   driver.close()


if __name__ == '__main__':
  user_data_dir = r'/private/var/folders/hx/l75c67m978g9zks9crwb78pc0000gn/T/.org.chromium.Chromium.QR8AUf'

  say_hi(user_data_dir)
