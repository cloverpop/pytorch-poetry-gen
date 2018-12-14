#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import re
import json
import codecs

from sc_2_tc import zh2Hant
from tc_2_sc import zh2Hans
    
#---------------------------------------------------
# Global constant
#
global json_list

# original json root folder
#JSON_ROOT = os.getcwd()
#JSON_ROOT= "C:\zyang\workspace\pytorch-poetry-gen\pytorch-poetry-gen\chinese-poetry\json"
JSON_ROOT = os.getcwd() 

# new json generated root folder
JSON_GEN_ROOT = os.getcwd() + os.sep + 'gen'

INPUT_FILE = "poet.song.1000.json"

# convert TC to SC
def tc_2_sc(sentence):
    assert(sentence != None)

    sc_sentence = ''
    
    for i in range(len(sentence)):
        tc = sentence[i]
        try:
            sc = zh2Hans[tc]
        except KeyError:
            # loop again to see if sc is a sentence
            tmp_s = ''
            for j in range(len(tc)):
                tmp_tc = tc[j]
                try:
                    tmp_sc = zh2Hans[ tmp_tc ]
                except KeyError:
                    tmp_sc = tmp_tc
                tmp_s += tmp_sc
            
            sc = tmp_s            
        sc_sentence += sc

    return sc_sentence

# convert SC to TC
def sc_2_tc(sentence):
    assert(sentence != None)

    tc_sentence = ''
    
    for i in range(len(sentence)):
        sc = sentence[i]
        try:
            tc = zh2Hant[sc]
        except KeyError:
            tc = sc
        tc_sentence += tc

    return tc_sentence


def parse_and_generate_json(infile, outfile):
    assert( infile != None  )
    assert( outfile != None )
    
    fin = None
    fout = None
    
    try:
        fout = codecs.open(outfile, "wb", "utf-8")

        
        with codecs.open(infile, 'rb', 'utf-8') as fin:
            data = json.load(fin)
            data_out = {}

            #
            # can print all Chinese poems correctly
            #
            #print(json.dumps(data, ensure_ascii=False))

            poem_count = len(data)
            print("poem count=%d"%(poem_count))

            for i in range(poem_count):
                #
                # Processing 'author'
                #
                try:
                    tc_author = data[i]["author"]

                    #
                    # This will output the utf8 format author
                    #
                    #print(tc_author.encode('utf8'))

                    #
                    # This will output the Unicode format author (Chinese)
                    #
                    # print(tc_author)

                    sc_author = tc_2_sc(tc_author)
                    #print(sc_author)

                    #print(tc_author + "\t==>\t" + sc_author + "\t==>\t" + tc_author)
                    data_out['author'] = sc_author
                    
                except KeyError:
                    # this is not a poem
                    pass                

                #
                # Processing 'title'
                #
                try:
                    tc_title = data[i]["title"] 
                    sc_title = tc_2_sc(tc_title)

                    #tc2_title = sc_2_tc(sc_title)
                    #print(tc_title + "\t==>\t" + sc_title + "\t==>\t" + tc2_title)

                    data_out['title'] = sc_title
                except KeyError:
                    pass

                #
                # Processing 'strains'
                #
                try:
                    tc_strains = data[i]['strains']
                    sc_strains = tc_2_sc(tc_strains)
                    data_out['strains'] = sc_strains
                
                except KeyError:
                    pass

                #
                # Processing 'paragraphs'
                #
                try:
                    tc_poem = data[i]["paragraphs"]

                    # paragraph is special
                    tmp_poem = ''
                    for i in range(len(tc_poem)):
                        tc = tc_poem[i]
                        try:
                            #sc = zh2Hans[tc]
                            sc = tc_2_sc(tc)
                        except KeyError:
                            sc = tc
                        #print( tc + "\t=>\t" + sc)
                        tmp_poem += sc
                    #print(tmp_poem)
                    data_out["paragraphs"] = tmp_poem
                except KeyError:
                    pass

                #
                # Processing 'name'
                #
                try:
                    tc_name = data[i]['name']
                    sc_name = tc_2_sc(tc_name)
                    data_out['name'] = sc_name
                except KeyError:
                    pass

                #
                # Processing 'desc'
                #
                try:
                    tc_desc = data[i]['desc']
                    sc_name = tc_2_sc(tc_desc)
                    data_out['desc'] = sc_name
                except KeyError:
                    pass
                
                #print(data[i])
                json.dump(data_out, fout, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
                #break
                
        fin.close()
        fout.close()
        
    except IOError:
        print("Failed to open %s"%(infile))
        
    pass

def parse_all_json(root):
    global json_list
    
    assert(root!=None)
    valid_json = 0
    
    for root, dirs, files in os.walk(root):
        for filename in files:
            if filename.rfind('.json') != -1:
                path = root + os.sep + filename
                #print(path)
                json_list.append(path)

                infile = path
                if infile.rfind(os.sep+ 'gen' + os.sep) != -1:
                    continue

                valid_json += 1
                
                outfile = JSON_GEN_ROOT + os.sep + filename
                print(infile)
                print(outfile)
                parse_and_generate_json(infile, outfile)

    
    print("Total json file count=%d"%(valid_json))

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
    global json_list
    json_list = []
    
    parse_all_json(JSON_ROOT)

    pass
