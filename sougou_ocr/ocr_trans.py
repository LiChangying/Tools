#/user/bin/python python2.7.16
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__="lcy"

import md5
import urllib2
import urllib
import os
import time
import base64
import json
import ruamel.yaml as yaml
import cv2
import numpy
from wand.image import Image

from PIL import Image, ImageDraw, ImageFont


image_folder_path = ''          #图片完整路径
image_save_path = ''            #保存图片完整路径
# image_folder_path = r'C:\Users\lichangying\Desktop\test_pic'
# python ocr_trans.py C:\Users\lichangying\Desktop\test_pic
if len(sys.argv) < 2:
    print 'Please input img path'
    sys.exit()
elif len(sys.argv) < 3:
    print 'Please input save path'
    sys.exit()
else:
    image_folder_path = str(sys.argv[1])
    image_save_path = str(sys.argv[2])

# function:MD5签名
# input:str    要经MD5的字符串
# output:str    返回MD5的前32位
def data_md5(str):
    m = md5.new()
    m.update(str.encode(encoding='utf-8'))
    return m.hexdigest()

# function：将图片经base64编码
# input:img             图片路径
# return：base64_data    base64编码后数据
def img_base64_encode(img):
    with open(img,'rb') as fpic:                    #打开图片
        base64_data = base64.b64encode(fpic.read())    #base64编码
    return base64_data                              #返回编码结果

# function：将数据经base64解码还原图片
# input:base64_data  base64编码数据
# return：img        base64解码后数据
def img_base64_decode(base64_data):
    return base64.b64decode(base64_data)          #返回解码结果

# function：对长度超过1024的图片取前1024位处理
# input:str             图片数据
# return：str           切片后的数据
def img_short(str):
    if len(str) > 1024:
        return str[0:1024]
    else:
        return str

#function : 获取经OCR后的结果
# input:str  图片完整路径
# return：str OCR返回数据集
def get_result(img_path):
    #源语言
    fromLan = 'en'
    #目标语言
    toLan = 'zh-CHS'
    #接入地址
    url = 'http://deepi.sogou.com/api/sogouService'
    #平台PID
    pid = '52db1895b60c5a55ed5322d1b5fec684'
    #平台Service
    service = 'translateOpenOcr'
    #用户密钥
    user_secret = '83ddd3234bc46e153f69a445b0b0981d'
    # 随机数，自己随机生成，建议时间戳
    salt = str(int(time.time())) #10位时间戳
    # 图片路径
    image_path = img_path
    # 图片base64编码
    img_base64_data = img_base64_encode(image_path)
    # sign签名
    # 若编码后数据长度超1024，取前1024位，否则，全取
    img_short_data = img_short(img_base64_data)
    sign = data_md5(pid + service + salt + img_short_data + user_secret)
    # print(sign)
    #对各字段做URL encode
    inputData = {
        'service':service,
        'pid':pid,
        'salt':salt,
        'from':fromLan,
        'to':toLan,
        'image':img_base64_data
        ,'sign':sign
    }
    #URL encode
    inputData = urllib.urlencode(inputData)
    #header信息
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'accept': "application/json"
        }
    #Request
    request = urllib2.Request(url,data=inputData,headers=headers)
    #Response
    response = urllib2.urlopen(request)
    #获取响应内容
    response_data = response.read()
    # print response_data
    return response_data

#function : 响应数据接送格式转换
#input : str,需要转换的数据
#output : json，转换后的数据，json格式
def str_trans_json(str):
    response_data = json.loads(str)          #将已编码的 JSON 字符串解码为 Python 对象
    json_data = json.dumps(response_data, ensure_ascii=False, encoding='utf-8')   #将 Python 对象编码成 JSON 字符串
    unicode_data = yaml.safe_load(json_data)
    return unicode_data

#function : 图片上加文字
#input : img,Opencv数据格式
#input : text,文本
#input : left,左上角坐标
#input : top，左上角坐标
#input : textColor，文字颜色
#tinput : extSize : 文字大小
#output : img，转换后的数据，Opencv格式
def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, numpy.ndarray)):  #判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    # 字体  字体*.ttc的存放路径一般是： /usr/share/fonts/opentype/noto/ 查找指令locate *.ttc
    font = ImageFont.truetype(r'D:\pycode\sougou_ocr\NotoSansCJK-Regular.ttc', textSize)
    # 字体颜色
    fillColor = textColor
    # 文字输出位置
    position = (left, top)
    # 输出内容
    str = text

    # 需要先把输出的中文字符转换成Unicode编码形式
    if not isinstance(str, unicode):
        str = str.decode('utf8')
    draw.text(position, str, font=font, fill=fillColor)
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

#function :返回图片旋转结果
#input : mat，图片源
#input : angle，角度信息
#output : rotated_mat，旋转后的图片
def rotate_image(mat, angle):
    # angle in degrees
    height, width = mat.shape[:2]
    image_center = (width/2, height/2)

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    abs_cos = abs(rotation_mat[0,0])
    abs_sin = abs(rotation_mat[0,1])

    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat

#function :将识别结果在原图进行标注，批量画标注矩形框bounding box
#input : img_path,图片路径
#input : trans_data,OCR后的结果集
#output : img，标注后的图片(为新建图片)
def label_pic(img_path,trans_data):
    #图片信息
    img = cv2.imread(img_path,cv2.IMREAD_COLOR)

    #图片旋转操作
    img_angle = 0
    # 图片方向,1-逆时针旋转90度，2-逆时针旋转180度，3-逆时针旋转270度
    pic_direction = trans_data['direction']
    if pic_direction == 1:
        img_angle = 90
        img = rotate_image(img,img_angle)
    elif pic_direction == 2:
        img_angle = 180
        img = rotate_image(img, img_angle)
    elif pic_direction == 3:
        img_angle = 270
        img = rotate_image(img, img_angle)
    else:
        pass

    #提取OCR转换后结果数据集，包含识别结果，识别内容所在区域坐标
    result_data = trans_data['result']
    content = []        #识别内容
    frame = []          #识别内容所在区域
    text_height = []    #字高度
    for data in result_data:
        content.append(data['content'])
        frame.append(data['frame'])
        text_height.append(data['text_height'])
    # print 'direction : ' + str(pic_direction)
    # print 'content : ' + str(len(content))
    # print 'frame : ' + str(len(frame))
    # print response.read()

    #批量画标注矩形框bounding box
    if len(content) == 0 | len(frame) == 0:
        pass
    else:
        for i in range(len(frame)):                     #获取bbox的位置，左上角&右下角
            left_top_x = int(frame[i][0].split(',')[0])
            left_top_y = int(frame[i][0].split(',')[1])
            right_bottom_x = int(frame[i][2].split(',')[0])
            right_bottom_y = int(frame[i][2].split(',')[1])
            # 画标注矩形框bounding box
            cv2.rectangle(img,(left_top_x,left_top_y),
                          (right_bottom_x,right_bottom_y),
                          (255,255,255),-1)                     #白色bbox
            # # 标注文本
            text = content[i]
            text_height_self = int(text_height[i])   #识别结果字的高度
            # font = cv2.FONT_HERSHEY_SIMPLEX
            display_data = ''
            if len(text) * text_height_self > right_bottom_x - left_top_x:                      #拆分文本
                line_data_cnt = (right_bottom_x - left_top_x) // int((text_height_self / 3.3))
                for i in range(0,len(text),line_data_cnt):
                    display_data += (text[i:i+line_data_cnt] + '\n')
            else:
                display_data = text
            for i,txt in enumerate(display_data.split('\n')):                               #插入文本
                y = left_top_y + i * text_height_self                           #插入文本所在高度
                img = cv2ImgAddText(img, txt, left_top_x, y, (0, 0, 0), int(text_height_self / 2))
            #     # cv2.putText(img, txt, (left_top_x, y), font, 0.8, (0, 0, 0), 1)
    # cv2.imwrite('test_001.jpg',img)
    return img

#function :将翻译结果在原图进行标注，批量画标注矩形框bounding box，搜狗提供pic的base64编码
#input : img_path,图片路径
#input : trans_data,OCR后的结果集
#output : img，翻译后的图片(为新建图片)
def translate_pic(img_path,trans_data):
    img = trans_data['pic']
    img = img_base64_decode(img)
    with open('translate_temp.jpg', 'wb') as fpic:
        fpic.write(img)
    img = cv2.imread('translate_temp.jpg',cv2.IMREAD_COLOR)
    return img


#function : 将原图、识别内容图、翻译结果图合并成一张图
#input : image_path,图片路径
#input : save_path,转换后图片保存路径
#output : None
def trans_image(image_path,save_path):
    #获取OCR结果集
    ocr_trans_data = str_trans_json(get_result(image_path))
    # merge image
    imagelist = []
    #获取原图
    pic1 = cv2.imread(image_path, cv2.IMREAD_COLOR)
    # 图片方向,1-逆时针旋转90度，2-逆时针旋转180度，3-逆时针旋转270度
    pic_direction = ocr_trans_data['direction']
    if pic_direction == 1:
        img_angle = 90
        pic1 = rotate_image(pic1, img_angle)
    elif pic_direction ==2:
        img_angle = 180
        pic1 = rotate_image(pic1, img_angle)
    elif pic_direction == 3:
        img_angle = 270
        pic1 = rotate_image(pic1, img_angle)
    else:
        pass
    imagelist.append(pic1)
    #获取识别内容图片
    pic2 = label_pic(image_path, ocr_trans_data)
    imagelist.append(pic2)
    #获取翻译结果图片
    pic3 = translate_pic(image_path,ocr_trans_data)
    imagelist.append(pic3)
    full_image = numpy.concatenate(imagelist, axis=1)
    #新图片名称命名
    result_pic_name = str(int(time.time() * 1000)) + '_' + os.path.split(image_path)[1].split('.')[0] +  '_merge.png'
    cv2.imwrite(os.path.join(save_path,result_pic_name), full_image)

#function : 将该目录下的所有图片进行OCR转换
#input : path, picture folder path
#iinput : save_path, trans picture save path
#output : None
def pic_file_recursive(path,save_path):
    #重新组织路径
    cnt_success = 0  # 成功计数
    cnt_fail = 0  # 失败计数
    for folderName, subfolders, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('jpg') | filename.endswith('png'):
                img_path = os.path.join(folderName,filename)
                try:
                    trans_image(img_path,save_path)
                    cnt_success += 1
                    print img_path + ' Success.'
                except IOError:
                    print img_path + ' Fail.'
                    cnt_fail += 1
                    continue
    return 'Total %d. %d Success, %d Fail' % (cnt_success + cnt_fail, cnt_success, cnt_fail)



if __name__ == '__main__':
    # print image_folder_path
    print pic_file_recursive(image_folder_path,image_save_path)
    # str_trans_json(get_result(image_folder_path))
    # trans_image(image_folder_path)
