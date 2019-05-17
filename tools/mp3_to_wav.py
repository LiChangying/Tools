#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pydub
import argparse
import os
import io
import wave

'''
mp3转wav，单个文件
'''
def trans_mp3_to_wav(mp3_path,wav_path):
    with open(mp3_path,'rb') as fmp3:
        data = fmp3.read()
    aud = io.BytesIO(data)
    pydub.AudioSegment.converter = r'D:\test_tool\ffmpeg-20190508-06ba478-win64-static\bin\ffmpeg.exe'   #ffmpeg的可执行路径
    sound = pydub.AudioSegment.from_file(aud, format='mp3')
    raw_data = sound._data
    size = len(raw_data)
    try:
        f = wave.open(wav_path, 'wb')
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.setnframes(size)
        f.writeframes(raw_data)
        f.close()
    except:
        print mp3_path + ' is failed.'

'''
批量文件处理
'''
def file_gallery(inputdir,outputdir):
    suc_cnt = 0
    fail_cnt = 0
    for root, dirs, files in os.walk(inputdir):
        for file in files:
            if  file.endswith('.mp3') or file.endswith('.Mp3') or file.endswith('MP3') or file.endswith('.mP3'):
                source_path = os.path.join(root,file)
                target_path = os.path.join(outputdir,file.split('.')[0] + '.wav')
                trans_mp3_to_wav(source_path,target_path)
                suc_cnt += 1
            else:
                fail_cnt += 1
                print file
            # if filename.endswith('jpg') | filename.endswith('png'):
            #     num += 1
            #     file_path = os.path.join(root,filename)
            #     new_file_path = os.path.join(output_path,str(num))
            #     shutil.copy(file_path,new_file_path)
            #     print file_path
    return '%s succeed, %s failed.' %(str(suc_cnt),str(fail_cnt))

'''
获取wav音频信息
(0,1)声道
(1,2)采样宽度
(2,16000)帧速率
(3,2510762)帧数
(4,'NONE')唯一标识
(5,'not compressed')无损
'''
def get_wav_params(wav_path):
    f = wave.open(wav_path,'rb')
    params =  f.getparams()
    f.close()
    return params


if __name__ == '__main__':
    curpath = os.getcwd()
    parser = argparse.ArgumentParser(description='Command line client for get stream result')
    parser.add_argument('-i', '--inputdir', default=os.path.join(curpath, "audio"), dest="inputdir",
                        help="音频文件夹位置")
    parser.add_argument('-o', '--outputdir',default=os.path.join(curpath,'trans_audio'), dest="outputdir",
                        help="转出音频文件保存位置")
    args = parser.parse_args()
    # inputdir = r'C:\Users\lichangying\Desktop\Download'
    # ouputdir = r'C:\Users\lichangying\Desktop\audio'
    print file_gallery(args.inputdir,args.outputdir)
    # print file_gallery(inputdir,ouputdir)