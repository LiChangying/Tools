#/user/bin/python python2.7.16
# coding=utf-8

'''
#python2
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
'''

__author__="lcy"

import hashlib

def get_md5(data):
    m = hashlib.md5()
    m.update(data.encode('utf-8'))
    return m.hexdigest()