#/user/bin/python python2.7.16
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__="lcy"

'''
    音频采样率转换
'''

from pydub import AudioSegment
import os
import wave

'''
#音频文件路径
audio_path = r''
file_name = r''
#保存路径
save_path = r''
#读取音频文件，设置采样率
audio_file = AudioSegment.from_wav(os.path.join(audio_path,file_name))
#按指定采样率导出文件到指定路径
audio_file.export(os.path.join(save_path,file_name),format='wav',bitrate='16k')
'''

#打开音频文件，获取音频文件参数
def get_params_audio(src_path):
    try:
        f_audio = wave.open(src_path,'rb')
        return f_audio.getparams()
    except IOError as e:
        print e
    finally:
        f_audio.close()

audio_file_path = r'C:\Users\lichangying\Desktop\fanyiguan_log_1000_en\video\1.wav'
print get_params_audio(audio_file_path)
