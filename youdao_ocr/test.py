import base64
import hashlib
import time
import sys
import json

import requests

client = "fanyiguan"
secret_key = "%29jqQ#2n2&]zad(ta9)"

ocr_url_para = 'http://ocrtran.youdao.com/ocr/tranocr?' \
               'keyfrom=fanyi.3.11.6.android&' \
               'imei=imei&' \
               'userId=user&' \
               'type=composite&' \
               'clientele=fanyiguan&'

default_input_info_count = 10
current_milli_time = lambda: int(round(time.time() * 1000))

def get_ocr_result_base64(image_path,  ocr_url=ocr_url_para):
    lang_from = 'en'
    lang_to = 'zh-CHS'
    image_bytes = open(image_path, 'rb').read()
    image_base64 = base64.b64encode(image_bytes)
    input_info = bytearray()
    if input is not None:
        input_length = len(image_base64)
        if input_length > default_input_info_count * 2:
            input_info = image_base64[:default_input_info_count] + str(input_length).encode() + image_base64[
                                                                                                input_length - default_input_info_count:]
        else:
            input_info = image_base64
    salt = str(current_milli_time())
    md5bytes = client.encode('utf-8') + input_info + salt.encode('utf-8') + secret_key.encode('utf-8')
    sign = hashlib.md5(md5bytes).hexdigest()
    print(sign)

    ocr_url = ocr_url + "&salt=" + salt + "&sign=" + sign + "&from=" + lang_from + "&to=" + lang_to
    print(ocr_url)

    response = requests.post(
        url=ocr_url,
        data=image_base64
    )
    print "response"
    return response.json()


if __name__ == '__main__':
    img_path = r'C:\Users\lichangying\Desktop\筛选的case\纸质90\105.jpg'
    ocr_result = get_ocr_result_base64(img_path)
    print(json.dumps(ocr_result, ensure_ascii=False))
