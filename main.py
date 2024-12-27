# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, \
    QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QMessageBox, QCheckBox, QTextEdit, QDialog, QTableWidget,QFileDialog, \
    QTableWidgetItem, QAbstractItemView, QGridLayout
from PyQt5.QtCore import QSettings, QProcess, pyqtSlot

from src.utils.security import encrypt_string, decrypt_string
from src.utils.tabledata import export_table_to_excel, import_table_from_excel,\
     open_file_with_program, generate_filename, update_omo_from_table, import_pdata_to_table
from src.utils.omo_integrate import OmoIntegrate
from src.utils.log import get_logger
from src.utils.selenium_tools import get_driver

from src.views.Ui_loginwindow import Ui_login_window
from src.views.Ui_mainwindow import Ui_mainwindow

from src.models.login import test_login
from src.models.say_hi import say_hi
from src.models.deal_new_greet import deal_new_greet
from src.models.get_jobinfo import download_resume
from src.models.move_picked_resume import move_picked_resume


class LoginWindow(QMainWindow, Ui_login_window):
    """
    登录窗口类
    """
    def __init__(self):
          super().__init__()  # 使用超类，继承父类的属性及方法\n
          self.setupUi(self)  # 构造窗体界面
          self.initUI()

    def initUI(self):
        self.load_settings()
        # self.login_button.clicked.connect(self.login)

    @pyqtSlot()
    def on_login_button_clicked(self):  # 利用QT自带槽函数直接连接按钮
        self.login()
    def load_settings(self):
        # 使用QSettings加载上次保存的账号和密码
        settings = QSettings('config.ini', QSettings.IniFormat)
        settings.beginGroup('LoginInfo')
        username = settings.value('username', '')
        password = decrypt_string(settings.value('password', ''))
        server = settings.value('server', 'odoo14.kelote.com')
        db = settings.value('db', 'klt_hr')
        remember = settings.value('remember', False, type=bool)
        settings.endGroup()

        # 将加载的数据显示在界面上
        self.username_edit.setText(username)
        self.password_edit.setText(password)
        self.server_edit.setText(server)
        self.db_edit.setText(db)
        self.remember_checkbox.setChecked(remember)

    def save_settings(self):
        # 将账号和密码保存到配置文件中
        settings = QSettings('config.ini', QSettings.IniFormat)
        settings.beginGroup('LoginInfo')
        settings.setValue('username', self.username_edit.text())
        settings.setValue('password', encrypt_string(self.password_edit.text()))
        settings.setValue('server', self.server_edit.text())
        settings.setValue('db', self.db_edit.text())
        settings.setValue('remember', self.remember_checkbox.isChecked())
        settings.endGroup()

    def login(self):
        # 获取用户名和密码
        username = self.username_edit.text()
        password = self.password_edit.text()
        server = self.server_edit.text()
        db = self.db_edit.text()
        remember = self.remember_checkbox.isChecked()

        omo_integrate = OmoIntegrate(server, db, username, password)
        uid = omo_integrate.login()
        if uid:
            print("登录成功.")
            if remember:
                # 如果勾选了记住账号和密码，则保存到配置文件中
                self.save_settings()
            # 登录成功后打开RPA招聘界面
            self.rpa_window = RPAWindow(omo_integrate)
            self.rpa_window.show()
            self.hide()  # 隐藏登录界面
        else:
            print("登录失败.")
            QMessageBox.warning(self, '警告', '登录失败!')


class RPAWindow(QMainWindow, Ui_mainwindow):
    """
    RPA招聘数据处理
    """
    def __init__(self, omo_integrate):
        super().__init__()
        self.setupUi(self)
        self.selected_campuses = []
        self.init_campus_selection()
        self.initUI(omo_integrate)
        self.logger = get_logger(self.log_textedit)

    def init_campus_selection(self):
        # 校区列表
        campuses = ["重庆", "杭州", "厦门", "广州", "北京", "天津", "郑州", 
                   "山西", "济南", "武汉", "南宁", "中山", "佛山", "深圳", 
                   "潍坊", "淄博", "苏州", "天津", "青岛", "上海", "西安", 
                   "长沙", "长春", "合肥", "南京", "成都", "东莞", "河北"]
        
        # 创建网格布局
        layout = QGridLayout()
        
        # 动态创建复选框并添加到布局
        for i, campus in enumerate(campuses):
            checkbox = QCheckBox(campus)
            checkbox.stateChanged.connect(self.on_campus_selected)
            layout.addWidget(checkbox, i // 6, i % 6)  # 每行6个
            
        # 设置布局到GroupBox
        self.campus_group.setLayout(layout)

    def on_campus_selected(self):
        self.selected_campuses = [
            checkbox.text() 
            for checkbox in self.campus_group.findChildren(QCheckBox) 
            if checkbox.isChecked()
        ]

    def initUI(self, omo_integrate):
        self.tabWidget.setCurrentIndex(2)
        self.update_omo_button.clicked.connect(lambda: self.update_omo(omo_integrate))

    @pyqtSlot()
    def on_connect_zhilian_button_clicked(self):
        login = test_login()
        if login:
            msg="智联连接成功"
        else:
            msg="智联连接失败，请确保已登录后重新连接"
        self.logger.info(msg)

    @pyqtSlot()
    def on_fetch_info_button_clicked(self):
        self.tabWidget.setCurrentIndex(0)

        driver = get_driver()

        try:

          # 处理打招呼
          # msg = say_hi(driver)
          # self.logger.info(msg)

          # 处理可以聊
          msg = deal_new_greet(driver)
          self.logger.info(msg)

        except:
          msg += "处理新招呼失败"

        try:

          # 从智联获得的数据在tablewidget中显示
          # pdata = get_from_zhilian()
          temp_file_path, msg = download_resume(driver, self.fetch_table)
          driver.close()
          # import_pdata_to_table(pdata, self.fetch_table)
          # 输出最终的 Excel 文件
          try:
              final_file_path = generate_filename('抓取数据')
              os.rename(temp_file_path, final_file_path)
              import_table_from_excel(self.fetch_table, final_file_path)
              open_file_with_program(final_file_path)
              msg += f'数据已输出到目录下,{final_file_path}'
          except:
              import_table_from_excel(self.fetch_table, temp_file_path)
              open_file_with_program(temp_file_path)
              msg += f'数据已输出到目录下,{temp_file_path}'
          # 输出table的数据到excel
          # file_path = generate_filename('抓取数据')
          # export_table_to_excel(self.fetch_table, file_path)
          # open_file_with_program(file_path)


          self.logger.info(msg)

        except Exception as e:
          msg += f"出错了:{e}"

          if temp_file_path:
              import_table_from_excel(self.fetch_table, temp_file_path)
              open_file_with_program(temp_file_path)
              msg += f'数据已输出到目录下,{temp_file_path}'
          else:
              QMessageBox.warning(self, '警告', f'出错了!没有抓取到信息！{e}')


    @pyqtSlot()
    def on_open_excel_button_clicked(self):
        # 打开文件对话框，让用户选择Excel文件
        file_path, _ = QFileDialog.getOpenFileName(self,
                        '打开Excel文件', '', 'Excel Files (*.xlsx *.xls *.xlsm)')
        import_table_from_excel(self.omo_table, file_path)

        msg = f'数据已从{file_path}读取成功'
        self.logger.info(msg)

    @pyqtSlot()
    def on_batch_download_button_clicked(self):
        msg = move_picked_resume(self)
        if msg:
            self.logger.info(msg)
            QMessageBox.information(self,'提示', f'{msg}')
        else:
            msg = "请至少选择一行！"
            self.logger.info(msg)
            QMessageBox.warning(self, "警告", msg)

    def update_omo(self, omo_integrate):
      try:
        if self.omo_table.columnCount() != 0:
          # 添加新的一列并设置标题
          if self.omo_table.horizontalHeaderItem(0).text() != '执行结果':
            self.omo_table.insertColumn(0)
            header_item = QTableWidgetItem("执行结果")
            self.omo_table.setHorizontalHeaderItem(0, header_item)

          update_omo_from_table(omo_integrate, self.omo_table)
          self.omo_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
          # 输出table的数据到excel
          file_path = generate_filename('OMO更新日志')
          export_table_to_excel(self.omo_table, file_path)
          msg_type = 'info'
          qbox_type = 'information'
          msg = f'已完成更新，请检查结果，同时结果已写入到文件\t{file_path}'
        else:
          msg_type = 'warning'
          qbox_type = 'warn'
          msg = f'请先打开文件'
      except Exception as e:
        msg_type = 'error'
        qbox_type = 'critical'
        msg = f'执行出现错误{str(e)[:50]}'
      getattr(self.logger, msg_type)(msg)
      getattr(QMessageBox, qbox_type)(self, '更新结果', msg)


class KltRpaApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.window = LoginWindow()
        self.window.show()  # 显示窗口


if __name__ == '__main__':
    app = KltRpaApp()
    sys.exit(app.exec_())

