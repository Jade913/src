# # -*- coding: utf-8 -*-

import json
import logging
import os
import re
import time
import winsound

import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from src.utils.selenium_tools import get_course
from src.utils.tabledata import import_single_resume_to_table, append_row_to_excel, generate_filename, init_excel_file


def sound():
    freq = 2000
    duration = 100
    winsound.Beep(freq, duration)


def countdown(t):
    for i in range(t, 0, -1):
        print(f'倒计时{i}秒')
        time.sleep(1)
        sound()


def download_resume(driver, table_widget):
    msg = "开始处理简历信息及下载简历"

    url = "https://rd6.zhaopin.com/app/candidate?tab=pending&jobNumber=-1&jobTitle=%E4%B8%8D%E9%99%90"
    driver.get(url)

    # 使用 XPath 定位包含文本为"沟通中"的<span>元素
    tab_span = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@class='candidate-tabs']/div[@class='candidate-tabs--left']//span[text()='沟通中']"))
    )

    # 获取该<span>元素的父节点<div>元素，即包含【沟通中】按钮的<div>元素
    tab_div = tab_span.find_element(By.XPATH, "./..")

    # 点击【沟通中】按钮
    tab_div.click()
    # print("点击【沟通中】按钮成功")
    msg += "\n点击【沟通中】按钮成功"

    # # 等待职位选择器可见
    # job_selector = WebDriverWait(driver, 10).until(
    #   EC.visibility_of_element_located((By.CLASS_NAME, "job-selector"))
    # )
    #
    # # 点击职位选择器
    # job_selector.click()
    #
    # # 等待职位选项可见
    # job_options = WebDriverWait(driver, 10).until(
    #   EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".job-selector__item"))
    # )
    #
    # # 遍历点击所有的职位选项
    # for option in job_options:
    #   job_title_element = option.find_element(By.CLASS_NAME, "job-selector__item-title")
    #   job_title = job_title_element.text
    #   if job_title == "不限":
    #     continue  # 跳过第一个选项
    #   # try:
    #   job_location_element = option.find_element(By.CLASS_NAME, "job-selector__item-city")
    #   job_location = job_location_element.text.strip()
    #   # except NoSuchElementException:
    #   #   job_location = "未提供"
    #   print("当前职位：", job_title, "，职位地点：", job_location)
    #   msg += f"\n当前职位：{job_title}，职位地点：{job_location}"
    #   option.click()
    #   time.sleep(1)  # 等待页面加载

    contact_selector = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'contact-selector')))
    contact_selector.click()

    by_phone = driver.find_element(By.XPATH,
                                   "//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']//div[@class='km-scrollbar__view']//div[@class='km-select__options']//a[@class='condition-selector__item km-option']//div[@class='km-option__label']//div[@title='有电话']")
    by_phone.click()

    try:
        # 等待复选框元素出现
        checkbox_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'not-read'))
        )

        if checkbox_container:
            # 查找复选框元素并点击
            checkbox = checkbox_container.find_element(By.XPATH, ".//div[@class='km-checkbox__icon']")
            checkbox.click()


    except Exception as e:
        print(f"出现错误: {e}")

    # 点击标签按钮
    tag_selector = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'resume-tag-selector')))
    tag_selector.click()

    untag_div = driver.find_element(By.XPATH,
                                    "//div[@class='km-popover__inner']//div[@class='km-select__dropdown km-select__dropdown--multiple']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']//div[@class='km-scrollbar__view']//div[@class='km-select__options']//a[@class='condition-selector__item km-option km-option--multiple']//div[@class='km-option__label']//div[@title='未加标签的']")
    untag_div.click()

    # 确定框的父级
    popovers = driver.find_elements(By.XPATH,
                                    "//div[contains(@class, 'km-popover') and contains(@class, 'km-select__dropdown-wrapper') and contains(@class, 'condition-selector-popper')]")

    # 根据实际情况调整索引
    target_popover = popovers[1]

    # 在选中的popover中查找确定按钮
    confirm_button = target_popover.find_element(By.XPATH,
                                                 ".//div[@class='km-select__dropdown-footer']//button[@class='km-button km-control km-ripple-off km-button--primary km-button--filled is-mini']")
    confirm_button.click()

    # 点击 job-selector 以显示选项
    job_selector = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'job-selector')))
    job_selector.click()

    print("请在十秒内输入校区")
    countdown(10)

    # 5.31
    # 定位滚动容器
    wrap = driver.find_element(By.XPATH,
                               "//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']")

    # # 定义一个函数来滚动容器
    try:
        # popper = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,"//div[@class='km-popover km-select__dropdown-wrapper job-selector-popper']")))
        wrap2 = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,
                                            "//div[@class='km-popover km-select__dropdown-wrapper job-selector-popper']//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']")))

        ActionChains(driver).move_to_element(wrap2).perform()
        # 向下滚动20次，每次滚动一定的像素值（例如100px）
        for _ in range(20):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 100;", wrap2)
            time.sleep(0.5)

        print("已经滚动到容器底部!")
        # 确保容器高度不是0
        # wrap_height = driver.execute_script("return arguments[0].offsetHeight;", wrap)
        # if wrap_height == 0:
        #     print("容器高度为0，可能没有内容或样式问题。")
        # else:
        #     # 尝试滚动到容器底部
        #     last_scroll_top = 0
        #     while True:
        #         driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", wrap)
        #         time.sleep(1)  # 等待是为了观察效果，但在实际测试中可能需要更复杂的逻辑
        #
        #         new_scroll_top = driver.execute_script("return arguments[0].scrollTop;", wrap)
        #         if new_scroll_top == last_scroll_top:
        #             break  # 如果没有新的滚动发生，则退出循环
        #         last_scroll_top = new_scroll_top
    except Exception as e:
        print(f"{e}---请手动滚动岗位列表到底部!---")
        # countdown(10)

    # 滚动到容器底部以确保加载所有选项
    # 获取所有选项元素
    options = driver.find_elements(By.XPATH,
                                   "//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']//div[@class='km-scrollbar__view']//div[@class='km-select__options']//a[@class='job-selector__item km-option']")

    resume_num = 0
    temp_file_path = generate_filename('抓取数据_临时')
    # 初始化临时 Excel 文件
    init_excel_file(temp_file_path)

    # 初始化当前索引变量
    current_index = 0

    print("请在10秒内选择起始岗位")
    countdown(10)
    # 获取所有选项元素
    # km_select_options = driver.find_elements(By.XPATH,
    #                                          "//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']//div[@class='km-scrollbar__view']//div[@class='km-select__options']")
    # options = driver.find_elements(By.XPATH,
    #                                "//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']//div[@class='km-scrollbar__view']//div[@class='km-select__options']//a[@class='job-selector__item km-option']")

    # 尝试获取手动选中的选项
    try:

        #
        current_selected_option = driver.find_element(By.XPATH,
                                                      "//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']//div[@class='km-scrollbar__view']//div[@class='km-select__options']//a[@class='job-selector__item km-option is-selected']")
        # 提取当前选中选项的岗位名称和岗位地址
        # 获取span元素的title属性作为岗位名称
        current_job_title = current_selected_option.find_element(By.CSS_SELECTOR,
                                                                 ".job-selector__item-title").get_attribute("title")
        # 获取div元素的title属性作为岗位地址
        current_job_city = current_selected_option.find_element(By.CSS_SELECTOR,
                                                                ".job-selector__item-city").get_attribute("title")
        print(f"当前选中的岗位名称: {current_job_title}")
        print(f"当前选中的岗位地址: {current_job_city}")
        # 遍历options列表
        for index, option in enumerate(options):
            # 提取当前option的岗位名称和岗位地址
            job_title = option.find_element(By.CSS_SELECTOR, ".job-selector__item-title").get_attribute("title")
            if job_title == '不限':
                continue
            job_city = option.find_element(By.CSS_SELECTOR, ".job-selector__item-city").get_attribute("title")
            print(f"当前option的岗位名称和岗位地址{index}：{job_title}---{job_city}")

            # 检查岗位名称和岗位地址是否匹配
            if job_title == current_job_title and job_city == current_job_city:
                current_index = index
                break  # 如果找到匹配项，则跳出循环
        if current_index == 0:
            print("未找到手动选中的选项，默认从头开始")
        else:
            print(f"将从第{current_index}个岗位开始遍历")
    except:
        options = driver.find_elements(By.XPATH,
                                       "//a[@class='job-selector__item km-option']")

        print("出错了，默认从头开始!")

    # 从当前索引开始遍历所有选项
    for option in options[current_index:]:

        #  遍历所有选项
        # for option in options:
        title_element = option.find_element(By.XPATH, ".//div[@class='job-selector__item-job']//span")
        job_title = title_element.get_attribute('title')

        # 排除【不限】选项
        if job_title != '不限':
            # 输出当前选项的城市名称
            city_element = option.find_element(By.XPATH, ".//div[@class='job-selector__item-city']")
            job_location = city_element.get_attribute('title')
            print(f"当前职位: {job_title}, 职位地点: {job_location}")
            msg += f"\n当前职位：{job_title}，职位地点：{job_location}"
            # 构造XPath表达式，包含所有指定的层级以及job_title和city的条件
            # xpath = f"""
            # //div[@class='km-popover__inner']
            #   //div[@class='km-select__dropdown']
            #   //div[@class='km-scrollbar']
            #   //div[@class='km-scrollbar__wrap']
            #   //div[@class='km-scrollbar__view']
            #   //a[@class='job-selector__item km-option']
            #     [div[@class='job-selector__item-job']
            #       [span[@title='{job_title}']]
            #       [{f".//div[@class='job-selector__item-city' and @title='{job_location}']" if job_location else ''}]
            #     ]
            # """

            try:
                # current_option = WebDriverWait(driver, 3).until(
                #       EC.element_to_be_clickable((By.XPATH,
                #                                   f"//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']//div[@class='km-scrollbar__view']//div[@class='km-select__options']//a[@class='job-selector__item km-option']//div[@class='job-selector__item-job']//span[@title='{job_title}']")))
                # 等待元素变得可点击并点击它
                # current_option = WebDriverWait(driver, 3).until(
                #   EC.element_to_be_clickable((By.XPATH, xpath))
                # )
                # current_option.click()
                option.click()
            except:

                # 每次点击 job-selector 以显示选项
                job_selector = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'job-selector')))
                job_selector.click()

                # 点击当前选项
                # current_option = WebDriverWait(driver, 3).until(
                #   EC.element_to_be_clickable((By.XPATH, xpath))
                # )
                # current_option.click()
                option.click()

            # 创建一个空列表来存储每个招聘者的信息
            resume_info_list = []

            try:

                # 等待第一个简历项可见
                resume_items = WebDriverWait(driver, 5).until(
                    EC.visibility_of_all_elements_located((By.CLASS_NAME, "resume-item__content")))

                # 点击第1个简历项
                resume_items[0].click()

            except:
                print(f"---当前岗位{job_title}没有投递者！---")
                continue
            i = 0
            old_resume_number = ""

            while True:
                clicked_save = False

                try:
                    try:
                        # 等待邮箱元素出现（如果它存在的话）
                        email_element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.resume-basic-new__email .is-ml-4'))
                        )
                        email_exist = True
                    except:
                        email_exist = False

                    try:
                        # 判断是不是统招
                        # 定位到包含教育经历的元素
                        # education_section = WebDriverWait(driver, 2).until(
                        #     EC.presence_of_element_located((By.CLASS_NAME, 'resume-section-new__body')))

                        education_section = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'resume-section-education-experiences'))
                        )
                        # 在resume-section-new__body下找new-education-experiences__item元素
                        education_items = education_section.find_elements(By.CLASS_NAME,
                                                                          'new-education-experiences__item')
                        for item in education_items:
                            # 提取时间范围信息
                            date_text = item.find_element(By.CLASS_NAME, 'new-education-experiences__item-time').text
                            if ' - ' in date_text:
                                date_range = date_text.split(' - ')
                                start_date = date_range[0]
                                end_date = date_range[1]

                                # 提取年份和月份
                                start_year, start_month = map(int, start_date.split('.'))
                                end_year, end_month = map(int, end_date.split('.'))

                                # 判断是否满足统招条件
                                if (end_year - start_year) >= 3 and start_month == 9 and (
                                        end_month == 6 or end_month == 7):
                                    print("是统招生")
                                    is_rec = True
                                    break  # 如果找到符合条件的，可以退出循环
                                else:
                                    print("不是统招生")
                                    is_rec = False
                    except:
                        print("无法判断是否为统招生，默认是")
                        is_rec = True
                    # 获取当前网址的resume_number
                    resume_url = driver.current_url
                    resume_number = re.search(r'resumeNumber=([^&]+)', resume_url).group(1)
                    if resume_number == old_resume_number:
                        # print("当前简历已经是最后一份，跳过处理。")
                        msg += f"\n当前简历已经是最后一份，跳过处理。"
                        try:
                            # 查找并点击关闭按钮
                            close_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH,
                                                            "//div[contains(@class, 'new-shortcut-resume__close')]"))
                            )
                            close_button.click()


                        except Exception as e:
                            print(f"出现错误: {e}")
                        break

                    if (email_exist and is_rec):

                        # 提取姓名、年龄、工作年限、学历和邮箱等
                        name_element = driver.find_element(By.CSS_SELECTOR, '.resume-basic-new__name')
                        name = name_element.text
                        age_element =  driver.find_element(By.CSS_SELECTOR, '.resume-basic-new__meta-item:nth-child(1)')
                        age = age_element.text.split('岁')[0].strip()
                        work_years_element = driver.find_element(By.CSS_SELECTOR,
                                                                 '.resume-basic-new__meta-item:nth-child(2)')
                        education_element = driver.find_element(By.CSS_SELECTOR,
                                                                '.resume-basic-new__meta-item:nth-child(3)')
                        # city_element = driver.find_element(By.CSS_SELECTOR,
                        #                                    '.resume-basic-new__meta-item:nth-child(5)')
                        status_element = driver.find_element(By.CSS_SELECTOR,
                                                             '.resume-basic-new__meta-item:nth-child(4)')

                        # age = age_element.text.split('(')[0].strip()
                        work_years = work_years_element.text.strip()
                        education = education_element.text.strip()
                        email = email_element.text
                        # job_objective = job_objective_element.text.strip()
                        city = ''
                        gender = ''
                        status = status_element.text.strip()

                        mobile = re.sub(r'[^\w\s]', '', email)
                        work_years_match = re.search(r'\d+', work_years)

                        if work_years_match:
                            work_years = int(work_years_match.group())
                        else:
                            work_years = 0

                        # 判断岗位对应什么课程
                        regit_course = get_course(job_title)

                        # 将信息存储到字典中
                        resume_info = {
                            "序号": i + 1,
                            "意向课程": regit_course,
                            "手机": mobile,
                            "校区": job_location,
                            "姓名": name,
                            "性别" : gender,
                            "邮箱": email,
                            "学历": education,
                            "工作年限": work_years,
                            "应聘职位": job_title,
                            "居住地": city,
                            "在职情况": status,
                            "简历编号": resume_number,
                            "来源": "智联"
                        }

                        try:

                            # 将字典添加到列表中
                            resume_info_list.append(resume_info)
                            # 将当前记录写入 QTableWidget
                            import_single_resume_to_table(resume_info, table_widget)
                            # 将当前记录追加到 Excel 文件
                            append_row_to_excel(resume_info, temp_file_path)

                        except Exception as e:
                            print(f"处理第 {i + 1} 份简历时出错: {e}")

                        # 下载简历
                        try:
                            if not clicked_save:
                                # 点击【存至本地】按钮
                                save_to_local_button = driver.find_element(By.XPATH,
                                                                           "//div[@class='resume-button position-r']")
                                save_to_local_button.click()
                                clicked_save = True

                                # 等待模态框出现
                                modal = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH,
                                                                    "//body/div[contains(@class, 'km-modal__wrapper save-resume')]/div[contains(@class, 'km-modal--open')]"))
                                )

                                try:
                                    # 在模态框中查找 footer 元素
                                    footer = modal.find_element(By.XPATH, ".//div[@class='km-modal__footer']")

                                    # 在 footer 中查找保存按钮
                                    save_button = footer.find_element(By.XPATH,
                                                                      './/button[contains(@class, "km-button--primary") and contains(@class, "km-button--filled")]')

                                    save_button.click()
                                    # print(f"-----==已下载{name}的简历！==-----")
                                    msg += f"\n-----==已下载{name}的简历！==-----"
                                    resume_num += 1
                                    # 等待模态框消失
                                    WebDriverWait(driver, 10).until_not(
                                        EC.presence_of_element_located((By.XPATH,
                                                                        "//body/div[contains(@class, 'km-modal__wrapper save-resume')]/div[contains(@class, 'km-modal--open')]"))
                                    )

                                except NoSuchElementException:
                                    # print("模态框内找不到【保存】按钮")
                                    msg += f"\n模态框内找不到【保存】按钮"

                        except NoSuchElementException:
                            # print("找不到【存至本地】按钮")
                            msg += f"\n找不到【存至本地】按钮"

                        except TimeoutException:
                            # print("超时，未找到元素")
                            msg += f"\n超时，未找到元素"

                    i += 1

                except Exception as e:
                    # 如果发生异常
                    # print(f"当前简历项没有邮箱信息，跳过处理。")
                    msg += f"\n-----=={name}没有邮箱信息，跳过处理{str(e)[:50]}==-----"

                finally:
                    # 点击下一份
                    try:
                        right_icon = WebDriverWait(driver, 2).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, "new-shortcut-resume__right")))
                        right_icon.click()
                        old_resume_number = resume_number


                    except:
                        break
    # 将列表转换为 Pandas DataFrame
    df = pd.DataFrame(resume_info_list)
    # print("沟通中简历处理完毕！")
    msg += f"\n沟通中简历处理完毕！共处理{resume_num}条简历。"
    return temp_file_path, msg
