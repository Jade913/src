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


# 判断岗位对应什么模块
def get_course(job_title):
    course_keywords = {
        'FICO': [
            '财务', '会计', '审计', '核算', '应收应付', '账务', '财务分析',
            '费用管理', '成本会计', '记账', '票据管理', '对账', '用友软件',
            '结算', '报税', '初级会计师', '会计从业资格证', '现金管理',
            '资金收付', '报销管理', '往来会计', '财务报表', '成本分析',
            '成本管理', '成本控制', '成本计划', '成本决策', 'fico'
        ],
        'MM': [
            '采购', '物料', '物流', '供应链专员', '仓储', '仓库管理',
            '供应链管理', '库存', '单证', '外贸分析', '物流调度',
            '订单采购', '出入库', '供应商数据库', '采购管理', '物流配送'
        ],
        'SD': [
            '销售', '市场', '商务', '数据分析', '招商', '课程顾问',
            '运营', '店长', '订单管理', '客户管理', '销售管理',
            '供应商', '供应链', '渠道销售', '销售内勤', '助理',
            'ERP', '系统运维', '招标'
        ],
        'PP': [
            '生产计划', '车间', '生产运营', '生产质量', '生产管理',
            '产线', '生产物料', '物料采购', '采购', '仓库', '仓库物料',
            '物料计划', '生产制造', '生产工艺', '工艺流程', '生产统计',
            '生产跟单', '工艺制造', '生产技术', '物料控制', '生产产品',
            '生产设备', '工厂', '生产主管', '生产组长', '生产督导'
        ]
    }

    # 遍历每个模块的关键词
    for course, keywords in course_keywords.items():
        pattern = '|'.join(keywords)
        if re.search(pattern, job_title.lower()):  # 转换为小写进行匹配
            return course

    return '待填写'


def check_work_experience(job_title, work_experience_text):
    """
    检查工作经历是否包含相关关键词
    :param job_title: 应聘职位
    :param work_experience_text: 工作经历文本
    :return: bool 是否符合要求
    """
    # 定义各模块的关键词
    keywords_map = {
        'FICO': [
            '财务', '会计', '审计', '核算', '应收应付', '账务', '财务分析', '费用管理',
            '成本会计', '记账', '票据管理', '对账', '用友软件', '结算', '报税',
            '初级会计师', '会计从业资格证', '现金管理', '资金收付', '报销管理',
            '往来会计', '财务报表', '成本分析', '成本管理', '成本控制', '成本计划', '成本决策'
        ],
        'MM': [
            '采购', '物料', '物流', '供应链专员', '仓储', '仓库管理', '供应链管理',
            '库存', '单证', '外贸分析', '物流调度', '订单采购', '出入库',
            '供应商数据库', '采购管理', '物流配送', '买手', '跟单', '仓库',
            '调度', '供应商'
        ],
        'SD': [
            '销售分析', '销售助理', '销售运营', '销售数据', '销售内勤', '市场分析',
            '市场营销', '销售统计', '销售招投标', '商务专员', '渠道销售', '渠道运营',
            '销售订单管理', '大客户经理', '项目运营', '销售支持', '销售', '市场',
            '商务', '数据分析', '招商', '课程顾问', '运营', '店长', '订单管理',
            '客户管理', '销售管理', '供应商', '供应链', 'ERP', '系统运维', '订单',
            '售前售后', '贸易', '数据', '统计', '商务', '报价', '产品', '业务'
        ],
        'PP': [
            '生产计划', '生产管理', '生产统计', 'pmc管理', '车间主任', '质量管理',
            '供应商管理', '车间', '生产运营', '生产质量', '产线', '生产物料',
            '物料采购', '采购', '仓库', '仓库物料', '物料计划', '生产制造',
            '生产工艺', '工艺流程', '生产跟单', '工艺制造'
        ]
    }

    try:
        # 确定应聘职位属于哪个模块
        module = get_course(job_title)
        if module == '待填写':
            return False

        # 获取该模块的关键词列表
        keywords = keywords_map.get(module, [])

        # 将工作经历文本转为小写进行匹配
        work_text = work_experience_text.lower()

        # 检查是否包含任何关键词
        for keyword in keywords:
            if keyword.lower() in work_text:
                print(f"找到匹配的关键词: {keyword}")
                return True

        print(f"未找到任何匹配的{module}模块关键词")
        return False

    except Exception as e:
        print(f"检查工作经历时出错: {e}")
        return False
