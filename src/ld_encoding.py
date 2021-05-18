import sys

import numpy as np
import random
from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants
from expyriment.misc._timer import get_time

from ld_matrix import LdMatrix
from ld_utils import newSoundAllocation, getPreviousSoundsAllocation, getPreviousMatrixOrder
from ld_utils import setCursor, newRandomPresentation, getPreviousMatrix, getLanguage, path_leaf, readMouse
from ld_sound import create_temp_sound_files, delete_temp_files
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

# Save time, nblocks, position, correctAnswer, RT
exp.add_data_variable_names(['Time', 'NBlock', 'Picture', 'Answers', 'RT'])

keepMatrix = True
if experimentName == 'Encoding':
    keepPreviousMatrix = False
    no_feedback = False
    cuecard_response_logging_text = 'CorrectCueCardResponse'
elif experimentName == 'Test-Encoding':
    keepPreviousMatrix = True
    nbBlocksMax = 1
    no_feedback = True
    cuecard_response_logging_text = 'CueCardResponse'
elif experimentName == 'ReTest-Encoding':
    keepPreviousMatrix = True
    nbBlocksMax = 1
    no_feedback = True
    cuecard_response_logging_text = 'CueCardResponse'

exp.add_experiment_info('Image categories (original order; src/config.py order): ')
exp.add_experiment_info(str(classPictures))

matrices = []
pictures_allocation = []
for i, category in enumerate(classPictures):
    if keepPreviousMatrix:
        previousMatrix = getPreviousMatrix(subjectName, 0, 'Encoding', i, category)
    else:
        previousMatrix = None
    matrices.append(LdMatrix(matrixSize, windowSize))  # Create matrices
    pictures_allocation.append(matrices[i].findMatrix(category, previousMatrix, keepMatrix))  # Find pictures_allocation
    matrices[i].associateCategory(category)

control.initialize(exp)

for i, category in enumerate(classPictures):
    matrices[i].associatePictures(pictures_allocation[i])  # Associate Pictures to cards
    exp.add_experiment_info('matrix {}, pictures from class {}:'.format(i, category))
    exp.add_experiment_info(str(matrices[i].listPictures))  # Add listPictures

soundsAllocation_index = getPreviousSoundsAllocation(subjectName, 0, 'choose-sound-association')
soundsAllocation = {key: sounds[soundsAllocation_index[key]] for key in soundsAllocation_index.keys()}

exp.add_experiment_info('Image classes order:')
exp.add_experiment_info(str(classPictures))
exp.add_experiment_info('Sounds order:')
exp.add_experiment_info(str(sounds))
exp.add_experiment_info('Image classes to sounds:')
exp.add_experiment_info(str(soundsAllocation))
exp.add_experiment_info('Image classes to sounds (index):')
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

correctAnswers = np.zeros((len(classPictures), nbBlocksMax))
currentCorrectAnswers = correctAnswers[0:len(classPictures), 0]
nBlock = 0

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], matrices[0].gap * 2 + cardSize[1]), position=(
    0, -windowSize[1]/float(2) + (2 * matrices[0].gap + cardSize[1])/float(2)), colour=constants.C_DARKGREY)

''' Presentation all locations '''
presentationOrder = newRandomPresentation()

instructions_ttl = stimuli.TextLine(ttl_instructions_text[language],
                                    position=(
                                        0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
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

new_matrix_presentation_order = None
learning_matrix_presentation_order = None
matrices_to_present = np.array(range(len(classPictures)))
# if experimentName == 'Encoding':
#     test_matrix_presentation_order = None
# elif experimentName == 'Test-Encoding':
#     test_matrix_presentation_order = getPreviousMatrixOrder(subjectName, 0, 'Encoding')
# elif experimentName == 'ReTest-Encoding':
#     test_matrix_presentation_order = getPreviousMatrixOrder(subjectName, 0, 'Test-Encoding')

while min(currentCorrectAnswers) < correctAnswersMax and nBlock < nbBlocksMax:

    # TODO change this line <1 != nbBlocksMax> to reflect relevant experiment more accurately
    # PRESENTATION BLOCK
    if 1 != nbBlocksMax or experimentName == 'Encoding':
        exp.add_experiment_info('Presentation_Block_{}_timing_{}'.format(nBlock, exp.clock.time))

        if len(matrices_to_present) > 2:
            while new_matrix_presentation_order == learning_matrix_presentation_order:
                new_matrix_presentation_order = list(np.random.permutation(matrices_to_present))
        else:
            new_matrix_presentation_order = list(np.random.permutation(matrices_to_present))
        learning_matrix_presentation_order = new_matrix_presentation_order
        exp.add_experiment_info(
            'Presentation_Block_{}_MatrixPresentationOrder_{}_timing_{}'.format(nBlock,
                                                                                learning_matrix_presentation_order,
                                                                                exp.clock.time))  # Add sync info
        instructions = stimuli.TextLine(presentation_screen_text[language],
                                        position=(0, -windowSize[1]/float(2) + (2*matrices[0].gap + cardSize[1])/float(2)),
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

        for i in learning_matrix_presentation_order:
            presentationOrder = newRandomPresentation(presentationOrder)
            matrix_i = matrices[i]
            matrix_i.plotDefault(bs, True)

            exp.add_experiment_info('Presentation_Block_{}_matrix_{}_category_{}_timing_{}'.format(
                nBlock, i, matrix_i._category, exp.clock.time))
            exp.add_experiment_info(str(presentationOrder))
            instructions = stimuli.TextLine(
                presentation_screen_text[language] + classNames[language][matrix_i._category] + ' ',
                position=(0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
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
                matrix_i.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
                exp.clock.wait(SoundBeforeImageTime)
                matrix_i.plotCard(nCard, True, bs, True)  # Show Location for ( 2s )
                exp.add_experiment_info('ShowCard_pos_{}_card_{}_timing_{}_sound_{}'.format(
                    nCard, matrix_i.listPictures[nCard], exp.clock.time,
                    sounds[soundsAllocation_index[matrix_i._category]]))

                exp.clock.wait(presentationCard)
                matrix_i.plotCard(nCard, False, bs, True)
                exp.add_experiment_info('HideCard_pos_{}_card_{}_timing_{}'.format(
                    nCard, matrix_i.listPictures[nCard], exp.clock.time))  # Add sync info

                ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
                exp.clock.wait(ISI)

            ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
            exp.clock.wait(ISI)

        # REST BLOCK
        instructions = stimuli.TextLine(
            rest_screen_text[language],
            position=(0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
            text_font=None, text_size=textSize, text_bold=None, text_italic=None,
            text_underline=None, text_colour=textColor, background_colour=bgColor,
            max_width=None)

        instructions.plot(bs)
        bs.present(False, True)
        exp.add_experiment_info(
            ['StartShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
        exp.clock.wait(restPeriod)
        exp.add_experiment_info(
            ['EndShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
        instructionRectangle.plot(bs)
        bs.present(False, True)

    # TEST BLOCK
    instructions = stimuli.TextLine(' TEST ',
                                    position=(
                                        0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
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

    trials_order = []
    pictures_allocation = [list(picture_matrix) for picture_matrix in pictures_allocation]
    pictures_allocation = [[card.rstrip('.png') for card in picture_matrix] for picture_matrix in pictures_allocation]
    trials_order = sum(pictures_allocation, [])
    trials_order = [card.rstrip('.png') for card in trials_order]
    random.shuffle(trials_order)

    exp.add_experiment_info(
        f'Test_Block_{nBlock}_timing_{exp.clock.time}')  # Add sync info
    exp.add_experiment_info(f'Test_Block_{nBlock}_Presentation_Order')
    exp.add_experiment_info(trials_order)
    matrix_i = matrices[0]
    matrix_i.plotDefault(bs, True)
    for trial_index, card in enumerate(trials_order):
        cueCards = []
        category = card[0]
        matrix_index = classPictures.index(category)
        matrix_i = matrices[matrix_index]
        pos = pictures_allocation[matrix_index].index(card)
        cueCards.append({'correct_card': True, 'category': category, 'card': card, 'pos': pos,
                         'matrix_index': matrix_index})
        exp.add_experiment_info(
            f"Trial_trialIndex_{str(trial_index)}_matrix_{category}"
            f"_pos_{pos}_card_{card}_timing_{exp.clock.time}")

        other_indexes = list(range(len(classPictures)))
        other_indexes.pop(matrix_index)
        for i, other_matrix_index in enumerate(other_indexes):
            cueCards.append({})
            cueCards[i + 1]['correct_card'] = False
            cueCards[i + 1]['card'] = random.choice(pictures_allocation[other_matrix_index])
            cueCards[i + 1]['category'] = cueCards[i + 1]['card'][0]
            cueCards[i + 1]['matrix_index'] = classPictures.index(cueCards[i + 1]['category'])
            cueCards[i + 1]['pos'] = pictures_allocation[other_matrix_index].index(cueCards[i + 1]['card'])

        random.shuffle(cueCards)

        matrix_i.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
        exp.clock.wait(SoundBeforeImageTime)

        for i in range(len(classPictures)):
            cuecard_matrix = matrices[cueCards[i]['matrix_index']]
            cuecard_pos = cueCards[i]['pos']
            cuecard_card = cueCards[i]['card']
            matrix_i._cueCard[i].setPicture(cuecard_matrix._matrix.item(cuecard_pos).stimuli[0].filename)
            matrix_i.plotCueCard(i, True, bs, True)
            exp.add_experiment_info(
                f"ShowCueCard_trialIndex_{str(trial_index)}_cueCardIndex_{i}_matrix_{cueCards[i]['category']}"
                f"_pos_{cuecard_pos}_card_{cuecard_card}_timing_{exp.clock.time}")
        exp.clock.wait(presentationCard)

        instructions = stimuli.TextLine(choose_image_text[language],
                                        position=(
                                            0,
                                            -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
                                        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                        text_underline=None, text_colour=textColor,
                                        background_colour=bgColor,
                                        max_width=None)
        instructions.plot(bs)
        bs.present(False, True)

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
                chosenCueCard_index = matrix_i.checkPosition(position, cue_card=True)
                if chosenCueCard_index is not None:
                    chosenCueCard = cueCards[chosenCueCard_index]
                    matrix_cueCard = matrix_i._cueCard[chosenCueCard_index]

                    if chosenCueCard['correct_card'] or \
                            (experimentName == 'Test-Encoding' or experimentName == 'ReTest-Encoding'):
                        exp.add_experiment_info(
                            f"{cuecard_response_logging_text}_trialIndex_{str(trial_index)}"
                            f"_cueCardIndex_{chosenCueCard_index}"
                            f"_matrix_{chosenCueCard['category']}"
                            f"_pos_{chosenCueCard['pos']}"
                            f"_card_{chosenCueCard['card']}"
                            f"_timing_{exp.clock.time}"
                        )
                        instructionRectangle.plot(bs)
                        bs.present(False, True)
                        matrix_i.response_feedback_stimuli_frame(bs, matrix_cueCard.position, True,
                                                                 show_or_hide=True, draw=True, no_feedback=no_feedback)
                        exp.clock.wait(feedback_time)
                        matrix_i.response_feedback_stimuli_frame(bs, matrix_cueCard.position, True,
                                                                 show_or_hide=False, draw=True, no_feedback=no_feedback)
                        instructions = stimuli.TextLine(choose_position_text[language],
                                                        position=(
                                                            0,
                                                            -windowSize[1] / float(2) + (
                                                                        2 * matrices[0].gap + cardSize[1]) / float(2)),
                                                        text_font=None, text_size=textSize, text_bold=None,
                                                        text_italic=None,
                                                        text_underline=None, text_colour=textColor,
                                                        background_colour=bgColor,
                                                        max_width=None)
                        instructions.plot(bs)
                        bs.present(False, True)
                        time_left = responseTime - rt - clicPeriod
                        # Ensuring participants have AT LEAST 3s (of value written in config file) to answer
                        if time_left < choose_location_minimum_response_time:
                            time_left = choose_location_minimum_response_time
                        valid_response = True
                        matrix_valid_response = False
                        while not matrix_valid_response:
                            mouse.show_cursor(True, True)
                            start = get_time()
                            rt, position = readMouse(start, mouseButton, time_left)
                            mouse.hide_cursor(True, True)
                            if rt is not None:
                                currentCard = matrix_i.checkPosition(position)
                                if currentCard is not None:
                                    # Click effect feedback block
                                    if currentCard not in removeCards:
                                        matrix_i._matrix.item(currentCard).color = clickColor
                                        matrix_i.plotCard(currentCard, False, bs, True)
                                        exp.clock.wait(clicPeriod)  # Wait 200ms
                                        matrix_i._matrix.item(currentCard).color = cardColor
                                        matrix_i.plotCard(currentCard, False, bs, True)
                                    instructionRectangle.plot(bs)
                                    bs.present(False, True)
                                    matrix_valid_response = True
                                    try:
                                        exp.add_experiment_info(
                                            f"MatrixResponse_trialIndex_{str(trial_index)}"
                                            f"_matrix_{chosenCueCard['category']}"
                                            f"_pos_{currentCard}"
                                            f"_card_{(matrices[chosenCueCard['matrix_index']]).listPictures[currentCard]}"
                                            f"_timing_{exp.clock.time}"
                                        )
                                    except:
                                        exp.add_experiment_info(
                                            'MatrixResponse_pos_{}_ERROR_timing_{}'.format(currentCard, exp.clock.time))
                                    if currentCard == chosenCueCard['pos']:
                                        if experimentName == 'Encoding' and nbBlocksMax != 1:
                                            matrix_i.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
                                        correctAnswers[matrix_index, nBlock] += 1
                                    exp.data.add([exp.clock.time, nBlock,
                                                  path_leaf(matrix_i._matrix.item(chosenCueCard['pos']).stimuli[0].filename),
                                                  path_leaf(matrix_i._matrix.item(currentCard).stimuli[0].filename),
                                                  rt])
                                else:
                                    if rt < time_left - clicPeriod:
                                        time_left = time_left - rt - clicPeriod
                                    else:
                                        exp.add_experiment_info(
                                            f"NoMatrixCardResponse_trialIndex_{str(trial_index)}"
                                            f"_timing_{exp.clock.time}")
                                        exp.data.add([exp.clock.time, nBlock,
                                                      path_leaf(matrix_i._matrix.item(chosenCueCard['pos']).stimuli[0].filename),
                                                      None,
                                                      rt])
                                        matrix_valid_response = True
                            else:
                                exp.add_experiment_info(
                                    f"NoMatrixCardResponse_trialIndex_{str(trial_index)}_timing_{exp.clock.time}")
                                matrix_valid_response = True

                    else:
                        exp.add_experiment_info(
                            f"WrongCueCardResponse_trialIndex_{str(trial_index)}"
                            f"_cueCardIndex_{chosenCueCard_index}"
                            f"_matrix_{chosenCueCard['category']}"
                            f"_pos_{chosenCueCard['pos']}"
                            f"_card_{chosenCueCard['card']}"
                            f"_timing_{exp.clock.time}"
                        )
                        instructionRectangle.plot(bs)
                        bs.present(False, True)
                        valid_response = True
                        matrix_i.response_feedback_stimuli_frame(bs, matrix_cueCard.position, False,
                                                                 show_or_hide=True, draw=True)
                        exp.clock.wait(feedback_time)
                        matrix_i.response_feedback_stimuli_frame(bs, matrix_cueCard.position, False,
                                                                 show_or_hide=False, draw=True)

                        exp.clock.wait(inter_feedback_delay_time)
                        for k in range(len(classPictures)):
                            if cueCards[k]['correct_card']:
                                break

                        # We use subject_correct parameter set to True in order to have green feedback on the correct
                        # image/card
                        matrix_i.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
                        matrix_i.response_feedback_stimuli_frame(bs, (matrix_i._cueCard[k]).position, True,
                                                                 show_or_hide=True, draw=True)
                        exp.clock.wait(feedback_time)
                        matrix_i.response_feedback_stimuli_frame(bs, (matrix_i._cueCard[k]).position, True,
                                                                 show_or_hide=False, draw=True)
                else:
                    if rt < time_left - clicPeriod:
                        time_left = time_left - rt - clicPeriod
                    else:
                        exp.add_experiment_info(f"NoCueCardResponse_trialIndex_{str(trial_index)}_timing_{exp.clock.time}")
                        valid_response, rt = True, None
            else:
                exp.add_experiment_info(f"NoCueCardResponse_trialIndex_{str(trial_index)}_timing_{exp.clock.time}")
        instructionRectangle.plot(bs)
        bs.present(False, True)

        for i in range(len(classPictures)):
            matrix_i.plotCueCard(i, False, bs, True)
            exp.add_experiment_info(
                f"HideCueCard_trialIndex_{str(trial_index)}_cueCardIndex_{i}_matrix_{cueCards[i]['category']}"
                f"_pos_{cuecard_pos}_card_{cuecard_card}_timing_{exp.clock.time}")

        # Longer than usual time between two trials, in order to ensure sounds aren't mixed up by participants
        exp.clock.wait(presentationCard)
        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI)

    if nbBlocksMax != 1 and experimentName != 'Encoding':
        matrix_i.plotDefault(bs, draw=True, show_matrix=False)
        results_feedback = f"""You got:
        {classNames[language][classPictures[0]]}: {str(int(correctAnswers[0, nBlock]))} out of {str(matrices[0]._matrix.size - len(removeCards))}
        {classNames[language][classPictures[1]]}: {str(int(correctAnswers[1, nBlock]))} out of {str(matrices[1]._matrix.size - len(removeCards))}
        {classNames[language][classPictures[2]]}: {str(int(correctAnswers[2, nBlock]))} out of {str(matrices[2]._matrix.size - len(removeCards))}"""
        instructions = stimuli.TextBox(results_feedback,
                                       size=(windowSize[0], 4 * cardSize[1]),
                                       position=(0, 0),
                                       text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                       text_underline=None, text_colour=textColor,
                                       background_colour=bgColor,
                                       text_justification=0)
        instructionRectangle_results = stimuli.Rectangle(size=(windowSize[0], 4 * cardSize[1]), position=(0, 0),
                                                         colour=constants.C_DARKGREY)

        instructions.plot(bs)
        bs.present(False, True)
        exp.clock.wait(shortRest)
        instructionRectangle_results.plot(bs)
        bs.present(False, True)

        pictures_allocation = [np.asarray([card + '.png' for card in picture_matrix])
                               for picture_matrix in pictures_allocation]
        for i, category in enumerate(classPictures):
            matrices[i].associatePictures(pictures_allocation[i])
        matrix_i = matrices[0]
        matrix_i.plotDefault(bs, True)
        for i in range(len(classPictures)):
            matrix_i.plotCueCard(i, False, bs, draw=True)

    if ignore_learned_matrices and correctAnswers[i, nBlock] > correctAnswersMax:
        matrices_to_present = np.delete(matrices_to_present, i)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI)
    exp.clock.wait(shortRest)

    instructions = stimuli.TextLine(
        rest_screen_text[language],
        position=(0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
        text_underline=None, text_colour=textColor, background_colour=bgColor,
        max_width=None)

    instructions.plot(bs)
    bs.present(False, True)
    exp.add_experiment_info(
        ['StartShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
    exp.clock.wait(restPeriod)
    exp.add_experiment_info(
        ['EndShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
    instructionRectangle.plot(bs)
    bs.present(False, True)

    currentCorrectAnswers = correctAnswers[:, nBlock]
    nBlock += 1

instructions = stimuli.TextLine(
    ending_screen_text[language],
    position=(0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
    text_underline=None, text_colour=textColor, background_colour=bgColor,
    max_width=None)

instructions.plot(bs)
bs.present(False, True)
exp.clock.wait(thankYouRest)
instructionRectangle.plot(bs)
bs.present(False, True)

control.end()

delete_temp_files()
