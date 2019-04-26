#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import hashlib
import time
import json
import base64
import ruamel.yaml as yaml
import cv2
import numpy
import os
from PIL import Image, ImageDraw, ImageFont

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

def get_result(image_path,  ocr_url=ocr_url_para):
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
    # print(sign)

    ocr_url = ocr_url + "&salt=" + salt + "&sign=" + sign + "&from=" + lang_from + "&to=" + lang_to
    # print(ocr_url)

    response = requests.post(
        url=ocr_url,
        data=image_base64
    )
    # print "response"
    return response.text

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
    font = ImageFont.truetype('NotoSansCJK-Regular.ttc', textSize)
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

#function : 图片上加矩形框Bbox
#input : img,Opencv数据格式
#input : top_position,左上角坐标
#input : bottom_position,右下角坐标
#input : text_color，Bbox颜色
#input : line_size，线条粗细
#output : img，转换后的数据，Opencv格式
def cv2ImagAddBbox(img, top_position=(0,0), bottom_position=(0,0), text_color=(0, 255, 0), line_size=-1):

    # 画标注矩形框bounding box
    cv2.rectangle(img, top_position,
                  bottom_position,
                  text_color, line_size)  # 白色bbox
    return img

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
    pic_direction = trans_data['orientation'].lower()
    if pic_direction == 'right':
        img_angle = 90
        img = rotate_image(img,img_angle)
    elif pic_direction == 'left':
        img_angle = -90
        img = rotate_image(img, img_angle)
    elif pic_direction == 'down':
        img_angle = 180
        img = rotate_image(img, img_angle)
    else:
        pass

    #提取OCR转换后结果数据集，包含识别结果，识别内容所在区域坐标
    try:
        result_data = trans_data['resRegions']
    except:
        print img_path + ' Error'
    content = []            #识别内容
    frame = []              #识别内容所在区域
    translate_content = []  #翻译内容
    line_height = []        #单行高度
    lines_count = []        #原文的行数
    for data in result_data:
        content.append(data['context'])
        frame.append(data['boundingBox'])
        translate_content.append(data['tranContent'])
        line_height.append(data['lineheight'])
        lines_count.append(data['linesCount'])
    # print 'direction : ' + str(pic_direction)
    # print 'content : ' + str(len(content))
    # print 'frame : ' + str(len(frame))
    # print response.read()

    img_content = img
    img_translate_content = img

    #批量画标注矩形框bounding box
    if len(content) == 0 | len(frame) == 0:
        pass
    else:
        for i in range(len(frame)):                     #获取bbox的位置，左上角&右下角
            left_top_x = int(frame[i].split(',')[0])
            left_top_y = int(frame[i].split(',')[1])
            width = int(frame[i].split(',')[2])
            height = int(frame[i].split(',')[3])
            # 画标注矩形框bounding box
            img_content = cv2ImagAddBbox(img_content,(left_top_x,left_top_y),(left_top_x + width, left_top_y + height),(255,255,255),-1)
            img_translate_content = cv2ImagAddBbox(img_translate_content, (left_top_x, left_top_y), (left_top_x + width, left_top_y + height),
                                         (255, 255, 255), -1)
            # # 标注文本
            text = content[i]
            text_translate = translate_content[i]
            text_height_self = int(line_height[i])   #识别结果字的高度
            text_lines_self = int(lines_count[i])    #该区域所有的行数
            display_data = ''                       #识别内容
            display_data_translate = ''             #翻译内容
            if text_lines_self > 1:                      #拆分文本
                line_data_cnt = width // int(text_height_self / 3)
                line_data_cnt_cn = width // int(text_height_self / 2)
                for i in range(text_lines_self):
                    display_data += ((text[i * line_data_cnt: (i + 1) * line_data_cnt]) + '\n')
                    display_data_translate += ((text_translate[i * line_data_cnt_cn: (i + 1) * line_data_cnt_cn]) + '\n')
            else:
                display_data = text
                display_data_translate = text_translate
            for i,txt in enumerate(display_data.split('\n')):                               #插入文本
                y = left_top_y + i * text_height_self                           #插入文本所在高度
                img_content = cv2ImgAddText(img_content, txt, left_top_x, y, (0, 0, 0), int(text_height_self / 2))
            for i,txt in enumerate(display_data_translate.split('\n')):                               #插入文本
                y = left_top_y + i * text_height_self                           #插入文本所在高度
                img_translate_content = cv2ImgAddText(img_translate_content, txt, left_top_x, y, (0, 0, 0), int(text_height_self / 2))
            #     # cv2.putText(img, txt, (left_top_x, y), font, 0.8, (0, 0, 0), 1)
    # cv2.imwrite('test_001.jpg',img)
    return img_content, img_translate_content

#function : 将原图、识别内容图、翻译结果图合并成一张图
#input : image_path,图片路径
#input : save_path,转换后图片保存路径
#output : None
def trans_image(image_path,save_path):
    #获取OCR结果集
    ocr_trans_data = ''
    # with open(r'C:\Users\lichangying\.PyCharmCE2019.1\config\scratches\scratch.json') as fjson:
    #     ocr_trans_data = fjson.read()
    # ocr_trans_data = str_trans_json(ocr_trans_data)
    ocr_trans_data = get_result(image_path)
    ocr_trans_data = str_trans_json(ocr_trans_data)
    if ocr_trans_data['errorCode'] == '0':
        # ocr_trans_data = json.dumps(ocr_trans_data, ensure_ascii=False)
        # merge image
        imagelist = []
        #获取原图
        pic1 = cv2.imread(image_path, cv2.IMREAD_COLOR)
        # 图片方向,1-逆时针旋转90度，2-逆时针旋转180度，3-逆时针旋转270度
        pic_direction = ocr_trans_data['orientation'].lower()
        print pic_direction
        if pic_direction == 'right':
            img_angle = 90
            pic1 = rotate_image(pic1, img_angle)
        elif pic_direction == 'left':
            img_angle = -90
            pic1 = rotate_image(pic1, img_angle)
        elif pic_direction == 'down':
            img_angle = 180
            pic1 = rotate_image(pic1, img_angle)
        else:
            pass
        imagelist.append(pic1)
        #获取识别内容图片
        pic_content,pic_translate_content = label_pic(image_path, ocr_trans_data)
        imagelist.append(pic_content)
        #获取翻译结果图片
        imagelist.append(pic_translate_content)
        full_image = numpy.concatenate(imagelist, axis=1)
        #新图片名称命名
        result_pic_name = str(int(time.time() * 1000)) + '_' + os.path.split(image_path)[1].split('.')[0] +  '_merge.png'
        cv2.imwrite(os.path.join(save_path,result_pic_name), full_image)
        print image_path + ' Success.'
        return 'Success'
    else:
        print image_path + ' Error'
        return 'Fail'
        pass

#function : 将该目录下的所有图片进行OCR转换
#input : path, picture folder path
#iinput : save_path, trans picture save path
#output : None
def pic_file_recursive(path,save_path):
    #重新组织路径
    cnt_success = 0     #成功计数
    cnt_fail = 0        #失败计数
    for folderName, subfolders, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('jpg') | filename.endswith('png'):
                img_path = os.path.join(folderName,filename)
                try:
                    flag = trans_image(img_path,save_path)
                    if flag == 'Success':
                        cnt_success += 1
                    else:
                        cnt_fail += 1
                except IOError:
                    print img_path + ' Fail.'
                    cnt_fail += 1
                    continue
    return 'Total %d. %d Success, %d Fail' % (cnt_success + cnt_fail, cnt_success, cnt_fail)

if __name__=='__main__':
    image_folder_path = ''  # 图片完整路径
    image_save_path = ''  # 保存图片完整路径
    if len(sys.argv) < 2:
        print 'Please input img path'
        sys.exit()
    elif len(sys.argv) < 3:
        print 'Please input save path'
        sys.exit()
    else:
        image_folder_path = str(sys.argv[1])
        image_save_path = str(sys.argv[2])
    # image_folder_path = r'C:\Users\lichangying\Desktop\test_pic'
    # image_save_path = r'C:\Users\lichangying\Desktop\test_pic'
    print pic_file_recursive(image_folder_path,image_save_path)
    # print data