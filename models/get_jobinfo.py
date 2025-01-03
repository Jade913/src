# # -*- coding: utf-8 -*-

import json
import logging
import os
import re
import time
import winsound
from datetime import datetime

import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

from src.utils.selenium_tools import get_course, check_work_experience
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


def click_next_resume(driver, msg, reason=""):
    """
    点击下一份简历
    :param driver: WebDriver实例
    :param msg: 消息字符串
    :param reason: 跳过原因
    :return: bool 是否成功点击
    """
    try:
        if reason:
            print(f"{reason}，跳过处理")
            msg += f"\n-----=={reason}，跳过处理==-----"

        right_icon = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "new-shortcut-resume__right")))
        right_icon.click()
        return True
    except Exception as e:
        print(f"点击下一份简历失败: {e}")
        return False


def check_resume_conditions(driver, job_title):
    """
    检查简历是否满足年龄、统招、工作经历和电话号码要求
    :return: tuple(bool, str, str) (是否满足所有条件, 不满足的原因, 电话号码)
    """
    try:
        # 1.检查年龄
        age_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.resume-basic-new__meta-item:nth-child(1)')))
        age_text = age_element.text.strip()
        age_match = re.search(r'(\d+)岁', age_text)
        if not age_match:
            return False, "无法获取年龄信息", ""
        age = int(age_match.group(1))
        if age < 23 or age > 39:
            return False, f"年龄{age}岁不在23-39岁范围内", ""

        # 2.检查电话号码
        try:
            view_detail_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//div[contains(text(), '查看详情')]]")))
            view_detail_btn.click()

            confirm_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, 
                    "//div[contains(@class, 'get-phone-popover__content--btn')][contains(text(), '确定查看')]")))
            confirm_btn.click()

            phone_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    ".resume-basic-new__contacts--phone .is-ml-20 > div:last-child")))
            phone_number = ''.join(phone_element.text.strip().split())
            
            # 检查电话号码格式
            if not phone_number:
                return False, "电话号码为空", ""
            
            # 移除所有非数字字符（空格、横杠等）
            phone_number = re.sub(r'\D', '', phone_number)
            
            # 验证是否为11位数字
            if not re.match(r'^\d{11}$', phone_number):
                return False, f"电话号码格式不正确: {phone_number}", ""
            
        except Exception as e:
            print(f"获取电话号码失败: {e}")
            return False, "无法获取电话号码", ""

        # 3.检查是否统招
        try:
            education_section = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'resume-section-education-experiences')))
            education_items = education_section.find_elements(By.CLASS_NAME, 'new-education-experiences__item')
            is_rec = False
            for item in education_items:
                date_text = item.find_element(By.CLASS_NAME, 'new-education-experiences__item-time').text
                if ' - ' in date_text:
                    date_range = date_text.split(' - ')
                    start_year, start_month = map(int, date_range[0].split('.'))
                    end_year, end_month = map(int, date_range[1].split('.'))
                    if (end_year - start_year) >= 3 and start_month == 9 and (end_month == 6 or end_month == 7):
                        is_rec = True
                        break
            if not is_rec:
                return False, "非统招生", ""
        except:
            return False, "判断统招状态失败", ""

        # 4.检查工作经历
        try:
            job_titles = driver.find_elements(By.CSS_SELECTOR, ".new-work-experiences__work-job-title")
            titles = [el.get_attribute('title') for el in job_titles]
            
            descriptions = driver.find_elements(By.CSS_SELECTOR, ".new-work-experiences__desc .is-pre-text")
            descs = [el.text for el in descriptions]
            
            skill_tags = driver.find_elements(By.CSS_SELECTOR, ".new-resume-detail-skill-tag span")
            skills = [el.text for el in skill_tags]
            
            work_experience_text = ' '.join(titles + descs + skills)
            
            if not check_work_experience(job_title, work_experience_text):
                return False, "工作经历不符合要求", ""
        except:
            return False, "获取工作经历失败", ""

        return True, "", phone_number

    except Exception as e:
        return False, f"检查条件时出错: {str(e)}", ""


def download_resume(driver, table_widget, selected_campuses=None):
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

    # 筛选联系方式
    contact_selector = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'contact-selector')))
    contact_selector.click()

    by_phone = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//div[@title='有电话' and contains(@class, 'candidate-filter-selector__item-label')]")))
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
                                    "//a[@class='candidate-filter-selector__item km-option km-option--multiple']//div[@class='candidate-filter-selector__item-label'][@title='未加标签的']")
    untag_div.click()

    confirm_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//div[@class='candidate-filter-selector__footer']//button[@class='km-button km-control km-ripple-off km-button--primary km-button--filled is-mini']")))
    confirm_button.click()

    # 点击 job-selector 以显示选项
    job_selector = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'job-selector')))
    job_selector.click()

    # 使用选中的校区列表自动处理
    # if selected_campuses:
    #     for campus in selected_campuses:
    #         try:
    #             # 等待并点击搜索框
    #             search_input = WebDriverWait(driver, 10).until(
    #                 EC.presence_of_element_located((By.CLASS_NAME, 'search-input')))
    #             search_input.clear()
    #             search_input.send_keys(campus)
    #
    #             # 等待并点击搜索结果
    #             search_result = WebDriverWait(driver, 10).until(
    #                 EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{campus}')]")))
    #             search_result.click()
    #
    #             time.sleep(1)  # 短暂等待以确保选择生效
    #         except Exception as e:
    #             print(f"处理校区 {campus} 时出错: {e}")
    #             continue
    # else:
    #     # 如果没有选中的校区
    #     print("未选择校区，从头处理！")

    # 5.31写入 12.31注释
    # 定位滚动容器
    # wrap = driver.find_element(By.XPATH,
    #                            "//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']")

    # # # 定义一个函数来滚动容器
    # try:
    #     # popper = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,"//div[@class='km-popover km-select__dropdown-wrapper job-selector-popper']")))
    #     wrap2 = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,
    #                                         "//div[@class='km-popover km-select__dropdown-wrapper job-selector-popper']//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']")))

    #     ActionChains(driver).move_to_element(wrap2).perform()
    #     # 向下滚动20次，每次滚动一定的像素值（例如100px）
    #     for _ in range(20):
    #         driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 100;", wrap2)
    #         time.sleep(0.5)

    #     print("已经滚动到容器底部!")
    #     # 确保容器高度不是0
    #     # wrap_height = driver.execute_script("return arguments[0].offsetHeight;", wrap)
    #     # if wrap_height == 0:
    #     #     print("容器高度为0，可能没有内容或样式问题。")
    #     # else:
    #     #     # 尝试滚动到容器底部
    #     #     last_scroll_top = 0
    #     #     while True:
    #     #         driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", wrap)
    #     #         time.sleep(1)  # 等待是为了观察效果，但在实际测试中可能需要更复杂的逻辑
    #     #
    #     #         new_scroll_top = driver.execute_script("return arguments[0].scrollTop;", wrap)
    #     #         if new_scroll_top == last_scroll_top:
    #     #             break  # 如果没有新的滚动发生，则退出循环
    #     #         last_scroll_top = new_scroll_top
    # except Exception as e:
    #     print(f"{e}---请手动滚动岗位列表到底部!---")
    #     # countdown(10)

    # # 滚动到容器底部以确保加载所有选项
    # # 获取所有选项元素
    # options = driver.find_elements(By.XPATH,
    #                                "//div[@class='km-popover__inner']//div[@class='km-select__dropdown']//div[@class='km-scrollbar']//div[@class='km-scrollbar__wrap']//div[@class='km-scrollbar__view']//div[@class='km-select__options']//a[@class='job-selector__item km-option']")

    resume_num = 0
    temp_file_path = generate_filename('抓取数据_临时')
    # 初始化临时 Excel 文件
    init_excel_file(temp_file_path)

    # 初始化当前索引变量
    current_index = 0

    # 用户选中的校区列表依次输入进输入框，然后滚动岗位列表，获取岗位列表，然后处理岗位列表的每个岗位下的简历
    try:
        resume_info_list = []
        if selected_campuses:
            for campus in selected_campuses:
                msg += f"\n开始处理校区：{campus}"
                # 在职位名称/发布地输入框中输入校区名称
                search_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "//div[contains(@class, 'km-select__search-input')]//input[@class='km-input__original is-normal']")))

                # 清除输入框中的内容
                search_input.send_keys(Keys.CONTROL + "a")
                search_input.send_keys(Keys.DELETE)
                time.sleep(0.2)

                if search_input.get_attribute('value'):
                    search_input.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
                    time.sleep(0.2)

                # 输入新的校区
                search_input.send_keys(campus)
                time.sleep(0.5)

                # 定位并滚动容器
                try:
                    scroll_container = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "//div[@class='km-popover km-select__dropdown-wrapper job-selector-popper']//div[@class='km-scrollbar__wrap']")))

                    # 移动到容器并滚动
                    ActionChains(driver).move_to_element(scroll_container).perform()
                    print(f"开始滚动获取{campus}的岗位列表...")

                    # 等待选项容器加载
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "km-select__options")))

                    # 获取该校区所有岗位
                    job_options = driver.find_elements(By.CSS_SELECTOR,
                                                       ".km-select__options > a.job-selector__item:not(:empty)")

                    # 打印当前获取到的所有岗位
                    print("\n当前获取到的岗位列表：")
                    for idx, opt in enumerate(job_options, 1):
                        try:
                            title = opt.find_element(By.CSS_SELECTOR, ".job-selector__item-title").get_attribute(
                                'title')
                            city = opt.find_element(By.CLASS_NAME, "job-selector__item-city").text.strip()
                            is_offline = "已下线" if len(
                                opt.find_elements(By.CLASS_NAME, "job-selector__item-tag")) > 0 else "在线"
                            print(f"[{idx}] {title} - {city} ({is_offline})")
                        except Exception as e:
                            print(f"[{idx}] 获取岗位信息失败: {str(e)}")

                    print(f"\n获取到{campus}的岗位列表，共{len(job_options)}个岗位，开始处理各个岗位...")

                    # 遍历处理每个岗位
                    for index, option in enumerate(job_options, 1):
                        try:
                            # 获取岗位标题
                            title_element = option.find_element(By.CSS_SELECTOR, ".job-selector__item-title")
                            job_title = title_element.get_attribute('title')

                            # 跳过"不限"选项
                            if job_title == '不限':
                                print(f"跳过'不限'选项")
                                continue

                            # 检查是否已下线
                            # try:
                            #     option.find_element(By.CLASS_NAME, "job-selector__item-tag")
                            #     print(f"跳过已下线岗位 [{index}/{len(job_options)}]: {job_title}")
                            #     continue
                            # except:
                            #     pass

                            # 获取城市信息并验证是否匹配当前校区
                            city_element = option.find_element(By.CLASS_NAME, "job-selector__item-city")
                            job_location = city_element.text.strip()

                            if campus not in job_location:
                                print(
                                    f"跳过不匹配校区的岗位 [{index}/{len(job_options)}]: {job_title} - {job_location}")
                                continue

                            print(f"\n正在处理岗位 [{index}/{len(job_options)}]: {job_title}, 地点: {job_location}")
                            msg += f"\n当前职位：{job_title}，职位地点：{job_location}"

                            # 点击选择该岗位
                            option.click()
                            time.sleep(1)  # 等待点击生效

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
                                    # 检查所有条件
                                    conditions_met, reason, phone_number = check_resume_conditions(driver, job_title)
                                    
                                    if not conditions_met:
                                        if not click_next_resume(driver, msg, reason):
                                            break
                                        continue

                                    # 获取简历编号
                                    resume_url = driver.current_url
                                    resume_number = re.search(r'resumeNumber=([^&]+)', resume_url).group(1)

                                    if resume_number == old_resume_number:
                                        msg += f"\n当前简历已经是最后一份，跳过处理。"
                                        try:
                                            close_button = WebDriverWait(driver, 10).until(
                                                EC.element_to_be_clickable((By.XPATH,
                                                                            "//div[contains(@class, 'new-shortcut-resume__close')]")))
                                            close_button.click()
                                        except Exception as e:
                                            print(f"关闭简历时出错: {e}")
                                        break

                                    # 提取简历信息
                                    name = driver.find_element(By.CSS_SELECTOR, '.resume-basic-new__name').text
                                    work_years = driver.find_element(By.CSS_SELECTOR,
                                                                     '.resume-basic-new__meta-item:nth-child(2)').text.strip()
                                    education = driver.find_element(By.CSS_SELECTOR,
                                                                    '.resume-basic-new__meta-item:nth-child(3)').text.strip()
                                    status = driver.find_element(By.CSS_SELECTOR,
                                                                 '.resume-basic-new__meta-item:nth-child(4)').text.strip()
                                    email = driver.find_element(By.CSS_SELECTOR,
                                                                '.resume-basic-new__email .is-ml-4').text

                                    # 处理数据
                                    work_years_match = re.search(r'\d+', work_years)
                                    work_years = int(work_years_match.group()) if work_years_match else 0
                                    regit_course = get_course(job_title)

                                    # 创建简历信息字典
                                    resume_info = {
                                        "序号": resume_num + 1,
                                        "意向课程": regit_course,
                                        "手机": phone_number,
                                        "校区": job_location,
                                        "姓名": name,
                                        "性别": "",
                                        "邮箱": email,
                                        "学历": education,
                                        "工作年限": work_years,
                                        "应聘职位": job_title,
                                        "居住地": "",
                                        "在职情况": status,
                                        "简历编号": resume_number,
                                        "来源": "智联"
                                    }

                                    # 保存简历信息
                                    resume_info_list.append(resume_info)
                                    import_single_resume_to_table(resume_info, table_widget)
                                    append_row_to_excel(resume_info, temp_file_path)

                                    # 下载简历
                                    if not clicked_save:
                                        save_to_local_button = driver.find_element(By.XPATH,
                                                                                   "//div[@class='resume-button position-r']")
                                        save_to_local_button.click()
                                        clicked_save = True

                                        modal = WebDriverWait(driver, 10).until(
                                            EC.presence_of_element_located((By.XPATH,
                                                                            "//body/div[contains(@class, 'km-modal__wrapper save-resume')]/div[contains(@class, 'km-modal--open')]")))

                                        try:
                                            footer = modal.find_element(By.XPATH, ".//div[@class='km-modal__footer']")
                                            save_button = footer.find_element(By.XPATH,
                                                                              './/button[contains(@class, "km-button--primary")]')
                                            save_button.click()
                                            msg += f"\n-----==已下载{name}的简历！==-----"
                                            resume_num += 1

                                            WebDriverWait(driver, 10).until_not(
                                                EC.presence_of_element_located((By.XPATH,
                                                                                "//body/div[contains(@class, 'km-modal__wrapper save-resume')]/div[contains(@class, 'km-modal--open')]")))
                                        except:
                                            msg += f"\n模态框内找不到【保存】按钮"

                                    old_resume_number = resume_number

                                    # 处理完成后点击下一份
                                    if not click_next_resume(driver, msg):
                                        break

                                except Exception as e:
                                    print(f"处理简历时出错: {e}")
                                    if not click_next_resume(driver, msg, "处理出错"):
                                        break

                        except Exception as e:
                            print(f"处理岗位时出错 [{index}/{len(job_options)}]: {str(e)}")
                            continue

                    print(f"\n========== {campus}校区所有岗位处理完成，共处理{len(job_options)}个岗位 ==========\n")
                    df_temp = pd.DataFrame(resume_info_list)
                    df_temp.to_excel(f"temp_{campus}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", index=False)

                except Exception as e:
                    print(f"处理{campus}校区时出错: {e}")
                    continue


    except Exception as e:
        print(f"出错: {e}")
