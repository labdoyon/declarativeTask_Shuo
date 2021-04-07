import sys

from config import dataFolder
from expyriment.misc import data_preprocessing
import numpy as np

agg = data_preprocessing.Aggregator(data_folder=dataFolder,
                                    file_name=sys.argv[1])

print 'Variable computed: '
data = {}
for variable in agg.variables:
    data[variable] = agg.get_variable_data(variable)

indexBlocks = np.unique(data['NBlock'])

for block in indexBlocks:
    print 'Block {}'.format(block)
    correctAnswers = np.logical_and(data['Picture']==data['Answers'], data['NBlock']==block)
    wrongAnswers = np.logical_and(data['Picture']!=data['Answers'], data['NBlock']==block)
    correctRT = [int(i) for i in data['RT'][correctAnswers]]
    print 'Correct answers: {}'.format(len(correctRT))
    print 'Mean correct RT: {} ms'.format(np.mean(correctRT))