# # -*- coding: utf-8 -*-

from datetime import datetime
import os
import shutil
import zipfile
import re
from src.utils.kltrpa_path import download_path


def clean_job_title(job_title):
    # 移除括号和其中的内容，以及特殊字符
    cleaned_title = re.sub(r'\（.*?\）|\(.*?\)|[^\w\s]', '', job_title)
    # 移除多余的空格
    cleaned_title = re.sub(r'\s+', '', cleaned_title)
    return cleaned_title

def matches_filename(filename, name, job_title):
    # 移除文件名中的下划线和文件后缀，转为字符串
    cleaned_filename = filename.replace('_', '').replace('.pdf', '').replace('.docx', '')

    # 移除名字中的空格
    cleaned_name = name.replace(' ', '')

    # 清理职位标题
    cleaned_job_title = clean_job_title(job_title)

    # 检查文件名是否包含名字和清理过的职位标题
    return cleaned_name in cleaned_filename and cleaned_job_title in cleaned_filename

def move_picked_resume(self):
    selected_rows = set()
    for idx in self.omo_table.selectedIndexes():
        selected_rows.add(idx.row())

    if selected_rows:

        # 构建picked文件夹路径
        now = datetime.now()
        # folder_name = f"picked_{now.strftime('%Y%m%d%H%M')}"
        # picked_dir = os.path.join(download_path, folder_name)
        # os.makedirs(picked_dir, exist_ok=True)

        # 使用 ZipFile 对象创建一个新的 ZIP 文件
        output_zip = os.path.join(download_path, f"picked_{now.strftime('%Y%m%d%H%M')}_简历打包.zip")
        file_count = 0
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 查找符合条件的简历文件
            for row in selected_rows:
                name = self.omo_table.item(row, 5).text()  # 第6列为姓名
                job = self.omo_table.item(row, 10).text()  # 岗位
                for filename in os.listdir(download_path):
                    if matches_filename(filename, name, job):  # if filename.startswith(f"{name}_"):

                        resume_path = os.path.join(download_path, filename)
                        # 将文件添加到 ZIP 文件
                        zipf.write(resume_path, arcname=os.path.relpath(resume_path, download_path))
                        file_count += 1
                        # shutil.move(resume_path, picked_dir)
        if file_count > 0:
            msg = f'选择简历已成功打包至{output_zip}！'
        else:
            msg = '没有找到任何简历！'

    else:
        # QMessageBox.warning(self, "警告", "请至少选择一行！")
        msg = False
    return msg
