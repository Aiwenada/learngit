#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2015  Data Enlighten Technology (Beijing) Co.,Ltd

__author__ = 'ada'

import Lib.Logger.log4py as log

class Pinyin():
    def __init__(self, data_path='./Mandarin.dat'):
        self.dict = {}
        for line in open(data_path):
            k, v = line.split('\t')
            self.dict[k] = v
        self.splitter = ''
    def get_pinyin(self, chars=u"输入"):
        result = []
        try:
            for char in chars:
                key = "%X" % ord(char)
                try:
                    result.append(self.dict[key].split(" ")[0].strip()[:-1].lower())
                except:
                    result.append(char)
        except Exception as e:
            log.e(e)
        return self.splitter.join(result)
    def get_initials(self, char=u'你好'):
        try:
            return self.dict["%X" % ord(char)].split(" ")[0][0]
        except:
            return char

if __name__ == '__main__':
    pinyintest = Pinyin()
    result = pinyintest.get_pinyin("测试2a论2台a.")
    print(result)