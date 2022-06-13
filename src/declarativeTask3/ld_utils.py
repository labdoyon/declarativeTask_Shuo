import ast
import ntpath
import os
import random

import keyboard
import pygame
from datetime import datetime
from time import time
import re

import numpy as np
from dateutil.parser import parse
from expyriment import misc, stimuli
from expyriment.io import Keyboard
from expyriment.misc._timer import get_time
from expyriment.misc.geometry import coordinates2position

from declarativeTask3.config import linesThickness, cardSize, colorLine, windowSize, bgColor, matrixSize, removeCards
from declarativeTask3.config import classPictures, sessions, rawFolder, ttl_characters
from declarativeTask3.config import number_ttl_in_rest_period, number_ttl_before_rest_period
from declarativeTask3.ttl_catch_keyboard import wait_for_ttl_keyboard_and_log_ttl
sep = os.path.sep


def checkWindowParameters(iWindowSize):
    result = False

    originalResolution = misc.get_monitor_resolution()

    if iWindowSize[0] <= originalResolution[0] and iWindowSize[1] <= originalResolution[1]:
        result = True

    return result


def drawLines(windowSize, gap, bs):

    linesPositions = np.empty([2,2], object)
    linesPositions[0,0] = (-windowSize[0]/float(2), windowSize[1]/float(2) - 2 * gap - cardSize[0] - linesThickness / float(2))
    linesPositions[0,1] = (windowSize[0]/float(2), windowSize[1]/float(2) - 2 * gap - cardSize[0] - linesThickness / float(2))
    linesPositions[1,0] = (-windowSize[0]/float(2), -windowSize[1]/float(2) + 2 * gap + cardSize[1] + linesThickness / float(2))
    linesPositions[1,1] = (windowSize[0]/float(2), -windowSize[1]/float(2) + 2 * gap + cardSize[1] + linesThickness / float(2))

    lines = np.empty([2], object)
    lines[0] = stimuli.Line(linesPositions[0,0], linesPositions[0,1], linesThickness, colour=colorLine, anti_aliasing=None)
    lines[1] = stimuli.Line(linesPositions[1,0], linesPositions[1,1], linesThickness, colour=colorLine, anti_aliasing=None)

    for line in lines:
        line.plot(bs)

    bs.present()


def plotLine(bs, gap, color=bgColor):
    linePositions = np.empty([2], object)
    linePositions[0] = (-cardSize[0]/float(2), windowSize[1]/float(2) - 2*gap - cardSize[0] - linesThickness/float(2))
    linePositions[1] = (cardSize[0]/float(2), windowSize[1]/float(2) - 2*gap - cardSize[0] - linesThickness/float(2))

    line = stimuli.Line(linePositions[0], linePositions[1], linesThickness, colour=color)
    line.plot(bs)

    return bs


def newRandomPresentation(oldPresentation=None, override_remove_cards=None, number_trials=None):
    if override_remove_cards is not None:
        removeCards = override_remove_cards
    else:
        from declarativeTask3.config import removeCards

    newPresentation = np.array(range(matrixSize[0]*matrixSize[1]), dtype=int)
    if len(removeCards):
        removeCards.sort(reverse=True)
        for nCard in removeCards:
            newPresentation = np.delete(newPresentation, nCard)

    if number_trials is not None:
        if not isinstance(number_trials, int):
            raise TypeError("<number_trials> should be an integer")
        if not number_trials >= 0:
            raise TypeError("<number_trials> should be a positive integer (0 is valid)")

        default_trials = np.copy(newPresentation)
        if number_trials > len(newPresentation):
            quotient, remainder = divmod(number_trials, len(newPresentation))
            # if the number of trials is several times (more than 1 time) the size of the matrix
            # Quotient
            for i in range(quotient-1):
                newPresentation = np.hstack((newPresentation, default_trials))
            # Remainder
            trials_to_be_added = default_trials
            np.random.shuffle(trials_to_be_added)
            trials_to_be_added = trials_to_be_added[:remainder]
            newPresentation = np.hstack((newPresentation, trials_to_be_added))
            np.random.shuffle(newPresentation)
        elif number_trials < len(newPresentation):
            np.random.shuffle(newPresentation)
            newPresentation = newPresentation[:number_trials]

    newPresentation = np.random.permutation(newPresentation)

    if oldPresentation is not None:
        while len(longestSubstringFinder(str(oldPresentation), str(newPresentation)).split()) > 3:
            newPresentation = np.random.permutation(newPresentation)

    return newPresentation


def longestSubstringFinder(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ""
    return answer


def getPreviousMatrix(subjectName, daysBefore, experienceName):

    currentDate = datetime.now()

    subject_dir = os.path.join(rawFolder, 'sourcedata', 'sub-' + subjectName)
    data_files = []
    for session in sessions:
        session_dir = os.path.join(subject_dir, 'ses-' + session, 'beh')
        if os.path.isdir(session_dir):
            data_files = data_files + \
                         [os.path.join(session_dir, file) for file in os.listdir(session_dir) if file.endswith('_beh.xpd') and
                          'task-' + experienceName in file]

    data_files.sort(reverse=True)  # latest runs first
    for dataFile in data_files:
        try:
            agg = misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
        except TypeError:
            continue
        previousDate = parse(agg[2]['date'])

        try:
            agg[3].index(experienceName)
        except (ValueError):
            continue

        if daysBefore == 0 or ((currentDate-previousDate).total_seconds() > 72000*daysBefore and (currentDate-previousDate).total_seconds() < 100800*daysBefore):
            header = agg[3].split('\n#e ')

            indexSubjectName = header.index('Subject:') + 1
            if subjectName in header[indexSubjectName]:
                print('File found: ' + dataFile)
                indexPositions = header.index('Positions pictures:') + 1
                previousMatrix = ast.literal_eval(header[indexPositions].split('\n')[0].split('\n')[0])
                return previousMatrix

    return None


def getPrevious(subjectName, daysBefore, experienceName, target):
    currentDate = datetime.now()

    data_files = []
    subject_dir = os.path.join(rawFolder, 'sourcedata', 'sub-' + subjectName)
    for session in sessions:
        session_dir = os.path.join(subject_dir, 'ses-' + session, 'beh')
        if os.path.isdir(session_dir):
            data_files = data_files + \
                [os.path.join(session_dir, file) for file in os.listdir(session_dir) if file.endswith('_beh.xpd') and
                 'task-' + experienceName in file]

    data_files.sort(reverse=True)  # latest runs first
    for data_file in data_files:
        try:
            agg = misc.data_preprocessing.read_datafile(data_file, only_header_and_variable_names=True)
            previousDate = parse(agg[2]['date'])
        except TypeError:  # values missing in data file, data file corrupted
            continue
        try:
            agg[3].index(experienceName)
        except ValueError:  # value not found
            continue
        if daysBefore == 0 or ((currentDate-previousDate).total_seconds() > 72000*daysBefore and (currentDate-previousDate).total_seconds() < 100800*daysBefore):
            header = agg[3].split('\n#e ')

            indexSubjectName = header.index('Subject:') + 1
            if subjectName in header[indexSubjectName]:
                print('File found: ' + data_file)
                indexPositions = header.index(target) + 1
                previousTarget = header[indexPositions].split('\n')[0].split('\n')[0]
                try:  # dictionary or list
                    output = ast.literal_eval(previousTarget)
                except (SyntaxError, ValueError):  # string
                    output = previousTarget
                return output

    return None


def getLanguage(subjectName, daysBefore, experienceName):
    currentDate = datetime.now()

    subject_dir = os.path.join(rawFolder, 'sourcedata', 'sub-' + subjectName)
    data_files = []
    for session in sessions:
        session_dir = os.path.join(subject_dir, 'ses-' + session, 'beh')
        if os.path.isdir(session_dir):
            data_files = data_files + \
                         [os.path.join(session_dir, file) for file in os.listdir(session_dir) if file.endswith('_beh.xpd') and
                          'task-' + experienceName in file]

    data_files.sort(reverse=True)  # latest runs first
    for dataFile in data_files:
        try:
            agg = misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
        except TypeError:
            continue
        previousDate = parse(agg[2]['date'])

        try:
            agg[3].index(experienceName)
        except ValueError:
            continue
        if daysBefore == 0 or ((currentDate-previousDate).total_seconds() > 72000*daysBefore and (currentDate-previousDate).total_seconds() < 100800*daysBefore):
            header = agg[3].split('\n#e ')

            indexSubjectName = header.index('Subject:') + 1
            if subjectName in header[indexSubjectName]:
                print('File found: ' + dataFile)
                indexPositions = header.index('language:') + 1
                language = header[indexPositions].split('\n')[0].split('\n')[0]
                output = language
                return output

    # This ensures the latest language choice is used
    return None


def getPlacesOrFacesChoice(subjectName, daysBefore, experienceName):
    currentDate = datetime.now()

    subject_dir = os.path.join(rawFolder, 'sourcedata', 'sub-' + subjectName)
    data_files = []
    for session in sessions:
        session_dir = os.path.join(subject_dir, 'ses-' + session, 'beh')
        if os.path.isdir(session_dir):
            data_files = data_files + \
                         [os.path.join(session_dir, file) for file in os.listdir(session_dir) if file.endswith('_beh.xpd') and
                          'task-' + experienceName in file]

    data_files.sort(reverse=True)  # latest runs first
    for dataFile in data_files:
        try:
            agg = misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
        except TypeError:
            continue
        previousDate = parse(agg[2]['date'])

        try:
            agg[3].index(experienceName)
        except ValueError:
            continue
        if daysBefore == 0 or ((currentDate-previousDate).total_seconds() > 72000*daysBefore and (currentDate-previousDate).total_seconds() < 100800*daysBefore):
            header = agg[3].split('\n#e ')

            indexSubjectName = header.index('Subject:') + 1
            if subjectName in header[indexSubjectName]:
                print('File found: ' + dataFile)
                indexPositions = header.index('start_by_class1_or_class2:') + 1
                places_or_faces_choice = header[indexPositions].split('\n')[0].split('\n')[0]
                output = places_or_faces_choice
                return output

    # This ensures the latest language choice is used
    return None


def getPreviouslyCorrectlyRecalledImages(subject_name, experienceName):
    subject_dir = os.path.join(rawFolder, 'sourcedata', 'sub-' + subject_name)
    data_files = []
    for session in sessions:
        session_dir = os.path.join(subject_dir, 'ses-' + session, 'beh')
        if os.path.isdir(session_dir):
            data_files = data_files + \
                         [os.path.join(session_dir, file) for file in os.listdir(session_dir) if
                          file.endswith('_beh.xpd') and
                          'task-' + experienceName in file]

    data_files.sort(reverse=True)  # latest runs first

    for dataFile in data_files:
        try:
            agg = misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
        except TypeError:
            continue
        try:
            agg[3].index(experienceName)
        except ValueError:
            continue
        header = agg[3].split('\n#e ')
        index_subject_name = header.index('Subject:') + 1
        if subject_name not in header[index_subject_name]:
            continue

        header = [element for element in header if 'ShowCueCard' in element or 'Response' in element]
        positions_correctly_recalled = {}
        for event in header:
            if 'ShowCueCard' in event:
                position = int(re.search('pos_([0-9]+)_', event).group(1))
                positions_correctly_recalled[position] = False
            elif 'Response' in event:
                if 'NoResponse' in event or 'pos_None_ERROR' in event:
                    positions_correctly_recalled[position] = False
                else:
                    response_position = int(re.search('pos_([0-9]+)_', event).group(1))
                    if response_position == position:
                        positions_correctly_recalled[position] = True
                    else:
                        positions_correctly_recalled[position] = False

        return positions_correctly_recalled

    return None


def normalize_presentation_order(presentation_order, learning_matrix, random_matrix):
    positions = [int(i) for i in presentation_order[0]]
    matrix_a_or_rec = [int(i) for i in presentation_order[1]]
    images = [random_matrix[position] if matrix_a_or_rec[index] else learning_matrix[position]
              for index, position in enumerate(positions)]

    while any([positions[i] == positions[i+1] for i in range(len(positions)-1)]) or \
            any([images[i] == images[i+1] for i in range(len(positions)-1)]):
        zipped_lists = list(zip(positions, matrix_a_or_rec, images))
        random.shuffle(zipped_lists)

        positions, matrix_a_or_rec, images = zip(*zipped_lists)
        positions, matrix_a_or_rec, images = list(positions), list(matrix_a_or_rec), list(images)

    new_presentation_order = np.array([np.array(positions), np.array(matrix_a_or_rec)])

    return new_presentation_order


def normalize_test_presentation_order(trials_order, pictures_allocation):
    positions = []
    for card in trials_order:
        category = card[0]
        matrix_index = classPictures.index(category)
        positions.append(pictures_allocation[matrix_index].index(card))

    while any([positions[i] == positions[i + 1] for i in range(len(positions) - 1)]):
        zipped_lists = list(zip(positions, trials_order))
        random.shuffle(zipped_lists)

        positions, trials_order = zip(*zipped_lists)
        positions, trials_order = list(positions), list(trials_order)

    return trials_order


def subfinder(mylist, pattern):
    answers = []
    for i in range(len(mylist) - len(pattern)+1):
        if np.all(mylist[i:i+len(pattern)] == pattern):
            answers.append(True)
        else:
            answers.append(False)

    try:
        answers.index(True)
    except ValueError:
        return False

    return True


def setCursor(arrow):
    hotspot = (0, 0)
    s2 = []
    for line in arrow:
        s2.append(line.replace('x', 'X').replace(',', '.').replace('O', 'o'))
    cursor, mask = pygame.cursors.compile(s2, 'X', '.', 'o')
    size = len(arrow[0]), len(arrow)
    pygame.mouse.set_cursor(size, hotspot, cursor, mask)


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def readMouse(startTime, button, duration=None):
    iKeyboard = Keyboard()
    if duration is not None:
        while int((get_time() - startTime) * 1000) <= duration:
            alle = pygame.event.get()
            rt = int((get_time() - startTime)*1000)
            for e in alle:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == button:
                    return rt, coordinates2position(e.pos)

            if iKeyboard.process_control_keys():
                break

        return None, None

    else:
        while True:
            alle = pygame.event.get()
            rt = int((get_time() - startTime)*1000)
            for e in alle:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == button:
                    return rt, coordinates2position(e.pos)

            if iKeyboard.process_control_keys():
                break
    #
    # if nBlock < 0:  # if nBlock == 0:
    #
    #     ''' Presentation all locations + memorization'''
    #
    #     list = np.random.permutation(m.size[0] * m.size[1])
    #     list = list.tolist()
    #     list.remove((m.size[0]*m.size[1])/2)
    #
    #     for nCard in list:
    #         isLearned = False
    #
    #         while not isLearned:
    #             mouse.hide_cursor(True, True)
    #             bs = m.plotCard(nCard,True,bs)  # Show Location for ( 2s )
    #             bs.present(False, True)
    #             exp.clock.wait(presentationCard)
    #
    #             bs = m.plotCard(nCard, False, bs)  # Hide Location
    #             m._cueCard.setPicture(m._matrix.item(nCard).stimuli[0].filename)
    #             bs = m.plotCueCard(True, bs)  # Show Cue
    #             bs.present(False, True)  # Update Screen
    #
    #             exp.clock.wait(presentationCard)  # Wait
    #
    #             bs = m.plotCueCard(False, bs)  # Hide Cue
    #             bs.present(False, True)  # Update Screen
    #             mouse.show_cursor(True, True)  # Show cursor
    #
    #             position = None
    #             [event_id, position, rt] = mouse.wait_press(buttons=None, duration=responseTime, wait_for_buttonup=True)
    #
    #             if position is not None:
    #                 if m.checkPosition(position) == nCard:
    #                     mouse.hide_cursor(True, True)
    #                     isLearned = True
    #
    #             ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    #             exp.clock.wait(ISI)


def absoluteTime(firstTime):
    return int((time()*1000))-firstTime


def vertices_frame(size, frame_thickness):
    return [(size[0]-frame_thickness, 0),
            (0, -size[1]),
            (-size[0], 0),
            (0, size[1]),
            (frame_thickness, 0),
            (0, -(size[1]-frame_thickness)),
            (size[0]-2*frame_thickness, 0),
            (0, size[1]-2*frame_thickness),
            (-(size[0]-2*frame_thickness), 0)]


def generate_bids_filename(subject_id, session, task, filename_suffix='_beh', filename_extension='.xpd',
                           run=None):
    if run is None:
        return 'sub-' + subject_id + '_ses-' + session + '_task-' + task + filename_suffix + filename_extension
    else:
        return 'sub-' + subject_id + '_ses-' + session + '_task-' + task +\
               '_run-' + str(run) +\
               filename_suffix + filename_extension


def rename_output_files_to_BIDS(subject_name, session, experiment_name,
                                datafile_dir, eventfile_dir):
    i = 1
    wouldbe_datafile = generate_bids_filename(
        subject_name, session, experiment_name, filename_suffix='_beh', filename_extension='.xpd')
    wouldbe_eventfile = generate_bids_filename(
        subject_name, session, experiment_name, filename_suffix='_events', filename_extension='.xpe')

    while os.path.isfile(datafile_dir + os.path.sep + wouldbe_datafile) or \
            os.path.isfile(eventfile_dir + os.path.sep + wouldbe_eventfile):
        i += 1
        i_string = '0' * (2 - len(str(i))) + str(i)  # 0 padding, assuming 2-digits number
        wouldbe_datafile = generate_bids_filename(subject_name, session, experiment_name, filename_suffix='_beh',
                                                  filename_extension='.xpd', run=i_string)
        wouldbe_eventfile = generate_bids_filename(subject_name, session, experiment_name, filename_suffix='_events',
                                                   filename_extension='.xpe', run=i_string)

    return wouldbe_datafile, wouldbe_eventfile


def logging_ttl_time_stamps_with_ttl_char_hotkeys(exp):
    #  You can place this function after exp is defined, and before control.initialize and control.start
    for ttl_char in ttl_characters:
        keyboard.add_hotkey(ttl_char, lambda: exp.add_experiment_info(
            'TTL_RECEIVED_timing-{}_method-{}'.format(exp.clock.time, "hotkey")))


def rest_function(exp, original_last_ttl_timestamp, block_index=None, pre_rest=False):
    if not pre_rest:
        number_ttl_to_wait = number_ttl_in_rest_period
        pre_rest_text = ''
    else:
        number_ttl_to_wait = number_ttl_before_rest_period
        pre_rest_text = '_preRest'

    if block_index is not None:
        block_string = f"_block_{block_index}"
    else:
        block_string = ""

    last_ttl_timestamp = original_last_ttl_timestamp
    exp.add_experiment_info(f'wait_{number_ttl_to_wait}_TTLs')
    exp.add_experiment_info(f'StartShortRest' + block_string + f'_timing_{exp.clock.time}{pre_rest_text}')
    for i in range(number_ttl_to_wait - 1):  # 1 TTL is already accounted for because of the next TTL
        last_ttl_timestamp = wait_for_ttl_keyboard_and_log_ttl(exp, last_ttl_timestamp)
    exp.add_experiment_info(f'EndShortRest' + block_string + f'_timing_{exp.clock.time}{pre_rest_text}')

    return last_ttl_timestamp


def load_mvpa_trials(subject_name, experienceName, mvpa_task_block_number=None):
    subject_dir = os.path.join(rawFolder, 'sourcedata', 'sub-' + subject_name)
    data_files = []
    for session in sessions:
        session_dir = os.path.join(subject_dir, 'ses-' + session, 'beh')
        if os.path.isdir(session_dir):
            data_files = data_files + \
                         [os.path.join(session_dir, file) for file in os.listdir(session_dir) if
                          file.endswith('_beh.xpd') and
                          'task-' + experienceName in file]

    data_files.sort(reverse=True)  # latest runs first
    for dataFile in data_files:
        try:
            agg = misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
        except TypeError:
            continue
        try:
            agg[3].index(experienceName)
        except ValueError:
            continue
        header = agg[3].split('\n#e ')
        index_subject_name = header.index('Subject:') + 1
        if subject_name not in header[index_subject_name]:
            continue

        # index_random_matrices = header.index('RandomMatrix') + 1
        # random_matrices = ast.literal_eval(header[index_random_matrices].split('\n')[0].split('\n')[0])
        presentation_order = header[header.index('PresentationOrder')+1:header.index('PresentationOrderEndOf')]
        presentation_order = ''.join(presentation_order)
        presentation_order = presentation_order.split('array')
        presentation_order = [element for element in presentation_order if len(element) > 2]
        for index in range(len(presentation_order)):
            presentation_order[index] = presentation_order[index].replace('(', '')
            presentation_order[index] = presentation_order[index].replace('),', '')
            presentation_order[index] = presentation_order[index].replace(')]', '')
            presentation_order[index] = presentation_order[index].replace(', dtype=object', '')
            presentation_order[index] = presentation_order[index].replace('\'', '"')
            presentation_order[index] = np.array(ast.literal_eval(presentation_order[index]), dtype=object)

        if mvpa_task_block_number is None:
            return presentation_order
        else:
            return [presentation_order[mvpa_task_block_number]]

    return None
