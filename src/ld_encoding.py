import sys

import numpy as np
from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants
from expyriment.misc._timer import get_time

from ld_matrix import LdMatrix
from ld_utils import newSoundAllocation, getPreviousSoundsAllocation
from ld_utils import setCursor, newRandomPresentation, getPreviousMatrix, path_leaf, readMouse
from ld_sound import create_temp_sound_files
from config import *
from ttl_catch_keyboard import wait_for_ttl_keyboard


if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

if debug:
    control.set_develop_mode(True)

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject
# arguments = ['Encoding', 'test']
experimentName = arguments[0]
subjectName = arguments[1]

exp = design.Experiment(experimentName)  # Save experiment name
exp.add_experiment_info('Subject: ')
exp.add_experiment_info(subjectName)

# Save time, nblocks, position, correctAnswer, RT
exp.add_data_variable_names(['Time', 'NBlock', 'Picture', 'Answers', 'RT'])

if experimentName == 'Encoding':
    previousMatrix = None
    keepMatrix = True
    keepSoundsAllocation = True

exp.add_experiment_info('Image categories (original order; src/config.py order): ')
exp.add_experiment_info(str(classPictures))

# classPicturesPresentationOrder = list(np.random.permutation(classPictures))
matrix = []
newMatrix = []
for i, category in enumerate(classPictures):
    matrix.append(LdMatrix(matrixSize, windowSize))  # Create Matrix
    newMatrix.append(matrix[i].findMatrix(category, previousMatrix, keepMatrix))  # Find newMatrix
    matrix[i].associateCategory(category)

control.initialize(exp)

for i, category in enumerate(classPictures):
    matrix[i].associatePictures(newMatrix[i], picturesFolder=picturesFolderClass[category])  # Associate Pictures to cards
    exp.add_experiment_info('matrix {}, pictures from class {}:'.format(i, category))
    exp.add_experiment_info(str(matrix[i].listPictures))  # Add listPictures

previousSoundAllocation = getPreviousSoundsAllocation(subjectName, 0, 'DayOne-Learning')

if not previousSoundAllocation or not keepSoundsAllocation:
    soundsAllocation_index, soundsAllocation = newSoundAllocation()
else:
    soundsAllocation_index = previousSoundAllocation

exp.add_experiment_info('Image classes order:')
exp.add_experiment_info(str(classPictures))
exp.add_experiment_info('Sounds order:')
exp.add_experiment_info(str(sounds))
exp.add_experiment_info('Image classes to sounds:')
exp.add_experiment_info(str(soundsAllocation))
exp.add_experiment_info(str(soundsAllocation_index))

soundsVolumeAdjustmentIndB = create_temp_sound_files(subjectName)
exp.add_experiment_info('Sounds Volume adjustment (in dB):')
exp.add_experiment_info(str(soundsVolumeAdjustmentIndB))
if soundsVolumeAdjustmentIndB != [0, 0, 0]:
    volumeAdjusted = True
else:
    volumeAdjusted = False

control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)
exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

setCursor(arrow)

bs = stimuli.BlankScreen(bgColor)  # Create blank screen

exp.clock.wait(shortRest)

correctAnswers = np.zeros(nbBlocksMax)
currentCorrectAnswers = 0
nBlock = 0

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], matrix[0].gap * 2 + cardSize[1]), position=(
    0, -windowSize[1]/float(2) + (2 * matrix[0].gap + cardSize[1])/float(2)), colour=constants.C_DARKGREY)

''' Presentation all locations '''
presentationOrder = newRandomPresentation()

instructions_ttl = stimuli.TextLine(' PLEASE INPUT TTL ',
                                    position=(
                                    0, -windowSize[1] / float(2) + (2 * matrix[0].gap + cardSize[1]) / float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
instructionRectangle.plot(bs)
instructions_ttl.plot(bs)
bs.present(False, True)

wait_for_ttl_keyboard()
exp.add_experiment_info(['TTL_RECEIVED_timing_{}'.format(exp.clock.time)])

instructionRectangle.plot(bs)
bs.present(False, True)

while currentCorrectAnswers < correctAnswersMax and nBlock < nbBlocksMax:

    if 1 != nbBlocksMax or experimentName == 'DayOne-PreLearning':
        matrix_presentation_order = list(np.random.permutation(3))
        exp.add_experiment_info('Presentation_Block_{}_timing_{}'.format(nBlock, exp.clock.time))
        instructions = stimuli.TextLine(' PRESENTATION ',
                                        position=(0, -windowSize[1]/float(2) + (2*matrix[0].gap + cardSize[1])/float(2)),
                                        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                        text_underline=None, text_colour=textColor,
                                        background_colour=bgColor,
                                        max_width=None)
        instructionRectangle.plot(bs)
        instructions.plot(bs)
        bs.present(False, True)

        exp.clock.wait(shortRest)
        instructionRectangle.plot(bs)
        bs.present(False, True)

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI)

        # LOG and SYNC: Start Presentation
        exp.add_experiment_info('StartPresentation_Block_{}_timing_{}'.format(nBlock, exp.clock.time))  # Add sync info
        exp.add_experiment_info(
            'Presentation_Block_{}_MatrixPresentationOrder_{}_timing_{}'.format(nBlock, matrix_presentation_order,
                                                                                exp.clock.time))  # Add sync info

        for i in matrix_presentation_order:
            presentationOrder = newRandomPresentation(presentationOrder)
            matrix_i = matrix[i]
            matrix_i.plotDefault(bs, True)

            matrix_presentation_order = list(np.random.permutation(3))
            exp.add_experiment_info('Presentation_Block_{}_matrix_{}_category_{}_timing_{}'.format(
                nBlock, i, matrix_i._category, exp.clock.time))
            exp.add_experiment_info(str(presentationOrder))
            instructions = stimuli.TextLine(' PRESENTATION ' + matrix_i._category,
                                            position=(0, -windowSize[1] / float(2) + (
                                                        2 * matrix[0].gap + cardSize[1]) / float(2)),
                                            text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                            text_underline=None, text_colour=textColor,
                                            background_colour=bgColor,
                                            max_width=None)
            instructionRectangle.plot(bs)
            instructions.plot(bs)
            bs.present(False, True)

            exp.clock.wait(shortRest)
            instructionRectangle.plot(bs)
            bs.present(False, True)

            ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
            exp.clock.wait(ISI)

            for nCard in presentationOrder:
                mouse.hide_cursor(True, True)
                matrix_i.plotCard(nCard, True, bs, True)  # Show Location for ( 2s )
                matrix_i.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
                exp.add_experiment_info('ShowCard_pos_{}_card_{}_timing_{}_sound_{}'.format(
                    nCard, matrix_i.listPictures[nCard], exp.clock.time,
                    sounds[soundsAllocation_index[matrix_i._category]]))

                exp.clock.wait(presentationCard)
                matrix_i.plotCard(nCard, False, bs, True)
                exp.add_experiment_info('HideCard_pos_{}_card_{}_timing_{}'.format(
                    nCard, matrix_i.listPictures[nCard], exp.clock.time))  # Add sync info

                ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
                exp.clock.wait(ISI)

            exp.clock.wait(shortRest)

    instructions = stimuli.TextLine(' TEST ',
                                    position=(0, -windowSize[1] / float(2) + (2 * matrix[0].gap + cardSize[1]) / float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
    instructionRectangle.plot(bs)
    instructions.plot(bs)
    bs.present(False, True)

    # LOG and SYNC Start Test
    exp.add_experiment_info(['StartTest_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info

    exp.clock.wait(shortRest)  # Short Rest between presentation and cue-recall

    instructionRectangle.plot(bs)
    bs.present(False, True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI)

    ''' Cue Recall '''
    exp.add_experiment_info(['Block {} - Test'.format(nBlock)])  # Add listPictures
    exp.add_experiment_info(
        'Test_Block_{}_MatrixPresentationOrder_{}_timing_{}'.format(nBlock, matrix_presentation_order,
                                                                            exp.clock.time))  # Add sync info

    matrix_presentation_order = list(np.random.permutation(3))
    for i in matrix_presentation_order:
        matrix_i = matrix[i]
        presentationOrder = newRandomPresentation(presentationOrder)
        exp.add_experiment_info('Test_Block_{}_matrix_{}_category_{}_timing_{}'.format(
            nBlock, i, matrix_i._category, exp.clock.time))
        exp.add_experiment_info(str(presentationOrder))

        for nCard in presentationOrder:

            matrix_i._cueCard.setPicture(matrix_i._matrix.item(nCard).stimuli[0].filename)  # Associate Picture to CueCard

            matrix_i.plotCueCard(True, bs, True)  # Show Cue
            # LOG and SYNC show cue card
            exp.add_experiment_info(['ShowCueCard_pos_{}_card_{}_timing_{}'.format(nCard, matrix_i.listPictures[nCard],
                                                                                   exp.clock.time)])  # Add sync info

            exp.clock.wait(presentationCard)  # Wait presentationCard

            matrix_i.plotCueCard(False, bs, True)  # Hide Cue
            # LOG and SYNC hide cue card
            exp.add_experiment_info(['HideCueCard_pos_{}_card_{}_timing_{}'.format(nCard, matrix_i.listPictures[nCard],
                                                                                   exp.clock.time)])  # Add sync info

            mouse.show_cursor(True, True)

            start = get_time()
            rt, position = readMouse(start, mouseButton, responseTime)

            mouse.hide_cursor(True, True)
            if rt is not None:

                currentCard = matrix_i.checkPosition(position)

                # LOG and SYNC Response
                try:
                    exp.add_experiment_info(['Response_pos_{}_card_{}_timing_{}'.format(currentCard,
                                                                                        matrix_i.listPictures[currentCard],
                                                                                        exp.clock.time)])  # Add sync info
                except:
                    exp.add_experiment_info(
                        ['Response_pos_{}_ERROR_timing_{}'.format(currentCard, exp.clock.time)])  # Add sync info

                if currentCard is not None and currentCard not in removeCards:
                    matrix_i._matrix.item(currentCard).color = clickColor
                    matrix_i.plotCard(currentCard, False, bs, True)

                    exp.clock.wait(clicPeriod)  # Wait 200ms

                    matrix_i._matrix.item(currentCard).color = cardColor
                    matrix_i.plotCard(currentCard, False, bs, True)

                if currentCard == nCard:
                    correctAnswers[nBlock] += 1
                    exp.data.add([exp.clock.time, nBlock,
                                  path_leaf(matrix_i._matrix.item(nCard).stimuli[0].filename),
                                  path_leaf(matrix_i._matrix.item(currentCard).stimuli[0].filename),
                                  rt])

                elif currentCard is None:
                    exp.data.add([exp.clock.time, nBlock,
                                  path_leaf(matrix_i._matrix.item(nCard).stimuli[0].filename),
                                  None,
                                  rt])

                else:
                    exp.data.add([exp.clock.time, nBlock,
                                  path_leaf(matrix_i._matrix.item(nCard).stimuli[0].filename),
                                  path_leaf(matrix_i._matrix.item(currentCard).stimuli[0].filename),
                                  rt])
            else:
                exp.data.add([exp.clock.time, nBlock,
                              path_leaf(matrix_i._matrix.item(nCard).stimuli[0].filename),
                              None,
                              rt])

                # LOG and SYNC Response
                exp.add_experiment_info(['NoResponse'])  # Add sync info

            ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
            exp.clock.wait(ISI)

    currentCorrectAnswers = correctAnswers[nBlock]  # Number of correct answers

control.end()
