import sys

import numpy as np
from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants
from expyriment.misc._timer import get_time

from ld_matrix import LdMatrix
from ld_utils import setCursor, newRandomPresentation, readMouse, path_leaf
from ttl_catch_keyboard import wait_for_ttl_keyboard
from config import *

if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject

experimentName = arguments[0]
subjectName = arguments[1]

exp = design.Experiment(experimentName)  # Save experiment name
exp.add_experiment_info(['Subject: '])  # Save Subject Code
exp.add_experiment_info([subjectName])  # Save Subject Code

# Save time, nblocks, position, correctAnswer, RT
exp.add_data_variable_names(['Time', 'NBlock', 'Picture', 'Answers', 'RT'])

m = LdMatrix(matrixSize, windowSize)  # Create Matrix

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], m.gap * 2 + cardSize[1]), position=(
    0, -windowSize[1]/float(2) + (2 * m.gap + cardSize[1])/float(2)), colour=constants.C_DARKGREY)

picturesExamples = np.random.permutation(picturesExamples)

presentationOrder = newRandomPresentation()
presentationOrder = presentationOrder[0:3]

control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

nPict = 0
for nCard in presentationOrder:
    m._matrix.item(nCard).setPicture(picturesExamplesFolder + picturesExamples[nPict])
    nPict += 1

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

setCursor(arrow)

bs = stimuli.BlankScreen(bgColor)  # Create blank screen
m.plotDefault(bs, True)  # Draw default grid

exp.clock.wait(shortRest)

wait_for_ttl_keyboard()

exp.add_experiment_info(['Block {} - Presentation'.format(0)])  # Add listPictures
exp.add_experiment_info(str(list(presentationOrder)))  # Add listPictures

instructions = stimuli.TextLine(' PRESENTATION ',
                                position=(0, -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                text_underline=None, text_colour=textColor,
                                background_colour=bgColor,
                                max_width=None)
instructionRectangle.plot(bs)
instructions.plot(bs)
bs.present(False, True)

exp.clock.wait(shortRest)  # Short Rest between presentation and cue-recall

instructionRectangle.plot(bs)
bs.present(False, True)

exp.clock.wait(shortRest)

for nCard in presentationOrder:
    mouse.hide_cursor(True, True)
    m.plotCard(nCard, True, bs, True)  # Show Location for ( 2s )
    exp.clock.wait(presentationCard)
    m.plotCard(nCard, False, bs, True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI)

presentationOrder = np.random.permutation(presentationOrder)
exp.clock.wait(shortRest)  # Short Rest between presentation and cue-recall

instructions = stimuli.TextLine(' TEST ',
                                position=(0, -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                text_underline=None, text_colour=textColor,
                                background_colour=bgColor,
                                max_width=None)
instructionRectangle.plot(bs)
instructions.plot(bs)
bs.present(False, True)

exp.clock.wait(shortRest)  # Short Rest between presentation and cue-recall

instructionRectangle.plot(bs)
bs.present(False, True)

correctAnswers = 0

exp.add_experiment_info(['Block {} - Test'.format(0)])  # Add listPictures
exp.add_experiment_info(str(list(presentationOrder)))  # Add listPictures

for nCard in presentationOrder:

    m._cueCard.setPicture(m._matrix.item(nCard).stimuli[0].filename)  # Associate Picture to CueCard

    m.plotCueCard(True, bs, True)  # Show Cue

    exp.clock.wait(presentationCard)  # Wait presentationCard

    m.plotCueCard(False, bs, True)  # Hide Cue

    mouse.show_cursor(True, True)

    start = get_time()
    rt, position = readMouse(start, mouseButton, responseTime)

    mouse.hide_cursor(True, True)

    if rt is not None:

        currentCard = m.checkPosition(position)

        if currentCard is not None:
            m._matrix.item(currentCard).color = clickColor
            m.plotCard(currentCard, False, bs, True)

            exp.clock.wait(clicPeriod)  # Wait 500ms

            m._matrix.item(currentCard).color = cardColor
            m.plotCard(currentCard, False, bs, True)

        if currentCard == nCard:
            correctAnswers += 1
            exp.data.add([exp.clock.time, 0,
                          path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                          path_leaf(m._matrix.item(currentCard).stimuli[0].filename),
                          rt])

        elif currentCard is None:
            exp.data.add([exp.clock.time, 0,
                          path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                          None,
                          rt])
        else:
            exp.data.add([exp.clock.time, 0,
                          path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                          path_leaf(m._matrix.item(currentCard).stimuli[0].filename),
                          rt])
    else:
        exp.data.add([exp.clock.time, 0,
                      path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                      None,
                      rt])

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI)


if correctAnswers == 3:
    instructions = stimuli.TextLine(' PERFECT ',
                                    position=(0, -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
    instructions.plot(bs)
    bs.present(False, True)

    exp.clock.wait(responseTime)


