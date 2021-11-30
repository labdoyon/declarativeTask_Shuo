import sys
import os
from math import ceil

import numpy as np
from expyriment import control, stimuli, io, design, misc
from expyriment.misc._timer import get_time
import mouse as ms

from declarativeTask3.ld_matrix import LdMatrix
from declarativeTask3.ld_utils import setCursor, getPreviousMatrix, newRandomPresentation, readMouse
from declarativeTask3.ld_utils import getLanguage, getPlacesOrFacesChoice, rename_output_files_to_BIDS
from declarativeTask3.ld_utils import logging_ttl_time_stamps_with_ttl_char_hotkeys
from declarativeTask3.ld_utils import getPreviouslyCorrectlyRecalledImages, rest_function
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
faces_places_choice = getPlacesOrFacesChoice(subjectName, 0, 'choose-faces-places')
exp.add_experiment_info('start_by_class1_or_class2:')
exp.add_experiment_info(faces_places_choice)
exp.add_experiment_info('start_by_faces_or_places (same as above but explicit):')
exp.add_experiment_info(supported_start_by_choices_explicit[faces_places_choice])

# Save time, Response, correctAnswer, RT
exp.add_data_variable_names(['logging_timestamp', 'NBlock', 'categoryPresented', 'CorrectLocationShown',
                             'start_of_image_presentation_timestamp', 'end_of_image_presentation_timestamp',
                             'start_of_response_period_timestamp',
                             'subjectAnswered', 'subjectCorrect', 'ResponseTime'])

learningMatrix = getPreviousMatrix(subjectName, 0, 'PreLearn')
exp.add_experiment_info('Learning: ')
exp.add_experiment_info(str(learningMatrix))

randomMatrix = m.newRecognitionMatrix(learningMatrix)
exp.add_experiment_info('RandomMatrix: ')
exp.add_experiment_info(str(randomMatrix))

number_blocks = 1
intro_instruction = ' RECOGNITION '
if experimentName == "PostRecog1" or experimentName == "PostRecog2":

    if experiment_use_faces_or_places[faces_places_choice][experimentName] == 'faces':
        only_faces = True
        only_places = False
        parent_category = 'faces'
        removeCards = only_faces_remove_cards
        local_learning_matrix = [element for index, element in enumerate(learningMatrix) if matrixTemplate[index] < 4]
        local_random_matrix = [element for index, element in enumerate(randomMatrix) if matrixTemplate[index] < 4]
    elif experiment_use_faces_or_places[faces_places_choice][experimentName] == 'places':
        only_faces = False
        only_places = True
        parent_category = 'places'
        removeCards = only_places_remove_cards
        local_learning_matrix = [element for index, element in enumerate(learningMatrix) if matrixTemplate[index] > 3]
        local_random_matrix = [element for index, element in enumerate(randomMatrix) if matrixTemplate[index] > 3]

    exp.add_experiment_info('faces_or_places_for_this_experiment:')
    exp.add_experiment_info(parent_category)
    # local_learning_matrix = [element for index, element in enumerate(learningMatrix) if index not in removeCards]
    # local_random_matrix = [element for index, element in enumerate(randomMatrix) if index not in removeCards]
    exp.add_experiment_info(parent_category + '_only_matrix:')
    exp.add_experiment_info(str(local_learning_matrix))
    exp.add_experiment_info(parent_category + '_only_random_matrix:')
    exp.add_experiment_info(str(local_random_matrix))

elif experimentName == "MVPA":
    intro_instruction = ' MVPA '
    number_blocks = mvpa_number_blocks
    parent_category = 'both'
    only_faces = False
    only_places = False
    from config import removeCards  # default
    local_learning_matrix = learningMatrix
    local_random_matrix = randomMatrix
    exp.add_experiment_info('faces_or_places_for_this_experiment:')
    exp.add_experiment_info(parent_category)

    # get previously correctly recalled images
    if experiment_use_faces_or_places[faces_places_choice]['PostTest2'] == 'faces' and \
            experiment_use_faces_or_places[faces_places_choice]['PostLearn'] == 'places':
        correctly_recalled_faces = getPreviouslyCorrectlyRecalledImages(subjectName, experienceName='PostTest2')
        correctly_recalled_places = getPreviouslyCorrectlyRecalledImages(subjectName, experienceName='PostLearn')
    elif experiment_use_faces_or_places[faces_places_choice]['PostTest2'] == 'places' and \
            experiment_use_faces_or_places[faces_places_choice]['PostLearn'] == 'faces':
        correctly_recalled_faces = getPreviouslyCorrectlyRecalledImages(subjectName, experienceName='PostLearn')
        correctly_recalled_places = getPreviouslyCorrectlyRecalledImages(subjectName, experienceName='PostTest2')

    not_recalled_faces_locations = [index for (index, correctly_recalled) in correctly_recalled_faces.items()
                                    if correctly_recalled is False]
    # position indexes are 0 to 48 excluding 24
    not_recalled_faces_matrix_indexes = [index if index < center_card_position else index - 1 for
                                         index in not_recalled_faces_locations]
    # matrix indexes are 0 to 47
    not_recalled_faces = [learningMatrix[position] for position in not_recalled_faces_matrix_indexes]
    not_recalled_faces_location_in_random_matrix = [randomMatrix.index(image) for image in not_recalled_faces]

    not_recalled_places_locations = [index for (index, correctly_recalled) in correctly_recalled_places.items()
                                     if correctly_recalled is False]
    # position indexes are 0 to 48 excluding 24
    not_recalled_places_matrix_indexes = [index if index < center_card_position else index - 1 for
                                          index in not_recalled_places_locations]
    # matrix indexes are 0 to 47
    not_recalled_places = [learningMatrix[position] for position in not_recalled_places_matrix_indexes]
    not_recalled_places_location_in_random_matrix = [randomMatrix.index(image) for image in not_recalled_places]

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

button_size = (cardSize[0]/2 + m.gap/8, cardSize[1]*3/5)
rectangle_size = (cardSize[0]/2 + m.gap/8, cardSize[1])

matrixA_position = (cardSize[0]/4 + m.gap/4, 0)
matrixNone_position = (-cardSize[0]/4 - m.gap/4, 0)

matrixA = stimuli.TextBox(text='R', size=button_size,
                          position=matrixA_position,
                          text_size=textSize,
                          text_colour=constants.C_GREEN,
                          background_colour=cardColor)
matrixA_rectangle = stimuli.Rectangle(size=rectangle_size, position=matrixA_position, colour=cardColor)

matrixNone = stimuli.TextBox('W', size=button_size,
                             position=matrixNone_position,
                             text_size=textSize,
                             text_colour=constants.C_RED,
                             background_colour=cardColor)
matrixNone_rectangle = stimuli.Rectangle(size=rectangle_size, position=matrixNone_position, colour=cardColor)

m.plotDefault(bs)  # Draw default grid
m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, ttl_instructions_text[language], draw=False)
bs.present(False, True)

last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp)

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

# Pre-Rest before experience in order to have 15s or more of baseline brain activity in the MRI
rest_function(exp, last_ttl_timestamp)

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, intro_instruction, draw=False)
bs.present(False, True)

last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

# LOG and SYNC
exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info

for n_block in range(number_blocks):
    exp.add_experiment_info('Block_{}_timing_{}'.format(n_block, exp.clock.time))
    exp.add_experiment_info('Presentation Order: ')  # Save Presentation Order

    if experimentName == "PostRecog1" or experimentName == "PostRecog2":
        presentationMatrixLearningOrder = newRandomPresentation(override_remove_cards=removeCards)
        presentationMatrixLearningOrder = np.vstack((presentationMatrixLearningOrder, np.zeros(m.size[0]*m.size[1]-len(removeCards))))
        presentationMatrixRandomOrder = newRandomPresentation(presentationMatrixLearningOrder, override_remove_cards=removeCards)
        presentationMatrixRandomOrder = np.vstack((presentationMatrixRandomOrder, np.ones(m.size[0]*m.size[1]-len(removeCards))))
        trials_list_to_present = [presentationMatrixLearningOrder, presentationMatrixRandomOrder]
    elif experimentName == 'MVPA':
        # Adding Faces Trial
        presentationMatrixLearningOrder_faces = newRandomPresentation(number_trials=mvpa_number_trials_correct_position,
                                                                      override_remove_cards=only_faces_remove_cards +
                                                                      not_recalled_faces_locations)
        presentationMatrixRandomOrder_faces = newRandomPresentation(presentationMatrixLearningOrder_faces,
                                                                    number_trials=mvpa_number_trials_wrong_position,
                                                                    override_remove_cards=only_faces_remove_cards +
                                                                    not_recalled_faces_location_in_random_matrix)
        presentationMatrixLearningOrder_faces = np.vstack((
            presentationMatrixLearningOrder_faces,
            np.zeros(len(presentationMatrixLearningOrder_faces), dtype=int),
            mvpa_block_number_TRs_to_wait_inter_trials_for_correct_positions))
        presentationMatrixRandomOrder_faces = np.vstack((
            presentationMatrixRandomOrder_faces,
            np.ones(len(presentationMatrixRandomOrder_faces), dtype=int),
            mvpa_block_number_TRs_to_wait_inter_trials_for_wrong_positions))

        # Adding Places Trial
        presentationMatrixLearningOrder_places = newRandomPresentation(
            number_trials=mvpa_number_trials_correct_position,
            override_remove_cards=only_places_remove_cards + not_recalled_places_locations)
        presentationMatrixLearningOrder_places = np.vstack((
            presentationMatrixLearningOrder_places,
            np.zeros(len(presentationMatrixLearningOrder_places), dtype=int),
            mvpa_block_number_TRs_to_wait_inter_trials_for_correct_positions))
        presentationMatrixRandomOrder_places = newRandomPresentation(presentationMatrixLearningOrder_places,
                                                                     number_trials=mvpa_number_trials_wrong_position,
                                                                     override_remove_cards=only_places_remove_cards +
                                                                     not_recalled_places_location_in_random_matrix)
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
            listCards.append(local_learning_matrix[int(position)])
        else:
            listCards.append(local_random_matrix[int(position)])

    exp.add_experiment_info(str(list(presentationOrder)))  # Add listPictures

    if experimentName == "PostRecog1" or experimentName == "PostRecog2":
        number_TRs_inter_trials = recognition_block_number_TRs_to_wait_inter_trials.copy()

    for nCard in range(presentationOrder.shape[1]):
        # Inter Trial Interval
        min_iti_in_TRs = ceil((exp.clock.time - last_ttl_timestamp) / TR_duration)
        if experimentName == "PostRecog1" or experimentName == "PostRecog2":
            exp.add_experiment_info(f"min_iti_in_TRs_{min_iti_in_TRs}")
            # removing elements which can't be selected
            temp_number_TRs_inter_trials = [element for element in number_TRs_inter_trials if element >= min_iti_in_TRs]
            if not temp_number_TRs_inter_trials:
                trial_iti = np.random.choice(
                        [element for element in recognition_possible_iti if element >= min_iti_in_TRs])
                exp.add_experiment_info(f"ran_out_of_ITI_{trial_iti}_in_list")
            else:
                # temp_probabilities_to_pick = [1 / element ** 2 for element in temp_number_TRs_inter_trials]  # favoring ones
                temp_probabilities_to_pick = [1 for element in temp_number_TRs_inter_trials]  # favoring ones
                # sum of element should be one, normalizing
                temp_probabilities_to_pick = np.divide(temp_probabilities_to_pick, sum(temp_probabilities_to_pick))

                trial_iti = np.random.choice(temp_number_TRs_inter_trials, p=temp_probabilities_to_pick)
                number_TRs_inter_trials.remove(trial_iti)
        elif experimentName == "MVPA":
            trial_iti = presentationOrder[2][nCard]

        exp.add_experiment_info(f'wait_{trial_iti}_TTLs')
        for i_ttl in range(trial_iti - min_iti_in_TRs):
            last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)

        # Trial Block
        locationCard = int(presentationOrder[0][nCard])

        if bool(presentationOrder[1][nCard] == 0):
            showMatrix = 'MatrixA'
        else:
            showMatrix = 'MatrixRandom'

        category = listCards[nCard][:2]
        m._matrix.item(locationCard).setPicture(os.path.join(picturesFolderClass[category], listCards[nCard]))
        picture = listCards[nCard].rstrip(".png")
        last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)
        m.plotCard(locationCard, True, bs, True)
        start_of_image_presentation_timestamp = exp.clock.time
        exp.add_experiment_info(
            'ShowCard_pos_{}_card_{}_timing_{}'.format(locationCard, listCards[nCard], start_of_image_presentation_timestamp))

        # initiate mouse response block
        time_left = responseTime
        valid_response = False
        rt = 0

        last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)
        m.plotCard(locationCard, False, bs, True)
        end_of_image_presentation_timestamp = exp.clock.time
        exp.add_experiment_info(['HideCard_pos_{}_card_{}_timing_{}'.format(locationCard,
                                                                            listCards[nCard],
                                                                            end_of_image_presentation_timestamp)])

        m.plotCueCard(False, bs, draw=False, nocross=True)
        matrixA_rectangle.plot(bs)
        matrixA.plot(bs)
        matrixNone_rectangle.plot(bs)
        matrixNone.plot(bs)
        bs.present(False, True)

        answer = 'noResponse'
        start_of_response_period_timestamp = exp.clock.time
        valid_answer = False
        while exp.clock.time - start_of_response_period_timestamp < responseTime:
            if ms.is_pressed(button='left'):
                response_timestamp = exp.clock.time
                answer = 'matrixNone'
                valid_answer = True
                break
            if ms.is_pressed(button='right'):
                response_timestamp = exp.clock.time
                answer = 'matrixA'
                valid_answer = True
                break
            if exp.keyboard.process_control_keys():
                exp.keyboard.process_control_keys()
        if valid_answer:
            rt = exp.clock.time - start_of_response_period_timestamp
        else:
            rt = None
        if answer == 'matrixA':
            exp.data.add([exp.clock.time, n_block, category, showMatrix == 'MatrixA',
                          start_of_image_presentation_timestamp, end_of_image_presentation_timestamp,
                          start_of_response_period_timestamp,
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

        elif answer == 'matrixNone':
            exp.data.add([exp.clock.time, n_block, category, showMatrix == 'MatrixA',
                          start_of_image_presentation_timestamp, end_of_image_presentation_timestamp,
                          start_of_response_period_timestamp,
                          'incorrect', bool(presentationOrder[1][nCard] == 1), rt])
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
            exp.data.add([exp.clock.time, n_block, category, showMatrix == 'MatrixA',
                          start_of_image_presentation_timestamp, end_of_image_presentation_timestamp,
                          start_of_response_period_timestamp,
                          None, False, rt])
            exp.add_experiment_info(['Response_{}_timing_{}'.format('NoRT', exp.clock.time)])  # Add sync info
            valid_response = True

        exp.clock.wait(visual_comfort_wait_time, process_control_events=True)
        # for comfort, for objects not to move too quickly or suddenly on screen

        m.plotCueCard(False, bs, draw=True)
        bs.present(False, True)

    # Pre-Rest Block
    rest_function(exp, n_block, last_ttl_timestamp, pre_rest=True)

    # Plot instructions
    m.plot_instructions_rectangle(bs, instructions_card, draw=False)
    m.plot_instructions(bs, instructions_card, rest_screen_text[language], draw=False)
    bs.present(False, True)
    last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)
    m.plot_instructions_rectangle(bs, instructions_card, draw=False)
    m.plot_instructions_card(bs, instructions_card, draw=False)
    bs.present(False, True)

    # REST PERIOD
    rest_function(exp, last_ttl_timestamp)

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, ending_screen_text[language], draw=False)
bs.present(False, True)

exp.clock.wait(shortRest, process_control_events=True)
m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

control.end()
