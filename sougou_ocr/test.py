#/user/bin/python python2.7.16
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__="lcy"

from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy
import os

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

image_folder_path = ''          #图片完整路径
# image_folder_path = r'C:\Users\lichangying\Desktop\test_pic' python ocr_trans.py C:\Users\lichangying\Desktop\test_pic
# if len(sys.argv) < 2:
#     print 'Please input img path'
#     sys.exit()
# else:
#     image_folder_path = str(sys.argv[1])

for folderName, subfolders, filenames in os.walk(image_folder_path):
    for filename in filenames:
        if filename.endswith('jpg') | filename.endswith('png'):
            img_path = os.path.join(folderName, filename)
            try:
                print img_path
            except IOError:
                print img_path
                continue

image_path = r'C:\Users\lichangying\Desktop\IMG20190422_150236.png'
img = cv2.imread(image_path,cv2.IMREAD_COLOR)
img = cv2ImagAddBbox(img,(100,100),(200,200),(255,255,255))
img = cv2ImgAddText(img,'大家好',100,100,(0,255,0),40)
cv2.namedWindow("Image")
cv2.imshow('Image',img)
cv2.waitKey(0)
