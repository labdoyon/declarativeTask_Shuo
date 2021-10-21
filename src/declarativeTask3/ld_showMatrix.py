import ast
import sys

import numpy as np
from expyriment import control, stimuli, io, design, misc

from declarativeTask3.ld_matrix import LdMatrix
from declarativeTask3.config import *

control.defaults.window_mode = windowMode
control.defaults.window_size = windowSize


arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject

dataFile = arguments[0]

agg = misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
header = agg[3].split('\n#e ')
previousMatrix = ast.literal_eval(header[-1].split('\n')[0].split('\n')[0])

exp = design.Experiment(dataFile)  # Save experiment name

m = LdMatrix(matrixSize, windowSize)  # Create Matrix

control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

m.associatePictures(previousMatrix)  # Associate Pictures to cards
bs = stimuli.BlankScreen(bgColor)  # Create blank screen
bs = m.plotDefault(bs,False)

''' Presentation all locations '''
presentationOrder = np.array(range(m.size[0]*m.size[1]))
removeCards.sort(reverse=True)
for nCard in removeCards:
    presentationOrder = np.delete(presentationOrder, nCard)
presentationOrder = np.random.permutation(presentationOrder)
presentationOrder = presentationOrder.tolist()

for nCard in presentationOrder:
    bs = m.plotCard(nCard, True, bs, False)

bs.present()
kb=io.Keyboard()
kb.wait(keys=misc.constants.K_q)

