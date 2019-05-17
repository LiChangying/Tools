#/user/bin/python python2.7.16
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__="lcy"

import os
import shutil

def rename(path,save_path):
    cnt = 0
    for folderName, subfolders, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('jpg') | filename.endswith('png'):
                img_path = os.path.join(folderName, filename)
                cnt = cnt + 1
                # print cnt
                # if str(cnt) == '91':
                #     cnt = cnt + 1
                # elif str(cnt) == '120':
                #     cnt = cnt + 1
                shutil.copy(img_path,os.path.join(save_path,str(cnt) + '.' + filename.split('.')[1]))

save_path = r'C:\Users\lichangying\Desktop\temp'
sougou_pic_path = r'C:\Users\lichangying\Desktop\sougou_trans'
rename(sougou_pic_path,save_path)