#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib, urllib2
import ssl
import base64
import json
import time
from cookielib import CookieJar
import os

import time
import cv2
from wand.color import Color
from textwrap import fill
from wand.image import Image
from wand.drawing import Drawing
from wand.api import library
import numpy as np
from wand.compat import nested

import time
import time
import cv2

import md5
import random
from glob import glob

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

def draw_image(imgfile, rs, run_type, img_angle):
    line_strs = ''
    with Image(filename=imgfile+'_rect.png') as img:
        for r in rs['resRegions']:
            if len(r['tranContent']) == 0:
                continue
            bbox = [int(x) for x in r['boundingBox'].split(',')]

            if run_type == 'translate':
                line_strs += r['tranContent']
                line_strs += '\n'
            elif run_type == 'ocr':
                line_strs += r['context']
                line_strs += '\n'
            else:
                raise Exception, "run_type:%s does not exist" % run_type

            height = bbox[3]
            line_height = r['lineheight']
            top_y = bbox[1]
            top_x = bbox[0]
            width = bbox[2]
            columns = r['linesCount']

            with nested(Color('black'),
                        Color('black'),
                        Drawing()) as (bg, fg, draw):
                draw.stroke_width = 1
                draw.fill_color = fg
                draw.stroke_color = Color('black')
                draw.font = './NotoSansCJK-Regular.ttc'
                #        draw.font = '/usr/share/fonts/opentype/noto/NotoSansCJK-Thin.ttc'
                #draw.font = '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf'
                k = height
                draw.font_size = int(line_height)*0.7
                if(line_height > 10):
                    draw.font_size = int(line_height*0.6)
                #修正
                if r['lang'] == 'en' or run_type == 'ocr':
                    draw.font_size = int(line_height)
                    if line_height > 10:
                        draw.font_size = int(line_height*0.8)
                

                if run_type == 'translate':
                    trans = r['tranContent']
                elif run_type == 'ocr':
                    trans = r['context']
                else:
                    raise Exception, "run_type:%s does not exist" % run_type
                #trans = fill(trans,width=width/int(line_height*0.8) + 1)
                fill_width = width/int(draw.font_size) + 1
                if run_type == 'ocr' and r['lang'] == 'en': #en2cn
                    fill_width *= 2
                if run_type == 'translate' and r['lang'] == 'zh-CHS':
                    fill_width *= 2
                
                fill_width = max(fill_width, len(trans)/columns + 1)
                trans = fill(trans,width=fill_width)
                ##trans = fill(trans,width=width*0.5)
                #fill_width = max(len(trans)/columns + 1, width/int(line_height*0.8) + 1)
                #trans = fill(trans,width=fill_width)
                #print len(trans)/columns + 1, width/int(line_height) + 1
                draw.text(int(top_x),int(top_y+line_height),trans)
                draw(img)

        img.save(filename = "%s_%s_word.png" % (imgfile, run_type))

        m1 = cv2.imread("%s_%s_word.png" % (imgfile, run_type),1)
        m1 = rotate_image(m1, img_angle)
        if 'textAngle' in rs:
            angle = float(rs['textAngle'])
            rows,cols,cnl = m1.shape
            M1 = cv2.getRotationMatrix2D((cols/2,rows/2),-angle,1)
            m1 = cv2.warpAffine(m1,M1,(cols,rows))

        cv2.imwrite(imgfile+'_'+run_type+'.png',m1)
        with open(imgfile+'_'+run_type+'.txt', 'w') as fl:
            fl.write(line_strs)

def trans_image(image_path):
    file_name=glob(image_path+"/*.jpg") + glob("*.png") + glob("*.jpeg")
    for ff in file_name:
        
        #get http responce
        content = get_result(ff)

        j=json.loads(content)
        print content
        rs = j
        m = cv2.imread(ff.strip(),1)

        img_angle = 0

        if True:
            if 'exif' in rs:
                angle = rs['exif']
                if angle == 'right' or angle == 'Right' or angle == 'RIGHT':
                    img_angle = 90
                    m = rotate_image(m, 90)
                elif angle == 'right' or angle == 'Left' or angle == 'LEFT':
                    img_angle = -90
                    m = rotate_image(m, -90)
                elif angle == 'right' or angle == 'Down' or angle == 'DOWN':
                    img_angle = 180
                    m = rotate_image(m, 180)
            if 'orientation' in rs:
                angle = rs['orientation']
                if angle == 'right' or angle == 'Right' or angle == 'RIGHT':
                    img_angle = 90
                    m = rotate_image(m, 90)
                elif angle == 'right' or angle == 'Left' or angle == 'LEFT':
                    img_angle = -90
                    m = rotate_image(m, -90)
                elif angle == 'right' or angle == 'Down' or angle == 'DOWN':
                    img_angle = 180
                    m = rotate_image(m, 180)


        if 'textAngle' in rs:
            angle = float(rs['textAngle'])
            rows,cols,cnl = m.shape
            M = cv2.getRotationMatrix2D((cols/2,rows/2),+angle,1)
            m = cv2.warpAffine(m,M,(cols,rows))

        for r in rs['resRegions']:
            if len(r['tranContent']) == 0:
                continue
            bbox = [int(x) for x in r['boundingBox'].split(',')]
            line_height = r['lineheight']
            (b,g,r) = m[bbox[1],bbox[0]]
            cv2.rectangle(m,(bbox[0],bbox[1]),(bbox[0]+bbox[2],bbox[1]+bbox[3]),(int(b),int(g),int(r)),-1)

        cv2.imwrite(ff+'_rect.png',m)
        draw_image(ff, rs, 'translate', img_angle)
        draw_image(ff, rs, 'ocr', img_angle)
        #merge image
        imagelist = []
        imagelist.append(cv2.imread(ff, cv2.IMREAD_COLOR))
        imagelist.append(cv2.imread(ff + '_ocr.png', cv2.IMREAD_COLOR))
        imagelist.append(cv2.imread(ff + '_translate.png', cv2.IMREAD_COLOR))
        full_image = np.concatenate(imagelist, axis=1)
        cv2.imwrite(ff + "_merge.png", full_image)

image_path=sys.argv[1]
trans_image(image_path)
