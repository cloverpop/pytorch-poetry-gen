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
data = dataHandler.parseRawData(author=None, constrain=5)  # All if author=None
#data = dataHandler.parseRawData(author="李白".decode('utf-8'),constrain=5)  # All if author=None
#data = dataHandler.parseRawData(author="杜甫".decode('utf-8'),constrain=5)  # All if author=None
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

# --------------------------------------
#
#  If the unicode beginning is ranged from 0x8Exx,filter it out
#
to_remove_dict = {}

if 0:

	for key,value in word_to_ix.iteritems():
		try:
			if isinstance(key, unicode):
				#print (u"{k}   ->  {v}"  ).format(k=key, v=value),
				pass
			else:
				print(u"find a non-unicode value [%s]"%(key))
		except UnicodeError:
			to_remove_dict[key] = word_to_ix[key]
			print ("Detect a UnicodeError!")
			#print key.encode('utf-8')
			print key
			#print ("Detect a UnicodeError! ..")
		except TypeError:
			print ("Detect a type error!")
			pass
		pass

print ("Original raw dictionary length=[%d]"%(len(word_to_ix)))
print ("Non unicode dictionary length=[%d]"%(len(to_remove_dict)))


#
# Update word_to_ix
#
#for key in to_remove_dict.keys():
for key, value in to_remove_dict.iteritems():
	print "To delete:: key=[u'%s']"%(key)
	del word_to_ix[key]
	
#for key, value in to_remove_dict.iteritems():
	#print unicode(key).encode("utf-8")
	#print "value={}"%(to_remove_dict[key] )
	pass

print ("Filter out non-unicode dict length=[%d]"%(len(word_to_ix)))



# --------------------------------------


word_to_ix['<EOP>'] = len(word_to_ix)
word_to_ix['<START>'] = len(word_to_ix)

VOCAB_SIZE = len(word_to_ix)


#
# Post-process 'data' object
# - Filter out the abnormal characters
#
saved_data = data

for i in range(len(saved_data)):
    flag = 0
    try:
        # an ugly method to access data[] to trigger the UnicodeError exception
        #print( "[%s]"%(data[i]) )
        pass
    except UnicodeError:
        flag = 1

    # if it is abnormal character, remove it   
    if flag:
        del saved_data[i]
    else:    # keep the normal character
        data[i] = toList(data[i])
        #print data[i]
        data[i].append("<EOP>")


# save the word dic for sample method
p.dump(word_to_ix, file('wordDic', 'w'))

#
# save the poems in Chinese characters
#
poemList = open('poemList','w')
#for idx in range(len(saved_data)):
    #print( "[%s]"%(saved_data[idx]) )
    #exit(0)
    #poemList.write( saved_data[idx] )
#    pass
poemList.close()

#exit(0)

print "VOCAB_SIZE:", VOCAB_SIZE
print "data_size", len(data)
print "saved_data_size", len(saved_data)
data = saved_data
print "New data_size", len(data)

# --------------------------------------
#  debug

DEBUG = 0

if DEBUG:
	print word_to_ix['<EOP>']
	print word_to_ix['<START>']

	a=[]
	a.append("校")
	print a[0]
	#print unicode("校").encode('utf-8')
	print u"校".encode('utf-8')

	print word_to_ix[u"久"]
	print word_to_ix[u"知"]

	if u'\u653b' in word_to_ix:
		print u'\u653b'
# --------------------------------------



#
# Output the unicode value
#
#print word_to_ix



#
# Output the Chinese character
#
#print json.dumps(word_to_ix, encoding="utf-8", ensure_ascii=False)
#print json.dumps(word_to_ix,  ensure_ascii=False)

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

#-----------------------------------------------
# Preprocess the poems to filter out the poems that may cause errors during model creation
#
print("Original len(data)=[%d]"%(len(data))), 

filtered_data = data
error_times = 0
for case in range(len(data))[::-1]:
        counts = 0
        s = data[case]
        t, o = makeForOneCase(s, one_hot_var_target)
        # if makeForOneCase returns invalid value, skip
        if (len(t) == 0) and (len(o) == 0) :
            error_times += 1
            # now we have to remove the errarous poem
            del filtered_data[case]
            print("Delte data[%d]"%(case))
print("Bad poems=[%d]"%(error_times))

data = filtered_data
print("Remained len(data)=[%d] fileter_data=[%d]"%(len(data), len(filtered_data)))

# re-calculate the TRAINSIZE
TRAINSIZE = len(data)
print("New TRAINSIZE=[%d] word_to_ix len=[%d]"%(TRAINSIZE, len(word_to_ix)))

# reset the variables
one_hot_var_target = {}
for w in word_to_ix:
    one_hot_var_target.setdefault(w, make_one_hot_vec_target(w, word_to_ix))

#-----------------------------------------------
# Execute the test case for each batch data
#
def test():
    v = int(TRAINSIZE / batch)
    loss = 0
    counts = 0
    error_times = 0
    for case in range(v * batch, min((v + 1) * batch, TRAINSIZE)):
        s = data[case]
        hidden = model.initHidden()
        t, o = makeForOneCase(s, one_hot_var_target)

        # if makeForOneCase returns invalid value, skip
        if len(t) == 0 and len(o) == 0:
            error_times += 1
            continue

        if CUDA_GPU:
            output, hidden = model(t.cuda(), hidden)
            loss += criterion(output, o.cuda())
        else:
            output, hidden = model(t, hidden)
            loss += criterion(output, o)

        # if makeForOneCase returns invalid value, don't inc counts
        if (len(t) != 0) and (len(o) != 0) :
            counts += 1

    if error_times > 0:
       print("[train.py::test()] -> skip [%d] times"%(error_times))

    loss = loss / counts
    #print "=====",loss.data[0]
    print "=====",loss.item()

#-----------------------------------------------

print "start training"

for epoch in range(epochNum):
    for batchIndex in range(int(TRAINSIZE / batch)):
        model.zero_grad()
        loss = 0
        counts = 0
        error_times = 0
        for case in range(batchIndex * batch, min((batchIndex + 1) * batch, TRAINSIZE)):
            s = data[case]
            hidden = model.initHidden()
            t, o = makeForOneCase(s, one_hot_var_target)

            # if makeForOneCase returns invalid value, skip
            if (len(t) == 0) and (len(o) == 0) :
                error_times += 1
                continue

            if CUDA_GPU:
                output, hidden = model(t.cuda(), hidden)
                loss += criterion(output, o.cuda())
            else:
                output, hidden = model(t, hidden)
                loss += criterion(output, o)
                #print("[train.py::main] hidden=[%d]"%(hidden))
                #print "hidden", hidden

            # if makeForOneCase returns invalid value, don't inc counts
            if (len(t) != 0) and (len(o) != 0) :
                counts += 1

        if error_times > 0:
            print("[train.py::main()] -> skip [%d] times"%(error_times))

        loss = loss / counts
        loss.backward()
        #print epoch, " batch[%d]"%(batchIndex), loss.data[0]
        print epoch, " batch[%d]"%(batchIndex), loss.item()
        optimizer.step()
    test()

torch.save(model, 'poetry-gen.pt')
