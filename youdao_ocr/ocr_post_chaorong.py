import base64
import hashlib
import time
import sys
import json

import requests

client = "aicloud"
secret_key = "X#vNewsd(WUJ$yKT[nik"

#ocr_url_para = 'http://huawei.youdao.com/ocr/tranocr?keyfrom=keyfrom&imei=imei&clientele=' + client
#ocr_url_para = 'http://ns015x.corp.youdao.com:5304/ocr/tranocr?keyfrom=keyfrom&imei=imei&appKey=5e2e98c41178e554&clientele=' + client
#ocr_url_para = 'http://ns015x.corp.youdao.com:5304/ocr/tranocr?keyfrom=youdaotest&imei=imei&clientele=' + client
ocr_url_para = 'http://13.231.242.202:2304/ocr/tranocr?keyfrom=keyfrom&imei=imei&appKey=5e2e98c41178e554&clientele=' + client

default_input_info_count = 10
current_milli_time = lambda: int(round(time.time() * 1000))

def generate_url(image_base64, lang_from, lang_to, ocr_url):
    input_info = get_info(image_base64, default_input_info_count)
    #salt = "1540539471"#str(current_milli_time())
    salt = str(current_milli_time())
    sign = generate_sign(client, input_info, salt, secret_key)
    print(sign)

    uurl =  ocr_url + "&salt=" + salt + "&sign=" + sign + "&from=" + lang_from + "&to=" + lang_to
    return uurl

def get_ocr_result_base64(image_base64, lang_from, lang_to, ocr_url=ocr_url_para):
    ocr_url = generate_url(image_base64, lang_from, lang_to, ocr_url)
    print(ocr_url)

    response = requests.post(
        url=ocr_url,
        data=image_base64
    )
    print "response"
    return response.json()

def get_ocr_result_bytes(image_bytes, lang_from, lang_to, ocr_url=ocr_url_para):
    image_base64 = base64.b64encode(image_bytes)
    print image_base64
    return get_ocr_result_base64(image_base64, lang_from, lang_to, ocr_url)


def get_ocr_result(filename, lang_from, lang_to, ocr_url=ocr_url_para):
    image_bytes = open(filename, 'rb').read()
    return get_ocr_result_bytes(image_bytes, lang_from, lang_to, ocr_url)


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


def generate_sign(client, input_info, salt, secret_key):
    md5bytes = client.encode('utf-8') + input_info + salt.encode('utf-8') + secret_key.encode('utf-8')
    return hashlib.md5(md5bytes).hexdigest()

if __name__ == '__main__':
    type = 'image' # image or base
    lang_from = 'zh-CHS'
    lang_to = 'ja'

    if type == 'image':
        ocr_result = get_ocr_result(sys.argv[1], lang_from, lang_to)
    elif type == 'base64':
        ocr_result = get_ocr_result_base64(open(sys.argv[1]).read(), lang_from, lang_to)

    print(json.dumps(ocr_result, ensure_ascii=False))
