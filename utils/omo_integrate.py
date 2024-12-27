# -*- coding: utf-8 -*-

import xmlrpc.client

class OmoIntegrate():
    def __init__(self, server, db, username, password):
        self.db = db
        self.username = username
        self.password = password
        self.rpc_url = f'https://{server}/xmlrpc/2' 
        self.uid = None   
    def login(self):
        # 指定服务器作为连接
        common = xmlrpc.client.ServerProxy(f'{self.rpc_url}/common')
        # 登录验证
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        if self.uid:
            return True
        else:
            return None
    
    def export_customer_data(self, customer_dict):
        if 'row_no' in customer_dict:
            row_no = customer_dict['row_no']
            del customer_dict['row_no']
        if 'resumeNumber' in customer_dict:
            del customer_dict['resumeNumber'] 

        models = xmlrpc.client.ServerProxy(f'{self.rpc_url}/object')
        customer_result = models.execute_kw(self.db, self.uid, self.password, 
                            'kltcrm.import.customer', 'create_customer',
                            [
                            row_no,
                            customer_dict
                            ],
                            )
        return customer_result


# if __name__ == '__main__':
#     server = 'odoo14.kelote.com'
#     db = 'klt_hr'
#     username = 'demo'
#     password = 'demo'

#     omo_integrate = OmoIntegrate(server, db, username, password)
#     uid = omo_integrate.login()
#     if uid:
#         print("Authentication successuccessful.")
#         customer_dict = {'row_no':1,
#                         'campus_id':'南京',
#                         'regit_course': '业务模块',
#                         'mobile_phone': '54321',
#                         'name': '45678',
#                         'email': 'abcde@qq.com'}
#         result = omo_integrate.export_customer_data(customer_dict)
#         print(result)

#     else:
#         print("Authentication failed.")



    