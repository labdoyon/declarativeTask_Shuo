import sys
import numpy as np
from time import time

from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants
from expyriment.misc._timer import get_time

from ld_matrix import LdMatrix
from ld_utils import setCursor, newRandomPresentation, getPreviousMatrix, path_leaf, readMouse
from ld_utils import getPreviousSoundsAllocation, newSoundAllocation
from ld_utils import absoluteTime
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

if debug:
    control.set_develop_mode(True)


if len(sys.argv) == 4:  # declarativeTask was executed by relauncher
    arguments = str(''.join(sys.argv[1])).split(',')  # Get arguments - experiment name and subject
    experimentName = arguments[0]
    subjectName = arguments[1]
    subUnitIndex = sys.argv[2]
    suffix = subjectName + '_learning_trial_' + subUnitIndex + '_out_of_' + str(int(numberLearningSubUnits)-1)
    firstTime = int(float(sys.argv[3])*1000)
else:
    arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject
    experimentName = arguments[0]
    subjectName = arguments[1]
    if experimentName == 'DayOne-PreLearning':
        suffix = subjectName + '_PreLearning'
        picturesFolder = rawFolder + 'stimulis' + os.path.sep + 'PreLearning_stimulis' + os.path.sep
    else:
        suffix = None
    firstTime = int(time()*1000)

exp = design.Experiment(experimentName, filename_suffix=suffix)  # Save experiment name

exp.add_experiment_info('Subject: ')  # Save Subject Code
exp.add_experiment_info([subjectName])  # Save Subject Code

# Save time, nblocks, position, correctAnswer, RT
exp.add_data_variable_names(['Time', 'NBlock', 'Picture', 'Answers', 'RT'])

m = LdMatrix(matrixSize, windowSize)  # Create Matrix

if experimentName == 'DayOne-Learning':
    oldListPictures = getPreviousMatrix(subjectName, 0, 'DayOne-Learning')
    if oldListPictures is False:
        oldListPictures = None
    keepSoundsAllocation = True
    keepMatrix = True
    nbBlocksMax = numberBlocksSubUnit
elif experimentName == 'DayOne-TestLearning':
    oldListPictures = getPreviousMatrix(subjectName, 0, 'DayOne-Learning')
    keepMatrix = True
    keepSoundsAllocation = True
    nbBlocksMax = 1
elif experimentName == 'DayOne-TestConsolidation':
    oldListPictures = getPreviousMatrix(subjectName, 0, 'DayOne-Learning')
    keepMatrix = True
    keepSoundsAllocation = True
    nbBlocksMax = 1
elif experimentName == 'DayOne-PreLearning':
    oldListPictures = None
    keepSoundsAllocation = True
    keepMatrix = True
    nbBlocksMax = 1

if oldListPictures is False:
    print(FAIL + "Warning: no old list of pictures found" + ENDC)
    sys.exit()

newMatrix = m.findMatrix(oldListPictures, keepMatrix)  # Find newMatrix

exp.add_experiment_info('Positions pictures:')

control.initialize(exp)

m.associatePictures(newMatrix, picturesFolder)  # Associate Pictures to cards
# CAUTION: PYTHON 2 TO 3 CHANGE: CONSIDER WITH ATTENTION IF RELATED ISSUE OCCURS
exp.add_experiment_info(str(m.listPictures))  # Add listPictures

previousSoundAllocation = getPreviousSoundsAllocation(subjectName, 0, 'DayOne-Learning')

if not previousSoundAllocation or not keepSoundsAllocation:
    soundsAllocation = newSoundAllocation(numberClasses)
else:
    soundsAllocation = previousSoundAllocation

# CAUTION: PYTHON 2 TO 3 CHANGE: CONSIDER WITH ATTENTION IF RELATED ISSUE OCCURS
exp.add_experiment_info('Image classes order:')
exp.add_experiment_info(str(classPictures))
exp.add_experiment_info('Sounds order:')
exp.add_experiment_info(str(sounds))
exp.add_experiment_info('Image classes to sounds:')
exp.add_experiment_info(str(soundsAllocation))

soundsVolumeAdjustmentIndB = create_temp_sound_files(subjectName)
exp.add_experiment_info('Sounds Volume adjustment (in dB):')
exp.add_experiment_info(str(soundsVolumeAdjustmentIndB))
if soundsVolumeAdjustmentIndB != [0, 0, 0]:
    volumeAdjusted = True
else:
    volumeAdjusted = False

m.associateSounds(newMatrix, soundsAllocation)  # Associate Sounds to Cards depending on pictures

control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

setCursor(arrow)

bs = stimuli.BlankScreen(bgColor)  # Create blank screen
m.plotDefault(bs, True)  # Draw default grid

exp.clock.wait(shortRest)

correctAnswers = np.zeros(nbBlocksMax)
currentCorrectAnswers = 0
nBlock = 0

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], m.gap * 2 + cardSize[1]), position=(
    0, -windowSize[1]/float(2) + (2 * m.gap + cardSize[1])/float(2)), colour=constants.C_DARKGREY)

''' Presentation all locations '''
presentationOrder = newRandomPresentation()

while currentCorrectAnswers < correctAnswersMax and nBlock < nbBlocksMax:
    presentationOrder = newRandomPresentation(presentationOrder)

    instructions_ttl = stimuli.TextLine(' PLEASE INPUT TTL ',
                                    position=(0, -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
    instructionRectangle.plot(bs)
    instructions_ttl.plot(bs)
    bs.present(False, True)

    wait_for_ttl_keyboard()
    exp.add_experiment_info(['TTL_RECEIVED_timing_{}'.format(absoluteTime(firstTime))])

    instructionRectangle.plot(bs)
    bs.present(False, True)

    if 1 != nbBlocksMax or experimentName == 'DayOne-PreLearning':
        exp.add_experiment_info(['Block {} - Presentation'.format(nBlock)])  # Add listPictures
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

        exp.clock.wait(shortRest)
        instructionRectangle.plot(bs)
        bs.present(False, True)

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI)

        # LOG and SYNC: Start Presentation
        exp.add_experiment_info(['StartPresentation_{}_{}'.format(nBlock, absoluteTime(firstTime))])  # Add sync info

        for nCard in presentationOrder:
            mouse.hide_cursor(True, True)
            m.plotCard(nCard, True, bs, True)  # Show Location for ( 2s )
            m.playSound(nCard, volumeAdjusted=volumeAdjusted)
            exp.add_experiment_info(['ShowCard_pos_{}_card_{}_timing_{}_sound_{}'.format(nCard, m.returnPicture(nCard),
                                                                                         absoluteTime(firstTime), sounds[
                                                                                             m._matrix.item(
                                                                                                 nCard).sound])])

            exp.clock.wait(presentationCard)
            m.plotCard(nCard, False, bs, True)
            exp.add_experiment_info(['HideCard_pos_{}_card_{}_timing_{}'.format(nCard, m.returnPicture(nCard),
                                                                                absoluteTime(firstTime))])  # Add sync info

            ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
            exp.clock.wait(ISI)

    instructions = stimuli.TextLine(' TEST ',
                                    position=(0, -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
    instructionRectangle.plot(bs)
    instructions.plot(bs)
    bs.present(False, True)

    # LOG and SYNC test start
    exp.add_experiment_info(['StartTest_{}_{}'.format(nBlock, absoluteTime(firstTime))])  # Add sync info

    exp.clock.wait(shortRest)  # Short Rest between presentation and cue-recall

    instructionRectangle.plot(bs)
    bs.present(False, True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI)

    ''' Cue Recall '''
    presentationOrder = newRandomPresentation(presentationOrder)
    exp.add_experiment_info(['Block {} - Test'.format(nBlock)])  # Add listPictures
    exp.add_experiment_info(str(list(presentationOrder)))
    for nCard in presentationOrder:

        m._cueCard.setPicture(m._matrix.item(nCard).stimuli[0].filename)  # Associate Picture to CueCard
        m._cueCard.setSound(m._matrix.item(nCard).sound)  # Associate Sound to CueCard

        m.plotCueCard(True, bs, True)  # Show Cue
        m.playCueSound(volumeAdjusted=volumeAdjusted)
        cueSound = sounds[ m._matrix.item(nCard).sound]
        exp.add_experiment_info(['ShowCueCard_pos_{}_card_{}_timing_{}_sound_{}'.format(nCard,
                                                                                        m.returnPicture(nCard),
                                                                                        absoluteTime(firstTime),
                                                                                        cueSound)])

        exp.clock.wait(presentationCard)  # Wait presentationCard

        m.plotCueCard(False, bs, True)  # Hide Cue
        exp.add_experiment_info(['HideCueCard_pos_{}_card_{}_timing_{}'.format(nCard,
                                                                               m.returnPicture(nCard),
                                                                               absoluteTime(firstTime))])  # Add sync info

        # Mouse Response Block
        time_left = responseTime
        valid_response = False
        while True:
            mouse.show_cursor(True, True)

            start = get_time()
            rt, position = readMouse(start, mouseButton, time_left)

            mouse.hide_cursor(True, True)
            if rt is not None:

                currentCard = m.checkPosition(position)
                try:
                    exp.add_experiment_info(['Response_pos_{}_card_{}_timing_{}'.format(currentCard,
                                                                                        m.returnPicture(currentCard),
                                                                                        absoluteTime(firstTime))])  # Add sync info
                    valid_response = True
                except:
                    exp.add_experiment_info(['Response_pos_{}_ERROR_timing_{}'.format(currentCard,
                                                                                      absoluteTime(firstTime))])  # Add sync info

                if currentCard is not None and currentCard not in removeCards:
                    m._matrix.item(currentCard).color = clickColor
                    m.plotCard(currentCard, False, bs, True)

                    exp.clock.wait(clicPeriod)  # Wait 200ms

                    m._matrix.item(currentCard).color = cardColor
                    m.plotCard(currentCard, False, bs, True)

                if currentCard == nCard:
                    if experimentName == 'DayOne-PreLearning' or experimentName == 'DayOne-Learning':
                        m.playCueSound(volumeAdjusted=volumeAdjusted)
                    correctAnswers[nBlock] += 1
                    exp.data.add([absoluteTime(firstTime), nBlock,
                                  path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                                  path_leaf(m._matrix.item(currentCard).stimuli[0].filename),
                                  rt])

                elif currentCard is None:
                    exp.data.add([absoluteTime(firstTime), nBlock,
                                  path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                                  None,
                                  rt])
                else:
                    exp.data.add([absoluteTime(firstTime), nBlock,
                                  path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                                  path_leaf(m._matrix.item(currentCard).stimuli[0].filename),
                                  rt])
            else:
                exp.data.add([absoluteTime(firstTime), nBlock,
                              path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                              None,
                              rt])
                exp.add_experiment_info(['NoResponse'])  # Add sync info
            if valid_response or rt is None:
                break
            elif rt < time_left - clicPeriod:
                time_left = time_left - clicPeriod - rt
                pass
            else:
                break

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI)

    currentCorrectAnswers = correctAnswers[nBlock]  # Number of correct answers

    #if currentCorrectAnswers < correctAnswersMax and nBlock + 1 < nbBlocksMax:
    if nbBlocksMax != 1 or experimentName == 'DayOne-PreLearning':

        instructions = stimuli.TextLine('You got ' + str(int(correctAnswers[nBlock])) + ' out of ' + str(m._matrix.size-len(removeCards)),
                                        position=(0, -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                        text_underline=None, text_colour=textColor, background_colour=bgColor,
                                        max_width=None)
        instructions.plot(bs)
        bs.present(False, True)

        exp.clock.wait(shortRest)

        instructionRectangle.plot(bs)
        bs.present(False, True)

    instructions = stimuli.TextLine(
        ' REST ',
        position=(0, -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
        text_underline=None, text_colour=textColor, background_colour=bgColor,
        max_width=None)

    instructions.plot(bs)
    bs.present(False, True)

    exp.add_experiment_info(['StartShortRest_block_{}_timing_{}'.format(nBlock, absoluteTime(firstTime))])  # Add sync info

    exp.clock.wait(shortRest)

    exp.add_experiment_info(['EndShortRest_block_{}_timing_{}'.format(nBlock, absoluteTime(firstTime))])  # Add sync info

    instructionRectangle.plot(bs)
    bs.present(False, True)

    exp.add_experiment_info(['StartRest_block_{}_timing_{}'.format(nBlock, absoluteTime(firstTime))])  # Add sync info

    exp.clock.wait(restPeriod)

    exp.add_experiment_info(['EndRest_block_{}_timing_{}'.format(nBlock, absoluteTime(firstTime))])  # Add sync info

    nBlock += 1

exp.add_experiment_info(['Experiment completed without interruption'])

if currentCorrectAnswers >= correctAnswersMax:
    exp.add_experiment_info(['Experiment ended with success'])
exp.add_experiment_info([])

delete_temp_files()

exp.clock.wait(5000)
control.end()
