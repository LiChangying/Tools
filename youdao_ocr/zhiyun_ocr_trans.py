#/user/bin/python python2.7.16
# coding:utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import base64
import time
import random
import md5
import urllib
import urllib2

# 您的应用ID
appKey = "zhudytest123"
# 您的应用密钥，请勿把它和appKey泄露给他人
appSecret = "youdaoapiv120171"


def get_result(imgfile):
    current_milli_time = lambda: int(round(time.time() * 1000))
    print(imgfile)
    img = open(imgfile.strip()).read()
    imgb64= base64.b64encode(img)
    # 源语言
    fromLan = "auto"
    # 目标语言
    to = "zh-CHS"
    #to = "en"
    # 上传类型
    type = "1"
    # 随机数，自己随机生成，建议时间戳
    salt = random.randint(1, 65536)
    # 签名
    sign = appKey+imgb64+str(salt)+appSecret
    m1 = md5.new()
    m1.update(sign)
    sign = m1.hexdigest()
    data = {'appKey':appKey,'q':imgb64,'from':fromLan,'to':to,'type':type,'salt':str(salt),'sign':sign}
    oldmillsec = current_milli_time()
    f = urllib.urlopen(
        url = 'http://openapi.youdao.com/ocrtransapi',
        data    = urllib.urlencode(data)
    )
    content = f.read()
    return content

if __name__ == '__main__':
    img_path = r'D:\pycode\youdao_ocr\test_pic001.jpg'
    print get_result(img_path)