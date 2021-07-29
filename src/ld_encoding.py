import sys

import numpy as np
from math import floor
from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants
from expyriment.misc._timer import get_time

from ld_matrix import LdMatrix
from ld_utils import getPreviousSoundsAllocation, getPreviousMatrixOrder, normalize_test_presentation_order
from ld_utils import setCursor, newRandomPresentation, getPreviousMatrix, getLanguage, path_leaf, readMouse
from ld_utils import getPlacesOrFacesChoice
# from ld_sound import create_temp_sound_files, delete_temp_files
from config import *
from ttl_catch_keyboard import wait_for_ttl_keyboard
from ld_stimuli_names import classNames, ttl_instructions_text, presentation_screen_text, rest_screen_text, \
    ending_screen_text, choose_image_text, choose_position_text

if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

if debug:
    control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=True)

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject
experimentName = arguments[0]
subjectName = arguments[1]

exp = design.Experiment(experimentName)  # Save experiment name
exp.add_experiment_info('Subject: ')
exp.add_experiment_info(subjectName)
language = str(getLanguage(subjectName, 0, 'choose-language'))
exp.add_experiment_info('language: ')
exp.add_experiment_info(language)  # Save Subject Code
faces_places_choice = getPlacesOrFacesChoice(subjectName, 0, 'choose-faces-places')
exp.add_experiment_info('start_by_class1_or_class2:')
exp.add_experiment_info(faces_places_choice)
exp.add_experiment_info('start_by_faces_or_places (same as above but explicit):')
exp.add_experiment_info(supported_start_by_choices_explicit[faces_places_choice])

center = floor(matrixSize[0] * matrixSize[1] / 2)
if experiment_use_faces_or_places[faces_places_choice][experimentName] == 'faces':
    only_faces = True
    only_places = False
    exp.add_experiment_info('faces_or_places_for_this_experiment:')
    exp.add_experiment_info('faces')
    exp.add_experiment_info(faces_places_choice)  # Save Subject Code
    removeCards = [center] + \
                  [index + 1 if index >= center else index
                   for index, category in enumerate(matrixTemplate) if category > 3]
elif experiment_use_faces_or_places[faces_places_choice][experimentName] == 'places':
    only_faces = False
    only_places = True
    exp.add_experiment_info('faces_or_places_for_this_experiment:')
    exp.add_experiment_info('places')
    removeCards = [center] + \
                  [index + 1 if index >= center else index
                   for index, category in enumerate(matrixTemplate) if category <= 3]

# Save time, nblocks, position, correctAnswer, RT
exp.add_data_variable_names(['Time', 'NBlock', 'Picture', 'Answers', 'RT'])

keepMatrix = True
keepPreviousMatrix = True
if experimentName == 'PreLearn':
    keepPreviousMatrix = True
elif 'PreTest' in experimentName or 'PostTest' in experimentName:
    keepPreviousMatrix = True
    nbBlocksMax = 1
elif 'PostLearn' in experimentName:
    keepPreviousMatrix = True

m = LdMatrix(matrixSize, windowSize, override_remove_cards=removeCards)  # Create Matrix

if keepPreviousMatrix:
    previousMatrix = getPreviousMatrix(subjectName, 0, 'PreLearn')
else:
    previousMatrix = None
newMatrix = m.findMatrix(previousMatrix, keepMatrix)  # Find newMatrix

exp.add_experiment_info('Image categories (original order; src/config.py order): ')
exp.add_experiment_info(str(classPictures))
control.initialize(exp)

exp.add_experiment_info('Positions pictures:')
exp.add_experiment_info(str(newMatrix))  # Add listPictures

if only_faces:
    local_matrix = [element for index, element in enumerate(newMatrix) if matrixTemplate[index] < 4]
elif only_places:
    local_matrix = [element for index, element in enumerate(newMatrix) if matrixTemplate[index] > 3]
else:
    local_matrix = newMatrix

m.associatePictures(local_matrix)  # Associate Pictures to cards
if only_faces:
    exp.add_experiment_info('faces_only_matrix:')
    exp.add_experiment_info(str(m.listPictures))  # Add listPictures
elif only_places:
    exp.add_experiment_info('places_only_matrix:')
    exp.add_experiment_info(str(m.listPictures))  # Add listPictures

exp.add_experiment_info('Image classes order:')
exp.add_experiment_info(str(classPictures))

control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)
exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

setCursor(arrow)

bs = stimuli.BlankScreen(bgColor)  # Create blank screen

exp.clock.wait(shortRest, process_control_events=True)

correctAnswers = np.zeros(nbBlocksMax)
currentCorrectAnswers = 0
nBlock = 0

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], m.gap * 2 + cardSize[1]), position=(
    0, -windowSize[1]/float(2) + (2 * m.gap + cardSize[1])/float(2)), colour=constants.C_DARKGREY)

''' Presentation all locations '''
presentationOrder = newRandomPresentation(override_remove_cards=removeCards)

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

instructionRectangle.plot(bs)
bs.present(False, True)

while currentCorrectAnswers < correctAnswersMax and nBlock < nbBlocksMax:
    presentationOrder = newRandomPresentation(presentationOrder, override_remove_cards=removeCards)
    # PRESENTATION BLOCK
    if 1 != nbBlocksMax or experimentName == 'PreLearn':
        exp.add_experiment_info('Presentation_Block_{}_timing_{}'.format(nBlock, exp.clock.time))

        instructions = stimuli.TextLine(presentation_screen_text[language],
                                        position=(0, -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
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

        m.plotDefault(bs, True)  # Draw default grid
        bs.present(False, True)

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI, process_control_events=True)

        # LOG and SYNC: Start Presentation
        exp.add_experiment_info('StartPresentation_Block_{}_timing_{}'.format(nBlock, exp.clock.time))  # Add sync info

        for nCard in presentationOrder:
            mouse.hide_cursor(True, True)
            m.plotCard(nCard, True, bs, True)  # Show Location for ( 2s )
            exp.add_experiment_info('ShowCard_pos_{}_card_{}_timing_{}'.format(
                nCard, m.returnPicture(nCard), exp.clock.time))

            exp.clock.wait(presentationCard, process_control_events=True)
            m.plotCard(nCard, False, bs, True)
            exp.add_experiment_info('HideCard_pos_{}_card_{}_timing_{}'.format(
                nCard, m.returnPicture(nCard), exp.clock.time))  # Add sync info

            ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
            exp.clock.wait(ISI, process_control_events=True)

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI, process_control_events=True)

        m.plotDefault(bs, True, show_matrix=False)  # Draw default grid
        bs.present(False, True)

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI, process_control_events=True)

        # REST BLOCK
        instructions = stimuli.TextLine(
            rest_screen_text[language],
            position=(0, -windowSize[1] / float(2) + (2 * m.gap + cardSize[1]) / float(2)),
            text_font=None, text_size=textSize, text_bold=None, text_italic=None,
            text_underline=None, text_colour=textColor, background_colour=bgColor,
            max_width=None)

        instructions.plot(bs)
        bs.present(False, True)
        exp.add_experiment_info(
            ['StartShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
        exp.clock.wait(restPeriod, process_control_events=True)
        exp.add_experiment_info(
            ['EndShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
        instructionRectangle.plot(bs)
        bs.present(False, True)

    # TEST BLOCK
    instructions = stimuli.TextLine(' TEST ',
                                    position=(
                                        0, -windowSize[1] / float(2) + (2 * m.gap + cardSize[1]) / float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
    instructionRectangle.plot(bs)
    instructions.plot(bs)
    bs.present(False, True)

    # LOG and SYNC Start Test
    exp.add_experiment_info(['StartTest_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info

    exp.clock.wait(shortRest, process_control_events=True)  # Short Rest between presentation and cue-recall

    instructionRectangle.plot(bs)
    bs.present(False, True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)

    m.plotDefault(bs, True)  # Draw default grid
    bs.present(False, True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)

    ''' Cue Recall '''
    presentationOrder = newRandomPresentation(presentationOrder, override_remove_cards=removeCards)
    exp.add_experiment_info(['Block {} - Test'.format(nBlock)])  # Add listPictures
    exp.add_experiment_info(str(presentationOrder))
    for nCard in presentationOrder:

        m._cueCard.setPicture(m._matrix.item(nCard).stimuli[0].filename)  # Associate Picture to CueCard
        m._cueCard.setSound(m._matrix.item(nCard).sound)  # Associate Sound to CueCard

        m.plotCueCard(True, bs, True)  # Show Cue
        exp.add_experiment_info('ShowCueCard_pos_{}_card_{}_timing_{}'.format(nCard,
                                                                              m.returnPicture(nCard),
                                                                              exp.clock.time))
        exp.clock.wait(presentationCard)  # Wait presentationCard
        m.plotCueCard(False, bs, True)  # Hide Cue
        exp.add_experiment_info('HideCueCard_pos_{}_card_{}_timing_{}'.format(nCard, m.returnPicture(nCard),
                                                                              exp.clock.time))

        # Mouse Response Block
        time_left = responseTime
        valid_response = False
        rt = True  # Response time; equals None if participant haven't clicked within window time frame they were
        # given to answer
        while not valid_response and rt is not None:
            mouse.show_cursor(True, True)
            start = get_time()
            rt, position = readMouse(start, mouseButton, time_left)
            mouse.hide_cursor(True, True)

            if rt is not None:
                currentCard = m.checkPosition(position)
                try:
                    exp.add_experiment_info('Response_pos_{}_card_{}_timing_{}'.format(currentCard,
                                                                                       m.returnPicture(currentCard),
                                                                                       exp.clock.time))  # Add sync info
                    valid_response = True
                except:
                    exp.add_experiment_info('Response_pos_{}_ERROR_timing_{}'.format(currentCard, exp.clock.time))
                if currentCard is not None:  # and currentCard not in removeCards:
                    m._matrix.item(currentCard).color = clickColor
                    m.plotCard(currentCard, False, bs, True)

                    exp.clock.wait(clicPeriod)  # Wait 200ms

                    m._matrix.item(currentCard).color = cardColor
                    m.plotCard(currentCard, False, bs, True)

                if currentCard == nCard:
                    correctAnswers[nBlock] += 1
                    exp.data.add([exp.clock.time, nBlock,
                                  path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                                  path_leaf(m._matrix.item(currentCard).stimuli[0].filename),
                                  rt])

                elif currentCard is None:
                    exp.data.add([exp.clock.time, nBlock,
                                  path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                                  None,
                                  rt])
                else:
                    exp.data.add([exp.clock.time, nBlock,
                                  path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                                  path_leaf(m._matrix.item(currentCard).stimuli[0].filename),
                                  rt])
            else:
                exp.data.add([exp.clock.time, nBlock,
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

    m.plotDefault(bs, True, show_matrix=False)  # Draw default grid
    bs.present(False, True)

    currentCorrectAnswers = correctAnswers[nBlock]  # Number of correct answers
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
        rest_screen_text[language],
        position=(0, -windowSize[1] / float(2) + (2 * m.gap + cardSize[1]) / float(2)),
        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
        text_underline=None, text_colour=textColor, background_colour=bgColor,
        max_width=None)

    instructions.plot(bs)
    bs.present(False, True)
    exp.add_experiment_info(
        ['StartShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
    exp.clock.wait(restPeriod, process_control_events=True)
    exp.add_experiment_info(
        ['EndShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
    instructionRectangle.plot(bs)
    bs.present(False, True)

    nBlock += 1

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

control.end()
