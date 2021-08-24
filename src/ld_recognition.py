import sys

import numpy as np
from expyriment import control, stimuli, io, design, misc
from expyriment.misc._timer import get_time
from expyriment.misc import constants
from math import floor

from ld_matrix import LdMatrix
from ld_utils import setCursor, getPreviousMatrix, newRandomPresentation, readMouse
from ld_utils import getLanguage, getPlacesOrFacesChoice, rename_output_files_to_BIDS
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

exp.add_experiment_info('Subject: ')  # Save Subject Code
exp.add_experiment_info(subjectName)  # Save Subject Code
language = str(getLanguage(subjectName, 0, 'choose-language'))
exp.add_experiment_info('language: ')
faces_places_choice = getPlacesOrFacesChoice(subjectName, 0, 'choose-faces-places')
exp.add_experiment_info('start_by_class1_or_class2:')
exp.add_experiment_info(faces_places_choice)
exp.add_experiment_info('start_by_faces_or_places (same as above but explicit):')
exp.add_experiment_info(supported_start_by_choices_explicit[faces_places_choice])

if experiment_use_faces_or_places[faces_places_choice][experimentName] == 'faces':
    only_faces = True
    only_places = False
    exp.add_experiment_info('faces_or_places_for_this_experiment:')
    exp.add_experiment_info('faces')
elif experiment_use_faces_or_places[faces_places_choice][experimentName] == 'places':
    only_faces = False
    only_places = True
    exp.add_experiment_info('faces_or_places_for_this_experiment:')
    exp.add_experiment_info('places')


# Save time, Response, correctAnswer, RT
exp.add_data_variable_names(['Time', 'Matrix', 'CorrectAnswer', 'RT'])

learningMatrix = getPreviousMatrix(subjectName, 0, 'PreLearn')
exp.add_experiment_info('Learning: ')  # Save Subject Code
exp.add_experiment_info(str(learningMatrix))  # Add listPictures
if only_faces:
    local_learning_matrix = [element for index, element in enumerate(learningMatrix) if matrixTemplate[index] < 4]
    exp.add_experiment_info('faces_only_matrix:')
    exp.add_experiment_info(str(local_learning_matrix))  # Add listPictures
elif only_places:
    local_learning_matrix = [element for index, element in enumerate(learningMatrix) if matrixTemplate[index] > 3]
    exp.add_experiment_info('places_only_matrix:')
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
elif only_places:
    local_random_matrix = [element for index, element in enumerate(randomMatrix) if matrixTemplate[index] > 3]
    exp.add_experiment_info('places_only_random_matrix:')
    exp.add_experiment_info(str(local_random_matrix))  # Add listPictures
else:
    local_random_matrix = randomMatrix

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

wait_for_ttl_keyboard()
exp.add_experiment_info(['TTL_RECEIVED_timing_{}'.format(exp.clock.time)])

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

ISI = design.randomize.rand_int(300, 500)
exp.clock.wait(ISI, process_control_events=True)

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

exp.add_experiment_info('Presentation Order: ')  # Save Presentation Order

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

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, ' RECOGNITION ', draw=False)
bs.present(False, True)

exp.clock.wait(shortRest, process_control_events=True)

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

# LOG and SYNC
exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info

button_size = (cardSize[0]/2 + m.gap/8, cardSize[1])
matrixA_position = (cardSize[0]/4 + m.gap/4, 0)
matrixNone_position = (-cardSize[0]/4 - m.gap/4, 0)

matrixA = stimuli.TextBox(text='R', size=button_size,
                          position=matrixA_position,
                          text_size=textSize,
                          text_colour=constants.C_GREEN,
                          background_colour=cardColor)

matrixNone = stimuli.TextBox('W', size=button_size,
                             position=matrixNone_position,
                             text_size=textSize,
                             text_colour=constants.C_RED,
                             background_colour=cardColor)

ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
exp.clock.wait(ISI, process_control_events=True)

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
        'ShowCard_pos_{}_card_{}_timing_{}'.format(locationCard, listCards[nCard], exp.clock.time))

    exp.clock.wait(presentationCard, process_control_events=True)
    m.plotCard(locationCard, False, bs, True)
    exp.add_experiment_info(['HideCard_pos_{}_card_{}_timing_{}'.format(locationCard,
                                                                        listCards[nCard],
                                                                        exp.clock.time)])  # Add sync info
    ISI = design.randomize.rand_int(300, 500)
    exp.clock.wait(ISI, process_control_events=True)

    m.plotCueCard(False, bs, draw=False, nocross=True)
    matrixA.plot(bs)
    matrixNone.plot(bs)
    bs.present(False, True)

    time_left = responseTime
    valid_response = False
    rt = 0
    while not valid_response and rt is not None:
        mouse.show_cursor(True, True)

        start = get_time()
        rt, position = readMouse(start, mouseButton, time_left)  # time_left instead of response tine

        mouse.hide_cursor(True, True)

        if rt is not None:
            if matrixA.overlapping_with_position(position):
                valid_response = True
                exp.data.add([exp.clock.time, showMatrix, bool(presentationOrder[1][nCard] == 0), rt])
                matrixA = stimuli.TextBox(text='R', size=button_size,
                                          position=matrixA_position,
                                          text_size=textSize,
                                          text_colour=constants.C_GREEN,
                                          background_colour=clickColor)
                matrixA.plot(bs)
                bs.present(False, True)
                exp.clock.wait(clicPeriod, process_control_events=True)
                matrixA = stimuli.TextBox(text='R', size=button_size,
                                          position=matrixA_position,
                                          text_size=textSize,
                                          text_colour=constants.C_GREEN,
                                          background_colour=cardColor)
                matrixA.plot(bs)
                bs.present(False, True)
                exp.add_experiment_info(['Response_{}_timing_{}'.format('MatrixA', exp.clock.time)])  # Add sync info

            elif matrixNone.overlapping_with_position(position):
                valid_response = True
                exp.data.add([exp.clock.time, category, showMatrix, bool(presentationOrder[1][nCard] == 1), rt])
                matrixNone = stimuli.TextBox('W', size=button_size,
                                             position=matrixNone_position,
                                             text_size=textSize,
                                             text_colour=constants.C_RED,
                                             background_colour=clickColor)

                matrixNone.plot(bs)
                bs.present(False, True)
                exp.clock.wait(clicPeriod, process_control_events=True)
                matrixNone = stimuli.TextBox('W', size=button_size,
                                             position=matrixNone_position,
                                             text_size=textSize,
                                             text_colour=constants.C_RED,
                                             background_colour=cardColor)
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

    ISI = design.randomize.rand_int(300, 500)
    exp.clock.wait(ISI, process_control_events=True)

    m.plotCueCard(False, bs, draw=True)

    ISI = design.randomize.rand_int(300, 500)
    exp.clock.wait(ISI, process_control_events=True)

    bs.present(False, True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, ending_screen_text[language], draw=False)
bs.present(False, True)

exp.clock.wait(thankYouRest, process_control_events=True)
m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

control.end()
