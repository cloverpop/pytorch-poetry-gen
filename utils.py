import torch
import torch.autograd as autograd


def make_one_hot_vec(word, word_to_ix):
    rst = torch.zeros(1, 1, len(word_to_ix))
    rst[0][0][word_to_ix[word]] = 1
    return autograd.Variable(rst)


def make_one_hot_vec_target(word, word_to_ix):
    rst = autograd.Variable(torch.LongTensor([word_to_ix[word]]))
    return rst


def prepare_sequence(seq, word_to_ix):
    idxs = [word_to_ix[w] for w in seq]
    tensor = torch.LongTensor(idxs)
    return autograd.Variable(tensor)


def toList(sen):
    rst = []
    for s in sen:
        rst.append(s)
    return rst


def makeForOneCase(s, one_hot_var_target):
    tmpIn = []
    tmpOut = []
    count = 0
    for i in range(1, len(s)):
        w = s[i]
        w_b = s[i - 1]

        flag_normal = 1
        try:
            tmpIn.append(one_hot_var_target[w_b])
        except KeyError:
            count += 1
            #print("Ignore KeyError")
            flag_normal = 0
            pass

        # if it is normal character without exception, tmpOut appends
        if flag_normal:
            tmpOut.append(one_hot_var_target[w])

    if count > 0:
        print("[makeForOneCase] -> Ignore KeyError [%d] times"%(count))
        #print(u"[makeForOneCase] s=[%s]"%(s) )

    # Sanity check because torch.cat only accepts non-empty list
    if len(tmpIn) == 0 or len(tmpOut) == 0:
        return tmpIn, tmpOut
    else:
        return torch.cat(tmpIn), torch.cat(tmpOut)
