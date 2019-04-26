#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import time
import random
import md5
import json
import base64
import ruamel.yaml as yaml
import cv2
import numpy
import os
from PIL import Image, ImageDraw, ImageFont
import hashlib

# 您的应用ID
appKey = "zhudytest123"
# appKey = '5e2e98c41178e554'
# 您的应用密钥，请勿把它和appKey泄露给他人
# appSecret = "youdaoapiv120171"
appSecret = "%29jqQ#2n2&]zad(ta9)"
ocr_url_para = 'http://ocrtran.youdao.com/ocr/tranocr?' \
               'keyfrom=fanyi.3.11.6.android&' \
               'imei=imei&' \
               'userId=user&' \
               'type=composite&' \
               'clientele=fanyiguan&'

client = "fanyiguan"
secret_key = "%29jqQ#2n2&]zad(ta9)"
default_input_info_count = 10
current_milli_time = lambda: int(round(time.time() * 1000))

# function:MD5签名
# input:str    要经MD5的字符串
# output:str    返回MD5的前32位
def data_md5(str):
    m = md5.new()
    m.update(str.encode(encoding='utf-8'))
    return m.hexdigest()

def get_result(imgfile):
    print(imgfile)
    img = open(imgfile.strip()).read()
    imgb64= base64.b64encode(img)
    # 源语言
    fromLan = "auto"
    # 目标语言
    toLan = "zh-CHS"
    # 预定义客户端身份标识  翻译官 ： fanyiguan
    clientele = 'fanyiguan'
    # 产品名称.三位版本号.平台
    keyfrom = 'fanyi.3.11.6.android'
    # 用户身份标识----选填
    imei = 'imei'
    # 上传类型----选填
    type = "composite"
    # 随机数，自己随机生成，建议时间戳
    salt = str(int(time.time() * 1000))
    # 签名
    # sign是加密结果，加密规则为：clientele的取值 + input信息 + salt(随机数) + 私钥 ==> 取md5的值
    # 其中input信息为 input前10个字符 + input长度 + input后十个字符（当input长度大于20）或 input字符串（当input长度小于等于20） （其中input为图片进行BASE64编码以后生成的字符串）
    input = ''
    if len(imgb64) > 20:
        input = imgb64[0:10] + str(len(imgb64)) + imgb64[len(imgb64) - 10:]
    else:
        input = imgb64
    sign = clientele + input + str(salt) + appSecret
    sign = data_md5(sign)
    #编辑URL
    ocr_url = ocr_url_para + "&salt=" + salt + "&sign=" + sign + "&from=" + fromLan + "&to=" + toLan
    # return ocr_url
    response = requests.post(
        url=ocr_url,
        data=imgb64
    )
    return response.text

def get_info(image_base64, input_info_count):
    input_info = bytearray()
    if input is not None:
        input_length = len(image_base64)
        if input_length > input_info_count * 2:
            input_info = image_base64[:input_info_count] + str(input_length).encode() + image_base64[
                                                                                        input_length - input_info_count:]
        else:
            input_info = image_base64

    return input_info

def get_ocr_result_base64(image_base64, lang_from, lang_to, ocr_url=ocr_url_para):
    ocr_url = generate_url(image_base64, lang_from, lang_to, ocr_url)
    print(ocr_url)

    response = requests.post(
        url=ocr_url,
        data=image_base64
    )
    print "response"
    return response.json()

def generate_url(image_base64, lang_from, lang_to, ocr_url):
    input_info = get_info(image_base64, default_input_info_count)
    salt = str(current_milli_time())
    sign = generate_sign(client, input_info, salt, secret_key)
    print(sign)

    uurl =  ocr_url + "&salt=" + salt + "&sign=" + sign + "&from=" + lang_from + "&to=" + lang_to
    return uurl

def generate_sign(client, input_info, salt, secret_key):
    md5bytes = client.encode('utf-8') + input_info + salt.encode('utf-8') + secret_key.encode('utf-8')
    return hashlib.md5(md5bytes).hexdigest()

print get_ocr_result_base64(r'C:\Users\lichangying\Desktop\test.png','en','zh-CHS')