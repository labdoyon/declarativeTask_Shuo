import sys
import os

import numpy as np
from expyriment import control, stimuli, io, design, misc

from declarativeTask3.ld_matrix import LdMatrix
from declarativeTask3.config import *
from declarativeTask3.ld_utils import getPreviousMatrix

control.defaults.window_mode = windowMode
control.defaults.window_size = windowSize

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject

experimentName = arguments[0]
subjectName = arguments[1]

previousMatrix = getPreviousMatrix(subjectName, 0, 'ses-ExpD1_task-Learn-1stClass')


exp = design.Experiment(experimentName)  # Save experiment name

session_dir = os.path.normpath(os.path.join('sourcedata', 'sub-' + subjectName))
output_dir = session_dir
io.defaults.datafile_directory = output_dir
io.defaults.eventfile_directory = output_dir

m = LdMatrix(matrixSize, windowSize)  # Create Matrix

control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

m.associatePictures(previousMatrix)  # Associate Pictures to cards
bs = stimuli.BlankScreen(bgColor)  # Create blank screen
bs = m.plotDefault(bs, False)

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