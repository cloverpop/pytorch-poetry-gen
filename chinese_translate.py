#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import re
import json
import codecs

from langconv import *

#---------------------------------------------------
# Global constant
#
POEM_PATH = 'chinese-poetry' + os.sep + "json" 
INPUT_FILE = "poet.song.1000.json"

#
# This API uses the langconv library, which cannot translate TC->SC very well.
#
def Traditional2Simplified(sentence):
    '''
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    '''
    sentence = Converter('zh-hans').convert(sentence)
    return sentence


def read_file_part_one():
    remains = ""
    
    file=os.getcwd() + os.sep + POEM_PATH + os.sep + INPUT_FILE
    
    try:
        with codecs.open(file, 'r', 'utf-8') as fin:
            data = json.load(fin)

            #
            # can print all Chinese poems correctly
            #
            #print(json.dumps(data, ensure_ascii=False))

            poem_count = len(data)
            print("poem count=%d"%(poem_count))

            for i in range(poem_count):
                author = data[i]["author"]
                
                #
                # This will output the utf8 format author
                #
                #print(author.encode('utf8'))

                #
                # This will output the Unicode format author (Chinese)
                #
                # print(author)

                #sc_author = Traditional2Simplified(author)
                #print(sc_author)

                tc_title = data[i]["title"]
                sc_title = Traditional2Simplified(tc_title)
                print("\t\t\t" + sc_title)

                tc_poem = data[i]["paragraphs"]
                sc_poem = Traditional2Simplified(tc_poem)
                print(sc_poem)
                

        
        


        fin.close()
        
    except IOError:
        print("Failed to open %s"%(file))
            

    
    pass


def test():
    m = {'a' : '您好'}
    #
    print(m)
    # {'a': '您好'}
    print(json.dumps(m))
    # {"a": "\u60a8\u597d"}
    print(json.dumps(m, ensure_ascii=False))
    # {"a": "您好"}
    print(json.dumps(m, ensure_ascii=False).encode('utf8').decode('gbk'))
    # {"a": "鎮ㄥソ"}


if __name__ == "__main__":
    test()
    
    read_file_part_one()

    pass
