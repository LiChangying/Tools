# encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('gbk')

'''
统计各个音频文件时长
'''

from mutagen.mp3 import MP3
import os
import shutil
import wave
'''
mp3音频文件时长
'''
def file_gallery(folder_path,output_path):
    num = 0
    time = 0
    time_10 = 0
    time_20 = 0
    time_30 = 0
    time_40 = 0
    time_50 = 0
    time_60 = 0
    time_70 = 0
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                if filename.endswith('.mp3'):
                    audio = MP3(file_path)
                    length = audio.info.length
                elif filename.endswith('.wav'):
                    audio = wave.open(file_path)
                    params = audio.getparams()
                    length = params[3] / params[2]
                    # print file_path
                else:
                    pass
                time += length
                if length < 10:
                    time_10 += 1
                elif length < 20:
                    time_20 += 1
                elif length < 30:
                    time_30 += 1
                elif length < 40:
                    time_40 += 1
                elif length < 50:
                    time_50 += 1
                elif length < 60:
                    time_60 += 1
                else:
                    time_70 += 1
            except:
                num += 1
                print file_path
                os.remove(file_path)
            # if filename.endswith('jpg') | filename.endswith('png'):
            #     num += 1
            #     file_path = os.path.join(root,filename)
            #     new_file_path = os.path.join(output_path,str(num))
            #     shutil.copy(file_path,new_file_path)
            #     print file_path
    # return '%s deleted.' %str(num)
    print time
    return "The audio time less 10s: %s,\n20s: %s,\n30s: %s,\n40s: %s,\n50s: %s,\n60s: %s,\n more than 60s : %s." %(
        str(time_10),str(time_20),str(time_30),str(time_40),str(time_50),str(time_60),str(time_70)
    )


if __name__ == '__main__':
    inputdir = r'C:\Users\lichangying\Desktop\process'
    outputdir = r'C:\Users\lichangying\Desktop\audio'
    print file_gallery(inputdir,outputdir)