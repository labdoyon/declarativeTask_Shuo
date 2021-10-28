import sys
import os

import numpy as np
from math import floor
from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants
from expyriment.misc._timer import get_time

from declarativeTask3.ld_matrix import LdMatrix
from declarativeTask3.ld_utils import setCursor, newRandomPresentation, getPreviousMatrix, getLanguage, path_leaf,\
    readMouse, logging_ttl_time_stamps_with_ttl_char_hotkeys
from declarativeTask3.ld_utils import getPlacesOrFacesChoice, rename_output_files_to_BIDS
# from ld_sound import create_temp_sound_files, delete_temp_files
from declarativeTask3.config import *
from declarativeTask3.ttl_catch_keyboard import wait_for_ttl_keyboard_and_log_ttl
from declarativeTask3.ld_stimuli_names import classNames, ttl_instructions_text, presentation_screen_text, rest_screen_text, \
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
session = experiment_session[experimentName]
session_dir = os.path.normpath(os.path.join('sourcedata', 'sub-' + subjectName, 'ses-' + session))
output_dir = os.path.normpath(os.path.join(session_dir, 'beh'))
if not os.path.isdir(session_dir):
    os.mkdir(session_dir)
io.defaults.datafile_directory = output_dir
io.defaults.eventfile_directory = output_dir

logging_ttl_time_stamps_with_ttl_char_hotkeys(exp)  # logging all TTL information

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

bids_datafile, bids_eventfile = rename_output_files_to_BIDS(subjectName, session, experimentName,
                                                            io.defaults.datafile_directory,
                                                            io.defaults.eventfile_directory)
exp.data.rename(bids_datafile)
exp.events.rename(bids_eventfile)

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

setCursor(arrow)

bs = stimuli.BlankScreen(bgColor)  # Create blank screen

exp.clock.wait(shortRest, process_control_events=True)

correctAnswers = np.zeros(nbBlocksMax)
currentCorrectAnswers = 0
nBlock = 0

''' Presentation all locations '''
presentationOrder = newRandomPresentation(override_remove_cards=removeCards)

m.plotDefault(bs, draw=False)
m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, ttl_instructions_text[language], draw=False)
bs.present(False, True)

last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp)
exp.add_experiment_info('TTL_RECEIVED_QC_timing_{}'.format(exp.clock.time))  # for QC purposes

m.plot_instructions_rectangle(bs, instructions_card, draw=True)
ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
exp.clock.wait(ISI, process_control_events=True)

while currentCorrectAnswers < correctAnswersMax and nBlock < nbBlocksMax:
    presentationOrder = newRandomPresentation(presentationOrder, override_remove_cards=removeCards)
    # PRESENTATION BLOCK
    if 1 != nbBlocksMax or experimentName == 'PreLearn':
        exp.add_experiment_info('Presentation_Block_{}_timing_{}'.format(nBlock, exp.clock.time))

        m.plot_instructions_rectangle(bs, instructions_card, draw=False)
        m.plot_instructions(bs, instructions_card, presentation_screen_text[language], draw=False)
        bs.present(False, True)

        exp.clock.wait(shortRest, process_control_events=True)
        m.plot_instructions_rectangle(bs, instructions_card, draw=False)
        m.plot_instructions_card(bs, instructions_card, draw=False)
        bs.present(False, True)

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI, process_control_events=True)

        # LOG and SYNC: Start Presentation
        exp.add_experiment_info('StartPresentation_Block_{}_timing_{}'.format(nBlock, exp.clock.time))  # Add sync info

        mouse.hide_cursor(True, True)
        for nCard in presentationOrder:
            last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)
            exp.add_experiment_info('TTL_RECEIVED_QC_timing_{}'.format(exp.clock.time))  # for QC purposes
            m.plotCard(nCard, True, bs, True)  # Show Location for ( 2s )
            exp.add_experiment_info('ShowCard_pos_{}_card_{}_timing_{}'.format(
                nCard, m.returnPicture(nCard), exp.clock.time))

            last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)
            exp.add_experiment_info('TTL_RECEIVED_QC_timing_{}'.format(exp.clock.time))  # for QC purposes
            m.plotCard(nCard, False, bs, True)
            exp.add_experiment_info('HideCard_pos_{}_card_{}_timing_{}'.format(
                nCard, m.returnPicture(nCard), exp.clock.time))  # Add sync info

            # custom waiting time

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI, process_control_events=True)

        # REST BLOCK
        m.plot_instructions_rectangle(bs, instructions_card, draw=False)
        m.plot_instructions(bs, instructions_card, rest_screen_text[language], draw=False)
        bs.present(False, True)

        exp.add_experiment_info(
            ['StartShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
        exp.clock.wait(restPeriod, process_control_events=True)
        exp.add_experiment_info(
            ['EndShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
        m.plot_instructions_rectangle(bs, instructions_card, draw=True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)

    # TEST BLOCK
    m.plot_instructions_rectangle(bs, instructions_card, draw=False)
    m.plot_instructions(bs, instructions_card, ' TEST ', draw=False)
    bs.present(False, True)

    # LOG and SYNC Start Test
    exp.add_experiment_info(['StartTest_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info

    exp.clock.wait(shortRest, process_control_events=True)  # Short Rest between presentation and cue-recall

    m.plot_instructions_rectangle(bs, instructions_card, draw=False)
    m.plot_instructions_card(bs, instructions_card, draw=False)
    bs.present(False, True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)

    ''' Cue Recall '''
    presentationOrder = newRandomPresentation(presentationOrder, override_remove_cards=removeCards)
    exp.add_experiment_info(['Block {} - Test'.format(nBlock)])  # Add listPictures
    exp.add_experiment_info(str(presentationOrder))
    for nCard in presentationOrder:
        last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)
        exp.add_experiment_info('TTL_RECEIVED_QC_timing_{}'.format(exp.clock.time))  # for QC purposes
        m._cueCard.setPicture(m._matrix.item(nCard).stimuli[0].filename)  # Associate Picture to CueCard

        m.plotCueCard(True, bs, True)  # Show Cue
        exp.add_experiment_info('ShowCueCard_pos_{}_card_{}_timing_{}'.format(nCard,
                                                                              m.returnPicture(nCard),
                                                                              exp.clock.time))

        # Initiate Mouse Response Block
        time_left = responseTime
        valid_response = False
        rt = True  # Response time; equals None if participant haven't clicked within window time frame they were
        # given to answer

        last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)
        exp.add_experiment_info('TTL_RECEIVED_QC_timing_{}'.format(exp.clock.time))  # for QC purposes
        m.plotCueCard(False, bs, True)  # Hide Cue
        exp.add_experiment_info('HideCueCard_pos_{}_card_{}_timing_{}'.format(nCard, m.returnPicture(nCard),
                                                                              exp.clock.time))
        # Mouse Response Block
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

                    exp.clock.wait(clicPeriod, process_control_events=True)  # Wait 200ms

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
        exp.clock.wait(ISI, process_control_events=True)

    currentCorrectAnswers = correctAnswers[nBlock]  # Number of correct answers
    if nbBlocksMax != 1 or experimentName == 'DayOne-PreLearning':
        m.plot_instructions_rectangle(bs, instructions_card, draw=False)
        m.plot_instructions(bs, instructions_card,
                            'You got ' + str(int(correctAnswers[nBlock])) + ' out of '
                            + str(m._matrix.size-len(removeCards)), draw=False)
        bs.present(False, True)

        exp.clock.wait(shortRest, process_control_events=True)

        m.plot_instructions_rectangle(bs, instructions_card, draw=False)
        m.plot_instructions_card(bs, instructions_card, draw=False)
        bs.present(False, True)

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI, process_control_events=True)

    m.plot_instructions_rectangle(bs, instructions_card, draw=False)
    m.plot_instructions(bs, instructions_card, rest_screen_text[language], draw=False)
    bs.present(False, True)

    exp.add_experiment_info(
        ['StartShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
    exp.clock.wait(restPeriod, process_control_events=True)
    exp.add_experiment_info(
        ['EndShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
    m.plot_instructions_rectangle(bs, instructions_card, draw=False)
    m.plot_instructions_card(bs, instructions_card, draw=False)
    bs.present(False, True)

    nBlock += 1

ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
exp.clock.wait(ISI, process_control_events=True)

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, rest_screen_text[language], draw=False)
bs.present(False, True)

exp.clock.wait(thankYouRest, process_control_events=True)
m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

control.end()
