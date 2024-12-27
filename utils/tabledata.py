# -*- coding: utf-8 -*-

import pandas as pd
import os
import sys
import subprocess
from PyQt5.QtWidgets import QTableWidgetItem,QHeaderView

from .kltrpa_path import tabledata_path

CUOSTOMER_INFO_FIELD = {
    "序号": "row_no",
    "简历编号": "resumeNumber",
    "意向课程": "regit_course",
    "手机": "mobile_phone",
    "校区": "campus_id",
    "姓名": "name",
    "性别": "gender",
    # "年龄": "age",
    "邮箱": "email",
    "学历": "degree",
    "工作年限": "work_life",
    "应聘职位": "job_objective",
    "居住地": "domicile",
    "在职情况": "description",
    "来源": "source",
}



def export_pdata_from_table(table_widget):
    """
    从QTableWidget导出数据到DataFrame
    :param table_widget: QTableWidget对象
    :return: DataFrame对象
    """
    # 获取表头信息
    column_headers = [table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount())]
    # 初始化一个带有表头的DataFrame
    data_df = pd.DataFrame(columns=column_headers)

    # 获取表格的行数和列数（不包括表头）
    row_count = table_widget.rowCount()
    column_count = table_widget.columnCount()

    # 遍历表格的每个单元格
    for i in range(row_count):
        row_data = []
        for j in range(column_count):
            item = table_widget.item(i, j)
            if item is not None:
                # 将QTableWidgetItem的文本转换为字符串并添加到列表中
                row_data.append(item.text())
            else:
                row_data.append('')  # 如果单元格为空，则添加None
         # 创建一行数据并添加到DataFrame
        data_df.loc[i] = row_data

    # # 获得垂直表头并合并df
    # vertical_header_texts = [table_widget.verticalHeaderItem(i).text() for i in range(table_widget.rowCount())]
    # header_df = pd.DataFrame(vertical_header_texts, columns=['序号'])
    # merged_df = pd.concat([header_df, data_df], axis=1)

    return data_df


def import_single_resume_to_table(resume_info, table_widget):
  """
  将单条简历信息导入到 QTableWidget
  :param resume_info: 字典类型的简历信息
  :param table_widget: QTableWidget对象
  :return: None
  """
  row_count = table_widget.rowCount()
  table_widget.insertRow(row_count)

  for j, (key, value) in enumerate(resume_info.items()):
    text = str(value) if value else ''
    item = QTableWidgetItem(text)
    table_widget.setItem(row_count, j, item)

def init_excel_file(file_path):
  """
  初始化一个空的 Excel 文件，准备写入数据
  :param file_path: Excel 文件路径
  :return: None
  """
  df = pd.DataFrame(
    columns=["序号", "意向课程", "手机", "校区", "姓名", "性别", "邮箱", "学历", "工作年限", "应聘职位", "居住地",
             "在职情况", "简历编号", "来源"])
  df.to_excel(file_path, index=False)


def append_row_to_excel(resume_info, file_path):
  """
  将一条简历信息追加到 Excel 文件
  :param resume_info: 字典类型的简历信息
  :param file_path: Excel 文件路径
  :return: None
  """
  df = pd.DataFrame([resume_info])
  with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
    df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)


def import_pdata_to_table(pdata, table_widget):
    """
    将DataFrame导入到QTableWidget
    :param pdata: DataFrame对象
    :param table_widget: QTableWidget对象
    :return: None
    """
    # 清空现有表格数据
    table_widget.clear()
    # 第1列用作行索引
    # data = pdata.iloc[:, 1:]
    data = pdata
    # 获取数据行数和列数
    row_count = len(data)
    col_count = len(data.columns)

    # 初始化QTableWidget
    table_widget.setRowCount(row_count)
    table_widget.setColumnCount(col_count)

    # 设置水平表头（列标题）
    table_widget.setHorizontalHeaderLabels(data.columns)

    # 将数据填充到QTableWidget
    for i in range(row_count):
        for j in range(col_count):
            text = str(data.iloc[i, j]) if not pd.isna(data.iloc[i, j]) else ''
            # if pd.isna(text):
            #     text = ''
            item = QTableWidgetItem(text)
            table_widget.setItem(i, j, item)
        # # 设置第1列为行索引，需要前面data中不要用第1列序号列，pdata.iloc[:, 1:]
        # item = QTableWidgetItem(str(pdata.iloc[i, 0]))
        # table_widget.setVerticalHeaderItem(i, item)

    # # 自适应列宽
    # table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)



def import_table_from_excel(table_widget, excel_file):
    """
    从Excel文件导入数据到QTableWidget
    :param table_widget: QTableWidget对象
    :param excel_file: Excel文件路径
    :return: None
    """
    try:
        # 读取Excel文件
        excel_data = pd.read_excel(excel_file, engine='openpyxl')
        import_pdata_to_table(excel_data, table_widget)

        print(f"数据加载完成 {os.path.basename(excel_file)}")
    except Exception as e:
        print(f"数据加载出错: {str(e)}")

def export_table_to_excel(table_widget, filename):
    """
    将QTableWidget中的数据导出到Excel文件
    :param table_widget: QTableWidget对象
    :param filename: Excel文件路径
    :return: None
    """
    df = export_pdata_from_table(table_widget)
    df.to_excel(filename, index=False)
    df.to_excel(filename.replace('抓取数据','source'), index=False)

def open_file_with_program(file_path):
    if sys.platform.startswith('win'):
        os.startfile(file_path)
    elif sys.platform == 'darwin':
        subprocess.call(['open', file_path])
    else:
        try:
            subprocess.call(['xdg-open', file_path])
        except FileNotFoundError:
            print("No default application found to open the file.")

def generate_filename(fname):
    """
    生成唯一的文件名，确保文件名不重复
    :return: 唯一的文件名
    """
    timestamp = pd.Timestamp.now().strftime('%Y%m%d%H%M%S')
    target_folder = tabledata_path

    # 如果文件夹不存在，创建它
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 生成文件名和保存文件
    filename = os.path.join(target_folder, f'{ timestamp }-{fname}.xlsx')
    return filename

def update_omo_from_table(omo_integrate, table_widget):
    """
    使用tablewidget中的数据更新 OMO
    """
    column_count = table_widget.columnCount()
    header_labels = [table_widget.horizontalHeaderItem(column).text() for column in range(column_count)]
    for row in range(table_widget.rowCount()):
        row_data = {}
        for column in range(column_count):
            item = table_widget.item(row, column)
            if header_labels[column] in CUOSTOMER_INFO_FIELD:
                if item is not None:
                    row_data[CUOSTOMER_INFO_FIELD[header_labels[column]]] = item.text()
                else:
                    row_data[CUOSTOMER_INFO_FIELD[header_labels[column]]] = ""
        res_info = omo_integrate.export_customer_data(row_data)
        # 将执行结果写入单元格
        result_item = QTableWidgetItem(f"{res_info['msg_type']}{res_info['msg']}")
        table_widget.setItem(row, 0, result_item)
