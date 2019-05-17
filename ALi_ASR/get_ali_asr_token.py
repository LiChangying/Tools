# -*- coding: utf8 -*-
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
import ruamel.yaml as yaml

#function : 响应数据接送格式转换
#input : str,需要转换的数据
#output : json，转换后的数据，json格式
def str_trans_json(str):
    response_data = json.loads(str)          #将已编码的 JSON 字符串解码为 Python 对象
    json_data = json.dumps(response_data, ensure_ascii=False, encoding='utf-8')   #将 Python 对象编码成 JSON 字符串
    unicode_data = yaml.safe_load(json_data)
    return unicode_data

# 创建AcsClient实例
client = AcsClient(
   "LTAIIZOIsILn3aXy",
   "ZxSb5vWDH4hkzRkXbm1B2rGf6HKXVJ",
   "cn-shanghai"
);
# 创建request，并设置参数
request = CommonRequest()
request.set_method('POST')
request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
request.set_version('2019-02-28')
request.set_action_name('CreateToken')
response = client.do_action_with_exception(request)
response = str_trans_json(response)
Token = response['Token']
Token_ID = Token['Id']
with open("token_id.txt",'w') as f:
    f.write(Token_ID)