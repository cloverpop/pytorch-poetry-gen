# coding:utf-8

from __future__ import print_function

import torch
import cPickle as p
from utils import *



if torch.cuda.is_available():
    CUDA_GPU = 1
else:
    CUDA_GPU = 0
    print( "No GPU CUDA support")

model = torch.load('poetry-gen.pt')
max_length = 100
rFile = file('wordDic', 'r')
word_to_ix = p.load(rFile)

print("len(word_to_ix)=[%d]"%(len(word_to_ix)))

def invert_dict(d):
    return dict((v, k) for k, v in d.iteritems())


ix_to_word = invert_dict(word_to_ix)


# Sample from a category and starting letter
def sample(startWord='<START>'):
    input = make_one_hot_vec_target(startWord, word_to_ix)

    hidden = model.initHidden()
    output_name = "";
    if (startWord != "<START>"):
        output_name = startWord
    for i in range(max_length):
        if CUDA_GPU:
            output, hidden = model(input.cuda(), hidden)
        else:
            output, hidden = model(input, hidden)

        topv, topi = output.data.topk(1)
        topi = int(topi[0][0])

        w = ix_to_word[topi]
        if w == "<EOP>":
            break
        else:
            output_name += w
        input = make_one_hot_vec_target(w, word_to_ix)
    return output_name



print( sample("春".decode('utf-8')))
print( sample("花".decode('utf-8')))
print( sample("秋".decode('utf-8')))
print( sample("月".decode('utf-8')))
print( sample("夜".decode('utf-8')))
print( sample("山".decode('utf-8')))
print( sample("水".decode('utf-8')))
print( sample("葉".decode('utf-8')))
