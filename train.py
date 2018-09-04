# coding:utf-8

import random
import torch.nn as nn
import torch.optim as optim
import dataHandler
from model import PoetryModel
from utils import *
import cPickle as p

from sys import exit	#exit(0) for debug purpose
import json


#
# 0:  No GPU cuda support
# 1:  Use CPU instead of GPU
#
CUDA_GPU = 0


#
# Parse the raw data from Chinese-poetry json files
#
#data = dataHandler.parseRawData()  # All if author=None
data = dataHandler.parseRawData(author="李白".decode('utf-8'),constrain=5)  # All if author=None
# random.shuffle(data)
for s in data:
    #print s
    pass
word_to_ix = {}


#
# Convert the result to word_to_ix data structure
# word_to_ix is a dictionary.  
#    Key is the Chinese word, 
#    Value is the counter of the Key appeared in the poems
#
#    u'\u69cc': 889, u'\u63d0': 911, u'\u7957': 1679, 
#
for sentence in data:
    #print sentence
    for word in sentence:
	#print word
        if word not in word_to_ix:
            word_to_ix[word] = len(word_to_ix)
    #exit(1)
word_to_ix['<EOP>'] = len(word_to_ix)
word_to_ix['<START>'] = len(word_to_ix)

VOCAB_SIZE = len(word_to_ix)

print "VOCAB_SIZE:", VOCAB_SIZE
print "data_size", len(data)



# --------------------------------------
# debug
print word_to_ix['<EOP>']
print word_to_ix['<START>']




a=[]
a.append("校")
print a[0]
#print unicode("校").encode('utf-8')
print u"校".encode('utf-8')

print word_to_ix[u"久"]
print word_to_ix[u"知"]

print json.dumps(word_to_ix, ensure_ascii=False)


#exit(0)
# --------------------------------------

#
#
#


for i in range(len(data)):
    data[i] = toList(data[i])
    #print data[i]
    data[i].append("<EOP>")
# save the word dic for sample method
p.dump(word_to_ix, file('wordDic', 'w'))


#exit(0)

# save all avaible word
# wordList = open('wordList','w')
# for w in word_to_ix:
#     wordList.write(w.encode('utf-8'))
# wordList.close()

model = PoetryModel(len(word_to_ix), 256, 256);

if CUDA_GPU:
    print "GPU CUDA is enabled"
    model.cuda()  # running on GPU,if you want to run it on CPU,delete all .cuda() usage.

optimizer = optim.RMSprop(model.parameters(), lr=0.01, weight_decay=0.0001)
criterion = nn.NLLLoss()

one_hot_var_target = {}
for w in word_to_ix:
    one_hot_var_target.setdefault(w, make_one_hot_vec_target(w, word_to_ix))

epochNum = 10
TRAINSIZE = len(data)
batch = 100
def test():
    v = int(TRAINSIZE / batch)
    loss = 0
    counts = 0
    for case in range(v * batch, min((v + 1) * batch, TRAINSIZE)):
        s = data[case]
        hidden = model.initHidden()
        t, o = makeForOneCase(s, one_hot_var_target)
        if CUDA_GPU:
            output, hidden = model(t.cuda(), hidden)
            loss += criterion(output, o.cuda())
        else:
            output, hidden = model(t, hidden)
            loss += criterion(output, o)
        counts += 1
    loss = loss / counts
    print "=====",loss.data[0]
print "start training"
for epoch in range(epochNum):
    for batchIndex in range(int(TRAINSIZE / batch)):
        model.zero_grad()
        loss = 0
        counts = 0
        for case in range(batchIndex * batch, min((batchIndex + 1) * batch, TRAINSIZE)):
            s = data[case]
            hidden = model.initHidden()
            t, o = makeForOneCase(s, one_hot_var_target)
            if CUDA_GPU:
                output, hidden = model(t.cuda(), hidden)
                loss += criterion(output, o.cuda())
            else:
                output, hidden = model(t, hidden)
                loss += criterion(output, o)
            counts += 1
        loss = loss / counts
        loss.backward()
        print epoch, loss.data[0]
        optimizer.step()
    test()
torch.save(model, 'poetry-gen.pt')
