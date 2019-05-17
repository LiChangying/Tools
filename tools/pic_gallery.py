#/user/bin/python python2.7.16
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__="lcy"

import os
import shutil

source_path = ''          #图片完整路径
save_path = ''          #要保存的位置
# source_path = r'D:\work_folder\OCR评测(搜狗&翻译官)\筛选的case'
source_path = r'C:\Users\lichangying\Desktop\mc_fanyidan_log_en_201901\video'
save_path = r'C:\Users\lichangying\Desktop\test_pic'
# if len(sys.argv) < 3:
#     print 'Please input img path & save path'
#     sys.exit()
# else:
#     image_folder_path = str(sys.argv[1])
#     save_path = str(sys.argv[2])

# function : 图片整理到一个文件夹中，要求不能有重名文件
# input : folder_path
# input : output_path
# output : None
def pic_gallery(folder_path,output_path):
    num = 0
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            print filename
            with open('temp.txt','a') as f:
                f.write(filename)
                f.write('\n')
            # if filename.endswith('jpg') | filename.endswith('png'):
            #     num += 1
            #     file_path = os.path.join(root,filename)
            #     new_file_path = os.path.join(output_path,str(num))
            #     shutil.copy(file_path,new_file_path)
            #     print file_path
    return 'Done.'

if __name__ == '__main__':
    print pic_gallery(source_path,save_path)