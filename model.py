import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as F
# import nninit



#
# 0:  No GPU cuda support
# 1:  Use CPU instead of GPU
#
CUDA_GPU = 0


class PoetryModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim):
        super(PoetryModel, self).__init__()
        self.hidden_dim = hidden_dim
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, self.hidden_dim)

        self.linear1 = nn.Linear(self.hidden_dim, vocab_size)
        # self.dropout = nn.Dropout(0.2)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, input, hidden):
        length = input.size()[0]
        embeds = self.embeddings(input).view((length, 1, -1))
        output, hidden = self.lstm(embeds, hidden)
        output = F.relu(self.linear1(output.view(length, -1)))
        # output = self.dropout(output)
        output = self.softmax(output)
        return output, hidden

    def initHidden(self, length=1):
        if CUDA_GPU:
            return (Variable(torch.zeros(length, 1, self.hidden_dim).cuda()),
                Variable(torch.zeros(length, 1, self.hidden_dim)).cuda())
        else:
            #print("length=[%d] hidden_dim=[%d]"%(length, self.hidden_dim))
            return (Variable(torch.zeros(length, 1, self.hidden_dim)),
                Variable(torch.zeros(length, 1, self.hidden_dim)))
        pass


