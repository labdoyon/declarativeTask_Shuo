import sys
import os
from math import ceil

import numpy as np
from expyriment import control, stimuli, io, design, misc
from expyriment.misc._timer import get_time
from expyriment.misc import constants

from declarativeTask3.ld_matrix import LdMatrix
from declarativeTask3.ld_utils import setCursor, getPreviousMatrix, newRandomPresentation, readMouse
from declarativeTask3.ld_utils import getLanguage, getPlacesOrFacesChoice, rename_output_files_to_BIDS
from declarativeTask3.ld_utils import logging_ttl_time_stamps_with_ttl_char_hotkeys
from declarativeTask3.ttl_catch_keyboard import wait_for_ttl_keyboard_and_log_ttl
from declarativeTask3.config import *
from declarativeTask3.ld_stimuli_names import classNames, ttl_instructions_text, ending_screen_text, rest_screen_text

if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

m = LdMatrix(matrixSize, windowSize, recognition_bigger_cuecard=True)  # Create Matrix

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject
experimentName = arguments[0]
subjectName = arguments[1]

exp = design.Experiment(experimentName)  # Save experiment name

session = experiment_session[experimentName]
session_dir = 'sourcedata' + os.path.sep +\
             'sub-' + subjectName + os.path.sep +\
             'ses-' + session
output_dir = session_dir + os.path.sep +\
             'beh'
if not os.path.isdir(session_dir):
    os.mkdir(session_dir)
io.defaults.datafile_directory = output_dir
io.defaults.eventfile_directory = output_dir

logging_ttl_time_stamps_with_ttl_char_hotkeys(exp)  # logging all TTL information

exp.add_experiment_info('Subject: ')
exp.add_experiment_info(subjectName)
language = str(getLanguage(subjectName, 0, 'choose-language'))
exp.add_experiment_info('language: ')
faces_places_choice = getPlacesOrFacesChoice(subjectName, 0, 'choose-faces-places')
exp.add_experiment_info('start_by_class1_or_class2:')
exp.add_experiment_info(faces_places_choice)
exp.add_experiment_info('start_by_faces_or_places (same as above but explicit):')
exp.add_experiment_info(supported_start_by_choices_explicit[faces_places_choice])

# Save time, Response, correctAnswer, RT
exp.add_data_variable_names(['Time', 'categoryPresented', 'CorrectLocationShown',
                             'subjectAnswered', 'subjectCorrect', 'ResponseTime'])

learningMatrix = getPreviousMatrix(subjectName, 0, 'PreLearn')
exp.add_experiment_info('Learning: ')
exp.add_experiment_info(str(learningMatrix))

randomMatrix = m.newRecognitionMatrix(learningMatrix)
exp.add_experiment_info('RandomMatrix: ')
exp.add_experiment_info(str(randomMatrix))

exp.add_experiment_info('Image classes order:')
exp.add_experiment_info(str(classPictures))


control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

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

m.plotDefault(bs)  # Draw default grid
m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, ttl_instructions_text[language], draw=False)
bs.present(False, True)

last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp)
exp.add_experiment_info('TTL_RECEIVED_QC_timing_{}'.format(exp.clock.time))  # for QC purposes

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

ISI = design.randomize.rand_int(300, 500)
exp.clock.wait(ISI, process_control_events=True)

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, ' MVPA ', draw=False)
bs.present(False, True)

exp.clock.wait(shortRest, process_control_events=True)

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

# LOG and SYNC
exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info

button_size = (cardSize[0]/2 + m.gap/8, cardSize[1]*3/5)
rectangle_size = (cardSize[0]/2 + m.gap/8, cardSize[1])

matrixA_position = (cardSize[0]/4 + m.gap/4, 0)
matrixNone_position = (-cardSize[0]/4 - m.gap/4, 0)

matrixA_rectangle = stimuli.Rectangle(size=rectangle_size, position=matrixA_position, colour=cardColor)
matrixA = stimuli.TextBox(text='R', size=button_size,
                          position=matrixA_position,
                          text_size=textSize,
                          text_colour=constants.C_GREEN,
                          background_colour=cardColor)

matrixNone_rectangle = stimuli.Rectangle(size=rectangle_size, position=matrixNone_position, colour=cardColor)
matrixNone = stimuli.TextBox('W', size=button_size,
                             position=matrixNone_position,
                             text_size=textSize,
                             text_colour=constants.C_RED,
                             background_colour=cardColor)

ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
exp.clock.wait(ISI, process_control_events=True)

for n_block in range(mvpa_number_blocks):
    exp.add_experiment_info('Presentation_Block_{}_timing_{}'.format(n_block, exp.clock.time))
    exp.add_experiment_info('Presentation Order_Block_{}_'.format(n_block))  # Save Presentation Order

    center_position = floor(matrixSize[0] * matrixSize[1] / 2)
    # Adding Faces Trial
    only_faces_remove_cards = [center_position] + \
                              [index + 1 if index >= center_position else index
                               for index, category in enumerate(matrixTemplate) if category > 3]
    presentationMatrixLearningOrder_faces = newRandomPresentation(number_trials=mvpa_number_trials_correct_position,
                                                                  override_remove_cards=only_faces_remove_cards)
    presentationMatrixLearningOrder_faces = np.vstack((
        presentationMatrixLearningOrder_faces,
        np.zeros(len(presentationMatrixLearningOrder_faces), dtype=int),
        mvpa_block_number_TRs_to_wait_inter_trials_for_correct_positions))

    presentationMatrixRandomOrder_faces = newRandomPresentation(presentationMatrixLearningOrder_faces,
                                                                number_trials=mvpa_number_trials_wrong_position,
                                                                override_remove_cards=only_faces_remove_cards)
    presentationMatrixRandomOrder_faces = np.vstack((
        presentationMatrixRandomOrder_faces,
        np.ones(len(presentationMatrixRandomOrder_faces), dtype=int),
        mvpa_block_number_TRs_to_wait_inter_trials_for_wrong_positions))

    # Adding Places Trial
    only_places_remove_cards = [center_position] + \
                               [index + 1 if index >= center_position else index
                                for index, category in enumerate(matrixTemplate) if category <= 3]
    presentationMatrixLearningOrder_places = newRandomPresentation(number_trials=mvpa_number_trials_correct_position,
                                                                   override_remove_cards=only_places_remove_cards)
    presentationMatrixLearningOrder_places = np.vstack((
        presentationMatrixLearningOrder_places,
        np.zeros(len(presentationMatrixLearningOrder_places), dtype=int),
        mvpa_block_number_TRs_to_wait_inter_trials_for_correct_positions))
    presentationMatrixRandomOrder_places = newRandomPresentation(presentationMatrixLearningOrder_places,
                                                                 number_trials=mvpa_number_trials_wrong_position,
                                                                 override_remove_cards=only_places_remove_cards)
    presentationMatrixRandomOrder_places = np.vstack((presentationMatrixRandomOrder_places,
                                                     np.ones(len(presentationMatrixRandomOrder_places), dtype=int),
                                                      mvpa_block_number_TRs_to_wait_inter_trials_for_wrong_positions))

    # Null
    # presentationNull = np.vstack((np.full(mvpa_number_null_events, np.nan),
    #                               np.full(mvpa_number_null_events, np.nan),
    #                               []))  # TODO / WARNING: NULL EVENTS TO BE IMPLEMENTED

    # Sum
    trials_list_to_present = [presentationMatrixLearningOrder_faces, presentationMatrixLearningOrder_places,
                                   presentationMatrixRandomOrder_faces, presentationMatrixRandomOrder_places]
                                   # presentationNull]
    # Ensuring we only use integers
    for trial_list in trials_list_to_present:
        trial_list.astype(int)

    presentationOrder = np.hstack(tuple(trials_list_to_present))

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
            listCards.append(learningMatrix[int(position)])
        else:
            listCards.append(randomMatrix[int(position)])

    exp.add_experiment_info(str(list(presentationOrder)))  # Add listPictures

    for nCard in range(presentationOrder.shape[1]):

        # Inter Trial Interval
        trial_iti = presentationOrder[2][nCard]
        exp.add_experiment_info(f'wait_{trial_iti}_TTLs')
        for i_ttl in range(trial_iti - 1):  # one TTL is already accounted for, cannot wait less than
            # one TTL. If we put a 0 in the range above, we will wait one TTL, because of the next
            # <wait_for_ttl_keyboard_and_log_ttl> instruction
            last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)

        # Trial
        locationCard = int(presentationOrder[0][nCard])

        if bool(presentationOrder[1][nCard] == 0):
            showMatrix = 'MatrixA'
        else:
            showMatrix = 'MatrixRandom'

        category = listCards[nCard][:2]
        m._matrix.item(locationCard).setPicture(os.path.join(picturesFolderClass[category], listCards[nCard]))
        picture = listCards[nCard].rstrip(".png")
        last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)
        exp.add_experiment_info('TTL_RECEIVED_QC_timing_{}'.format(exp.clock.time))  # for QC purposes
        m.plotCard(locationCard, True, bs, True)

        exp.add_experiment_info(
            'ShowCard_pos_{}_card_{}_timing_{}'.format(locationCard, listCards[nCard], exp.clock.time))

        # initiate mouse response block
        time_left = responseTime
        valid_response = False
        rt = 0

        last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)
        exp.add_experiment_info('TTL_RECEIVED_QC_timing_{}'.format(exp.clock.time))  # for QC purposes
        m.plotCard(locationCard, False, bs, True)
        exp.add_experiment_info(['HideCard_pos_{}_card_{}_timing_{}'.format(locationCard,
                                                                            listCards[nCard],
                                                                            exp.clock.time)])  # Add sync info
        ISI = design.randomize.rand_int(300, 500)
        exp.clock.wait(ISI, process_control_events=True)

        m.plotCueCard(False, bs, draw=False, nocross=True)
        matrixA_rectangle.plot(bs)
        matrixNone_rectangle.plot(bs)
        matrixA.plot(bs)
        matrixNone.plot(bs)
        bs.present(False, True)

        while not valid_response and rt is not None:
            mouse.show_cursor(True, True)

            start = get_time()
            rt, position = readMouse(start, mouseButton, time_left)  # time_left instead of response tine

            mouse.hide_cursor(True, True)

            if rt is not None:
                if matrixA_rectangle.overlapping_with_position(position):
                    valid_response = True
                    exp.data.add([exp.clock.time, category, showMatrix == 'MatrixA',
                                  'correct', bool(presentationOrder[1][nCard] == 0), rt])
                    matrixA = stimuli.TextBox(text='R', size=button_size,
                                              position=matrixA_position,
                                              text_size=textSize,
                                              text_colour=constants.C_GREEN,
                                              background_colour=clickColor)
                    matrixA_rectangle = stimuli.Rectangle(size=rectangle_size, position=matrixA_position,
                                                          colour=clickColor)

                    matrixA_rectangle.plot(bs)
                    matrixA.plot(bs)
                    bs.present(False, True)
                    exp.clock.wait(clicPeriod, process_control_events=True)
                    matrixA = stimuli.TextBox(text='R', size=button_size,
                                              position=matrixA_position,
                                              text_size=textSize,
                                              text_colour=constants.C_GREEN,
                                              background_colour=cardColor)
                    matrixA_rectangle = stimuli.Rectangle(size=rectangle_size, position=matrixA_position,
                                                          colour=cardColor)
                    matrixA_rectangle.plot(bs)
                    matrixA.plot(bs)
                    bs.present(False, True)
                    exp.add_experiment_info(['Response_{}_timing_{}'.format('MatrixA', exp.clock.time)])  # Add sync info

                elif matrixNone_rectangle.overlapping_with_position(position):
                    valid_response = True
                    exp.data.add([exp.clock.time, category, showMatrix == 'MatrixA',
                                  'incorrect', bool(presentationOrder[1][nCard] == 1), rt])
                    exp.data.add([exp.clock.time, category, showMatrix, bool(presentationOrder[1][nCard] == 1), rt])
                    matrixNone = stimuli.TextBox('W', size=button_size,
                                                 position=matrixNone_position,
                                                 text_size=textSize,
                                                 text_colour=constants.C_RED,
                                                 background_colour=clickColor)
                    matrixNone_rectangle = stimuli.Rectangle(size=rectangle_size, position=matrixNone_position,
                                                             colour=clickColor)

                    matrixNone_rectangle.plot(bs)
                    matrixNone.plot(bs)
                    bs.present(False, True)
                    exp.clock.wait(clicPeriod, process_control_events=True)
                    matrixNone = stimuli.TextBox('W', size=button_size,
                                                 position=matrixNone_position,
                                                 text_size=textSize,
                                                 text_colour=constants.C_RED,
                                                 background_colour=cardColor)
                    matrixNone_rectangle = stimuli.Rectangle(size=rectangle_size, position=matrixNone_position,
                                                             colour=cardColor)
                    matrixNone_rectangle.plot(bs)
                    matrixNone.plot(bs)
                    bs.present(False, True)
                    exp.add_experiment_info(['Response_{}_timing_{}'.format('None', exp.clock.time)])  # Add sync info
            else:
                exp.data.add([exp.clock.time, category, showMatrix == 'MatrixA', None, False, rt])
                exp.add_experiment_info(['Response_{}_timing_{}'.format('NoRT', exp.clock.time)])  # Add sync info
                valid_response = True
            if rt is not None and not valid_response:
                if rt < time_left - clicPeriod:
                    time_left = time_left - clicPeriod - rt
                else:
                    exp.data.add([exp.clock.time, category, showMatrix == 'MatrixA', None, False, None])
                    exp.add_experiment_info(['Response_{}_timing_{}'.format('NoRT', exp.clock.time)])  # Add sync info
                    valid_response = True
                    break

        exp.clock.wait(300, process_control_events=True)# for comfort, for objects not to move too quickly or suddenly
        # on screen

        m.plotCueCard(False, bs, draw=True)
        bs.present(False, True)

    if n_block != mvpa_number_blocks - 1:
        # Pre-Rest Block
        for i in range(number_ttl_before_rest_period - 1):
            last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)

        m.plot_instructions_rectangle(bs, instructions_card, draw=False)
        m.plot_instructions(bs, instructions_card, rest_screen_text[language], draw=False)
        bs.present(False, True)
        exp.add_experiment_info(
            ['StartShortRest_block_{}_timing_{}'.format(n_block, exp.clock.time)])  # Add sync info

        exp.clock.wait(restPeriod, process_control_events=True)

        exp.add_experiment_info(
            ['EndShortRest_block_{}_timing_{}'.format(n_block, exp.clock.time)])  # Add sync info
        m.plot_instructions_rectangle(bs, instructions_card, draw=False)
        m.plot_instructions_card(bs, instructions_card, draw=False)
        bs.present(False, True)

# Pre-Rest Block
    for i in range(number_ttl_before_rest_period - 1):
        last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, ending_screen_text[language], draw=False)
bs.present(False, True)

exp.clock.wait(thankYouRest, process_control_events=True)
m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

control.end()
