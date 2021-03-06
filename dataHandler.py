#coding:utf-8

#
# Parse the json files of poems
#

import sys
import os
import json
import re

from sys import exit
import string

def parseRawData(author = None, constrain = None):
    rst = []

    def sentenceParse(para):
        if para == "":
            para = "-181-村橋路不端，數里就迴湍。積壤連涇脉，高林上笋竿。早嘗甘蔗淡，生摘琵琶酸。（「琵琶」，嚴壽澄校《張祜詩集》云：疑「枇杷」之誤。）好是去塵俗，煙花長一欄。"
            #para = "-181-村橋路不端，數里就迴湍。積壤連涇脉，高林上笋竿。早嘗甘蔗淡，生摘琵琶酸。好是去塵俗，煙花長一欄。"
        result, number = re.subn("（.*）", "", para)
        result, number = re.subn("（.*）", "", para)
        result, number = re.subn("{.*}", "", result)
        result, number = re.subn("《.*》", "", result)
        result, number = re.subn("《.*》", "", result)
        result, number = re.subn("[\]\[]", "", result)
        r = ""
        for s in result:
            if s not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']:
                r += s;
        r, number = re.subn("。。", "。", r)
        return r

    def handleJson(file):
        #print file
        rst = []
        data = json.loads(open(file).read())
        for poetry in data:
            pdata = ""
            if (author!=None and poetry.get("author")!=author):
                continue
            #
            # To check if there is a valid "paragraphs" section
            #
            p = poetry.get("paragraphs")
            flag = False
            for s in p:
                sp = re.split("[，！。]".decode("utf-8"), s)
                for tr in sp:
                    if constrain != None and len(tr) != constrain and len(tr)!=0:
                        flag = True
                        break
                    if flag:
                        break
            if flag:
                continue

            #I found Tang poems whose titles contains "琴曲歌辭" are duplicated
            #So that we have to filter it out
            my_title = poetry.get("title")
            if my_title.rfind(u"琴曲歌辭") != -1:
                print("Poem title=[%s]"%(my_title))
                continue

            for sentence in poetry.get("paragraphs"):
                pdata += sentence

            #
            # pdata is the Chinese
            #    斷崖如削瓜，嵐光破崖綠。天河從中來，白雲漲川谷。玉案赤文字，世眼不可讀。攝身凌青霄，松風拂我足。
            #
            # rst is a List data structure. Its element is object.
            #
            pdata = sentenceParse(pdata)
            if pdata!="":
                rst.append(pdata)
        return rst

    #
    # Self test the sentenceParse() function
    #
    #print sentenceParse("")

    #
    # data is a List data strcuture
    #
    data = []
    src = os.getcwd() + os.sep+ './chinese-poetry/json/'
    for filename in os.listdir(src):
        #
        #print("Filename="+ filename)
        #
        if filename.startswith("poet.tang"):
            data.extend(handleJson(src+filename))
    return data



#if __name__=='__main__':
#     print parseRawData.sentenceParse("熱暖將來賓鐵文，暫時不動聚白雲。撥卻白雲見青天，掇頭裏許便乘仙。（見影宋蜀刻本《李太白文集》卷二十三。）（以上繆氏本《太白集》）-362-。")

