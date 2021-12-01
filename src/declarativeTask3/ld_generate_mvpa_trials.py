import sys
import os

import numpy as np
from expyriment import control, stimuli, io, design, misc

from declarativeTask3.config import experiment_session, \
    experiment_use_faces_or_places, mvpa_equalize_number_correctly_recalled_images, \
    center_card_position, removeCards, mvpa_number_blocks, mvpa_number_trials_correct_position, \
    mvpa_number_trials_wrong_position, only_faces_remove_cards, only_places_remove_cards, \
    mvpa_block_number_TRs_to_wait_inter_trials_for_correct_positions, \
    mvpa_block_number_TRs_to_wait_inter_trials_for_wrong_positions, \
    matrixSize, windowSize
from declarativeTask3.ld_matrix import LdMatrix
from declarativeTask3.ld_utils import getPreviousMatrix, getPlacesOrFacesChoice, \
    getPreviouslyCorrectlyRecalledImages, newRandomPresentation, rename_output_files_to_BIDS


arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject
experimentName = arguments[0]
subjectName = arguments[1]

m = LdMatrix(matrixSize, windowSize, recognition_bigger_cuecard=True)  # Create Matrix
learningMatrix = getPreviousMatrix(subjectName, 0, 'PreLearn')
faces_places_choice = getPlacesOrFacesChoice(subjectName, 0, 'choose-faces-places')

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
not_recalled_places_locations = [index for (index, correctly_recalled) in correctly_recalled_places.items()
                                 if correctly_recalled is False]
# position indexes are 0 to 48 excluding 24

# Equalizing number correctly remembered images to present during MVPA
if mvpa_equalize_number_correctly_recalled_images:
    if len(not_recalled_faces_locations) != len(not_recalled_places_locations):
        number_not_correctly_recalled_images = max(len(not_recalled_faces_locations),
                                                   len(not_recalled_places_locations))
        number_images_to_add = number_not_correctly_recalled_images - min(len(not_recalled_faces_locations),
                                                                          len(not_recalled_places_locations))
        if len(not_recalled_faces_locations) < number_not_correctly_recalled_images:
            items_to_choose_among = [index for (index, correctly_recalled) in correctly_recalled_faces.items()
                                     if correctly_recalled is True]
            for i in range(number_images_to_add):
                not_recalled_faces_locations +=\
                    [items_to_choose_among.pop(np.random.randint(len(items_to_choose_among)))]
        elif len(not_recalled_places_locations) < number_not_correctly_recalled_images:
            items_to_choose_among = [index for (index, correctly_recalled) in correctly_recalled_places.items()
                                     if correctly_recalled is True]
            for i in range(number_images_to_add):
                not_recalled_places_locations +=\
                    [items_to_choose_among.pop(np.random.randint(len(items_to_choose_among)))]

not_recalled_faces_matrix_indexes = [index if index < center_card_position else index - 1 for
                                     index in not_recalled_faces_locations]
not_recalled_places_matrix_indexes = [index if index < center_card_position else index - 1 for
                                      index in not_recalled_places_locations]
# matrix indexes are 0 to 47
not_recalled_faces = [learningMatrix[position] for position in not_recalled_faces_matrix_indexes]
not_recalled_places = [learningMatrix[position] for position in not_recalled_places_matrix_indexes]


# Generate Vector of trials for the full experiment:
presentationOrder = [None] * mvpa_number_blocks
randomMatrix = [None] * mvpa_number_blocks
for n_block in range(mvpa_number_blocks):
    # Generating new wrong location trials
    randomMatrix[n_block] = m.newRecognitionMatrix(learningMatrix)
    local_random_matrix = randomMatrix[n_block]
    not_recalled_faces_location_in_random_matrix = [local_random_matrix.index(image) for image in not_recalled_faces]
    not_recalled_places_location_in_random_matrix = [local_random_matrix.index(image) for image in not_recalled_places]

    # Adding Faces Trial
    presentationMatrixLearningOrder_faces = newRandomPresentation(
        number_trials=mvpa_number_trials_correct_position, override_remove_cards=only_faces_remove_cards +
                                                                                 not_recalled_faces_locations)
    presentationMatrixRandomOrder_faces = newRandomPresentation(
        presentationMatrixLearningOrder_faces, number_trials=mvpa_number_trials_wrong_position,
        override_remove_cards=only_faces_remove_cards + not_recalled_faces_location_in_random_matrix)
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
    presentationMatrixRandomOrder_places = newRandomPresentation(
        presentationMatrixLearningOrder_places, number_trials=mvpa_number_trials_wrong_position,
        override_remove_cards=only_places_remove_cards + not_recalled_places_location_in_random_matrix)
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

    # Ensuring we only use integers
    for trial_list in trials_list_to_present:
        trial_list.astype(int)

    block_presentationOrder = np.hstack(tuple(trials_list_to_present))
    block_presentationOrder = block_presentationOrder[:, np.random.permutation(block_presentationOrder.shape[1])]
    presentationOrder[n_block] = block_presentationOrder


# SAVE RESULTS

session = experiment_session[experimentName]
session_dir = os.path.normpath(os.path.join('sourcedata', 'sub-' + subjectName, 'ses-' + session))
output_dir = os.path.normpath(os.path.join(session_dir, 'beh'))
if not os.path.isdir(session_dir):
    os.mkdir(session_dir)
io.defaults.datafile_directory = output_dir
io.defaults.eventfile_directory = output_dir

control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=True)
exp = design.Experiment(experimentName)  # Save experiment name
control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

bids_datafile, bids_eventfile = rename_output_files_to_BIDS(subjectName, session, experimentName,
                                                            io.defaults.datafile_directory,
                                                            io.defaults.eventfile_directory)
exp.data.rename(bids_datafile)
exp.events.rename(bids_eventfile)

exp.add_experiment_info('Subject: ')
exp.add_experiment_info(subjectName)
exp.add_experiment_info('Learning: ')
exp.add_experiment_info(str(learningMatrix))
exp.add_experiment_info('PresentationOrder')
exp.add_experiment_info(str(presentationOrder))
exp.add_experiment_info('RandomMatrix')
exp.add_experiment_info(str(randomMatrix))

control.end()
