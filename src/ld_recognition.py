import sys

import numpy as np
from expyriment import control, stimuli, io, design, misc
from expyriment.misc._timer import get_time

from ld_matrix import LdMatrix
from ld_utils import setCursor, getPreviousMatrix, newRandomPresentation, readMouse, getPreviousSoundsAllocation
from ttl_catch_keyboard import wait_for_ttl_keyboard
from config import *

from ld_sound import create_temp_sound_files, delete_temp_files

if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

m = LdMatrix(matrixSize, windowSize)  # Create Matrix

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject

experimentName = arguments[0]
subjectName = arguments[1]

exp = design.Experiment(experimentName)  # Save experiment name
exp.add_experiment_info('Subject: ')  # Save Subject Code
exp.add_experiment_info([subjectName])  # Save Subject Code

# Save time, Response, correctAnswer, RT
exp.add_data_variable_names(['Time', 'Matrix', 'CorrectAnswer', 'RT'])

exp.add_experiment_info('Learning: ')  # Save Subject Code
learningMatrix = getPreviousMatrix(subjectName, 0, 'DayOne-Learning')
exp.add_experiment_info(str(learningMatrix))  # Add listPictures

# interferenceMatrix = getPreviousMatrix(subjectName, 0, 'DayTwo-Interference')

exp.add_experiment_info('RandomMatrix: ')  # Save Subject Code
randomMatrix = m.newRecognitionMatrix(learningMatrix)

exp.add_experiment_info(str(randomMatrix))  # Add listPictures

exp.add_experiment_info('Image classes order:')
exp.add_experiment_info(str(classPictures))
exp.add_experiment_info('Sounds order:')
exp.add_experiment_info(str(sounds))

soundsAllocation = getPreviousSoundsAllocation(subjectName, 0, 'DayOne-Learning')
exp.add_experiment_info('Image classes to sounds:')
exp.add_experiment_info(str(soundsAllocation))

soundsVolumeAdjustmentIndB = create_temp_sound_files(subjectName)
exp.add_experiment_info('Sounds Volume adjustment (in dB):')
exp.add_experiment_info(str(soundsVolumeAdjustmentIndB))
if soundsVolumeAdjustmentIndB != [0, 0, 0]:
    volumeAdjusted = True
else:
    volumeAdjusted = False

exp.add_experiment_info('Presentation Order: ')  # Save Presentation Order

presentationMatrixLearningOrder = newRandomPresentation()
presentationMatrixLearningOrder = np.vstack((presentationMatrixLearningOrder, np.zeros(m.size[0]*m.size[1]-len(removeCards))))

presentationMatrixRandomOrder = newRandomPresentation(presentationMatrixLearningOrder)
presentationMatrixRandomOrder = np.vstack((presentationMatrixRandomOrder, np.ones(m.size[0]*m.size[1]-len(removeCards))))

presentationOrder = np.hstack((presentationMatrixLearningOrder, presentationMatrixRandomOrder))

presentationOrder = presentationOrder[:, np.random.permutation(presentationOrder.shape[1])]

listCards = []
for nCard in range(presentationOrder.shape[1]):
    if removeCards:
        removeCards.sort()
        removeCards = np.asarray(removeCards)
        tempPosition = presentationOrder[0][nCard]
        index = 0
        try:
            index = int(np.where(removeCards == max(removeCards[removeCards<tempPosition]))[0]) + 1
        except:
            pass

        position = tempPosition - index

    else:
        position = presentationOrder[0][nCard]

    if presentationOrder[1][nCard] == 0: # Learning Matrix
        listCards.append(learningMatrix[int(position)])
    else:
        listCards.append(randomMatrix[int(position)])

exp.add_experiment_info(str(list(presentationOrder)))  # Add listPictures

control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

# LOG and SYNC
exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

setCursor(arrow)

matrixA = stimuli.TextLine('  Correct location  ',
                           position=(-windowSize[0]/float(4),
                                     -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                           text_size=textSize,
                           text_colour=textColor,
                           background_colour=cardColor)

matrixARectangle = stimuli.Rectangle(size=matrixA.surface_size, position=matrixA.position,
                                     colour=cardColor)

matrixNone = stimuli.TextLine('  Wrong location  ',
                            position=(windowSize[0]/float(4),
                                      -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                            text_size=textSize,
                            text_colour=textColor,
                            background_colour=cardColor)

matrixNoneRectangle = stimuli.Rectangle(size=matrixNone.surface_size, position=matrixNone.position,
                                     colour=cardColor)


bs = stimuli.BlankScreen(bgColor)  # Create blank screen
bs = m.plotDefault(bs)  # Draw default grid
matrixARectangle.plot(bs)
matrixA.plot(bs)
matrixNone.plot(bs)
m._cueCard.color = bgColor
bs = m.plotCueCard(False, bs)

bs.present(False, True)

ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
exp.clock.wait(ISI)

wait_for_ttl_keyboard()
exp.add_experiment_info(['TTL_RECEIVED_timing_{}'.format(exp.clock.time)])


for nCard in range(presentationOrder.shape[1]):
    locationCard = int(presentationOrder[0][nCard])

    if bool(presentationOrder[1][nCard] == 0):
        showMatrix = 'MatrixA'
    else:
        showMatrix = 'MatrixRandom'

    m._matrix.item(locationCard).setPicture(picturesFolder + listCards[nCard])
    picture = listCards[nCard].rstrip(".png")
    for i in range(numberClasses):
        if classPictures[i] in picture:  # if card belongs to the the i-th class of pictures
            # associate this class' sound to the card
            m._matrix.item(locationCard).setSound(soundsAllocation[i])
            break
    m.plotCard(locationCard, True, bs, True)

    m.playSound(locationCard, volumeAdjusted=volumeAdjusted)
    cueSound = sounds[m._matrix.item(locationCard).sound]
    exp.add_experiment_info(['ShowCard_pos_{}_card_{}_timing_{}_sound_{}'.format(locationCard,
                                                                                 listCards[nCard],
                                                                                 exp.clock.time,
                                                                                 cueSound)])  # Add sync info

    exp.clock.wait(presentationCard)
    m.plotCard(locationCard, False, bs, True)
    exp.add_experiment_info(['HideCard_pos_{}_card_{}_timing_{}'.format(locationCard,
                                                                        listCards[nCard],
                                                                        exp.clock.time)])  # Add sync info

    mouse.show_cursor(True, True)

    start = get_time()
    rt, position = readMouse(start, mouseButton, responseTime)

    mouse.hide_cursor(True, True)

    if rt is not None:
        if matrixARectangle.overlapping_with_position(position):
            exp.data.add([exp.clock.time, showMatrix, bool(presentationOrder[1][nCard] == 0), rt])
            matrixA = stimuli.TextLine('  Correct location  ',
                                          position=(-windowSize[0]/float(4),
                                                    -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                          text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                          text_underline=None, text_colour=textColor,
                                          background_colour=clickColor,
                                          max_width=None)
            matrixA.plot(bs)
            bs.present(False, True)
            exp.clock.wait(clicPeriod)
            matrixA = stimuli.TextLine('  Correct location  ',
                                      position=(-windowSize[0]/float(4),
                                                -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                      text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                      text_underline=None, text_colour=textColor,
                                      background_colour=cardColor,
                                      max_width=None)
            matrixA.plot(bs)
            bs.present(False, True)
            exp.add_experiment_info(['Response_{}_timing_{}'.format('MatrixA', exp.clock.time)])  # Add sync info

        elif matrixNoneRectangle.overlapping_with_position(position):
            exp.data.add([exp.clock.time, showMatrix, bool(presentationOrder[1][nCard]==1), rt])
            matrixNone = stimuli.TextLine('  Wrong location  ',
                                          position=(windowSize[0]/float(4),
                                                    -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                          text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                          text_underline=None, text_colour=textColor,
                                          background_colour=clickColor,
                                          max_width=None)
            matrixNone.plot(bs)
            bs.present(False, True)
            exp.clock.wait(clicPeriod)
            matrixNone = stimuli.TextLine('  Wrong location  ',
                                          position=(windowSize[0]/float(4),
                                                    -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                          text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                          text_underline=None, text_colour=textColor,
                                          background_colour=cardColor,
                                          max_width=None)
            matrixNone.plot(bs)
            bs.present(False, True)
            exp.add_experiment_info(['Response_{}_timing_{}'.format('None', exp.clock.time)])  # Add sync info

        else:
            exp.data.add([exp.clock.time, showMatrix, False, rt])
            exp.add_experiment_info(['Response_{}_timing_{}'.format('NoRT', exp.clock.time)])  # Add sync info
    else:
        exp.data.add([exp.clock.time, showMatrix, False, rt])

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI)

delete_temp_files()

exp.clock.wait(5000)
