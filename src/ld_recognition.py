import sys

import numpy as np
from expyriment import control, stimuli, io, design, misc
from expyriment.misc._timer import get_time
from expyriment.misc import constants
from math import floor

from ld_matrix import LdMatrix
from ld_utils import setCursor, getPreviousMatrix, newRandomPresentation, readMouse
from ld_utils import getLanguage
from ttl_catch_keyboard import wait_for_ttl_keyboard
from config import *
from ld_stimuli_names import classNames, ttl_instructions_text, ending_screen_text

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
exp.add_experiment_info(subjectName)  # Save Subject Code
language = str(getLanguage(subjectName, 0, 'choose-language'))
exp.add_experiment_info('language: ')
only_faces = True
exp.add_experiment_info(f'only_faces: {only_faces}')

# Save time, Response, correctAnswer, RT
exp.add_data_variable_names(['Time', 'Matrix', 'CorrectAnswer', 'RT'])

learningMatrix = getPreviousMatrix(subjectName, 0, 'PreLearn')
exp.add_experiment_info('Learning: ')  # Save Subject Code
exp.add_experiment_info(str(learningMatrix))  # Add listPictures
if only_faces:
    local_learning_matrix = [element for index, element in enumerate(learningMatrix) if matrixTemplate[index] < 4]
    exp.add_experiment_info('faces_only_matrix:')
    exp.add_experiment_info(str(local_learning_matrix))  # Add listPictures
else:
    local_learning_matrix = learningMatrix

randomMatrix = m.newRecognitionMatrix(learningMatrix)
exp.add_experiment_info('RandomMatrix: ')  # Save Subject Code
exp.add_experiment_info(str(randomMatrix))  # Add listPictures
if only_faces:
    local_random_matrix = [element for index, element in enumerate(randomMatrix) if matrixTemplate[index] < 4]
    exp.add_experiment_info('faces_only_random_matrix:')
    exp.add_experiment_info(str(local_random_matrix))  # Add listPictures
else:
    local_random_matrix = randomMatrix

exp.add_experiment_info('Image classes order:')
exp.add_experiment_info(str(classPictures))


control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)
mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor
setCursor(arrow)
bs = stimuli.BlankScreen(bgColor)  # Create blank screen

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], m.gap * 2 + cardSize[1]), position=(
    0, -windowSize[1]/float(2) + (2 * m.gap + cardSize[1])/float(2)), colour=constants.C_DARKGREY)
instructions_ttl = stimuli.TextLine(ttl_instructions_text[language],
                                    position=(
                                        0, -windowSize[1] / float(2) + (2 * m.gap + cardSize[1]) / float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
instructionRectangle.plot(bs)
instructions_ttl.plot(bs)
bs.present(False, True)

wait_for_ttl_keyboard()
exp.add_experiment_info(['TTL_RECEIVED_timing_{}'.format(exp.clock.time)])

exp.add_experiment_info('Presentation Order: ')  # Save Presentation Order
center = floor(matrixSize[0] * matrixSize[1] / 2)
removeCards = [center] + \
              [index + 1 if index >= center else index
               for index, category in enumerate(matrixTemplate) if category > 3]
only_faces = True
presentationMatrixLearningOrder = newRandomPresentation(override_remove_cards=removeCards)
presentationMatrixLearningOrder = np.vstack((presentationMatrixLearningOrder, np.zeros(m.size[0]*m.size[1]-len(removeCards))))

presentationMatrixRandomOrder = newRandomPresentation(presentationMatrixLearningOrder, override_remove_cards=removeCards)
presentationMatrixRandomOrder = np.vstack((presentationMatrixRandomOrder, np.ones(m.size[0]*m.size[1]-len(removeCards))))

presentationOrder = np.hstack((presentationMatrixLearningOrder, presentationMatrixRandomOrder))

presentationOrder = presentationOrder[:, np.random.permutation(presentationOrder.shape[1])]

listCards = []
for nCard in range(presentationOrder.shape[1]):
    if len(removeCards):
        removeCards.sort()
        removeCards = np.asarray(removeCards)
        tempPosition = presentationOrder[0][nCard]
        index = 0
        try:
            index = int(np.where(removeCards == max(removeCards[removeCards < tempPosition]))[0]) + 1
        except:
            pass

        position = tempPosition - index

    else:
        position = presentationOrder[0][nCard]

    if presentationOrder[1][nCard] == 0:  # Learning Matrix
        listCards.append(local_learning_matrix[int(position)])
    else:
        listCards.append(local_random_matrix[int(position)])

exp.add_experiment_info(str(list(presentationOrder)))  # Add listPictures

instructions = stimuli.TextLine(' RECOGNITION ',
                                position=(0, -windowSize[1] / float(2) +
                                          (2 * m.gap + cardSize[1]) / float(2)),
                                text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                text_underline=None, text_colour=textColor,
                                background_colour=bgColor,
                                max_width=None)
instructionRectangle.plot(bs)
instructions.plot(bs)
bs.present(False, True)

exp.clock.wait(shortRest, process_control_events=True)
instructionRectangle.plot(bs)
bs.present(False, True)

# LOG and SYNC
exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info


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


bs = m.plotDefault(bs)  # Draw default grid
matrixARectangle.plot(bs)
matrixA.plot(bs)
matrixNone.plot(bs)
m._cueCard.color = bgColor
bs = m.plotCueCard(False, bs)

bs.present(False, True)

for nCard in range(presentationOrder.shape[1]):
    locationCard = int(presentationOrder[0][nCard])

    if bool(presentationOrder[1][nCard] == 0):
        showMatrix = 'MatrixA'
    else:
        showMatrix = 'MatrixRandom'

    category = listCards[nCard][:2]
    m._matrix.item(locationCard).setPicture(picturesFolderClass[category] + listCards[nCard])
    picture = listCards[nCard].rstrip(".png")
    m.plotCard(locationCard, True, bs, True)

    exp.add_experiment_info(
        'ShowCard_pos_{}_card_{}_timing_{}'.format(locationCard,
                                                            listCards[nCard], exp.clock.time))

    exp.clock.wait(presentationCard, process_control_events=True)
    m.plotCard(locationCard, False, bs, True)
    exp.add_experiment_info(['HideCard_pos_{}_card_{}_timing_{}'.format(locationCard,
                                                                        listCards[nCard],
                                                                        exp.clock.time)])  # Add sync info

    time_left = responseTime
    valid_response = False
    rt = 0
    while not valid_response and rt is not None:
        mouse.show_cursor(True, True)

        start = get_time()
        rt, position = readMouse(start, mouseButton, time_left)  # time_left instead of response tine

        mouse.hide_cursor(True, True)

        if rt is not None:
            if matrixARectangle.overlapping_with_position(position):
                valid_response = True
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
                exp.clock.wait(clicPeriod, process_control_events=True)
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
                valid_response = True
                exp.data.add([exp.clock.time, category, showMatrix, bool(presentationOrder[1][nCard] == 1), rt])
                matrixNone = stimuli.TextLine('  Wrong location  ',
                                              position=(windowSize[0]/float(4),
                                                        -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                              text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                              text_underline=None, text_colour=textColor,
                                              background_colour=clickColor,
                                              max_width=None)
                matrixNone.plot(bs)
                bs.present(False, True)
                exp.clock.wait(clicPeriod, process_control_events=True)
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
        if rt is not None:
            if rt < time_left - clicPeriod:
                time_left = time_left - clicPeriod - rt
            else:
                exp.data.add([exp.clock.time, showMatrix, False, rt])
                exp.add_experiment_info(['Response_{}_timing_{}'.format('NoRT', exp.clock.time)])  # Add sync info
                break

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)

instructions = stimuli.TextLine(
    ending_screen_text[language],
    position=(0, -windowSize[1] / float(2) + (2 * m.gap + cardSize[1]) / float(2)),
    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
    text_underline=None, text_colour=textColor, background_colour=bgColor,
    max_width=None)

instructions.plot(bs)
bs.present(False, True)
exp.clock.wait(thankYouRest, process_control_events=True)
instructionRectangle.plot(bs)
bs.present(False, True)
