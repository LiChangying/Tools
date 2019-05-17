#/user/bin/python python2.7.16
# coding=utf-8
import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

__author__="lcy"

import time
import datetime

# function ： 时间戳数值转时间，格式为YY-mm-dd HH-MM-SS
def stamp_trans_time(time_stamp):
    loc_time = time.localtime(time_stamp)
    time_format = time.strftime("%Y-%m-%d %H-%M-%S", loc_time)
    return time_format