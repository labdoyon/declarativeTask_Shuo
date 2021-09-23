import os
import csv
from math import floor

import numpy as np
import ast
import re
from scipy.spatial import distance
from expyriment.misc import data_preprocessing
from xpd_to_tsv_config import removeCards, matrixSize, matrixTemplate, classPictures, presentationCard


dont_suppress_card_double_checking = True

first_columns = ['Item', 'Class', 'MatrixA_X_coord', 'MatrixA_Y_coord']

test_recall_suffixes = ['matrixA_order', 'matrixA_distanceToMatrixA', 'matrixA_X_clicked', 'matrixA_Y_clicked',
                        'matrixA_ReactionTime', 'matrixA_ShowTime', 'matrixA_HideTime']

test_recognition_suffixes = \
    ['matrixA_order', 'matrixA_answer', 'matrixA_ReactionTime', 'matrixA_ShowTime', 'matrixA_HideTime',
     'matrixR_order', 'matrixR_answer', 'matrixR_ReactionTime', 'matrixR_ShowTime', 'matrixR_HideTime',
     'matrixR_distanceToMatrixA']

learning_suffixes = ['matrixA_order', 'matrixA_distanceToMatrixA', 'matrixA_X_clicked', 'matrixA_Y_clicked',
                     'matrixA_ReactionTime', 'matrixA_ShowTime', 'matrixA_HideTime',
                     'matrixA_learning_order', 'matrixA_LearningShowTime', 'matrixA_LearningHideTime']


class CorrectCards(object):
    def __init__(self):
        self.answer = []
        self.position = []
        self.picture = []


class WrongCards(object):
    def __init__(self):
        self.answer = []
        self.position = []
        self.picture = []


class Day(object):
    def __init__(self, recognition=False, learning=False):
        self.matrix = []
        self.header = []
        self.matrix_pictures = []
        self.number_blocks = 0
        self.matrix_size = ()
        self.events = []
        self.classes_order = []
        self.sounds_order = []
        self.classes_to_sounds = []
        self.ttl_in_data = None
        self.position_response_reaction_time = []
        self.hide_card_absolute_time = []
        self.show_card_absolute_time = []

        self.cards_order = {}
        if not recognition and not learning:
            self.recognition = False
            self.cards_distance_to_correct_card = []
            self.position_response_index_responded = []
            self.cards_order = []
            self.cards_position = []
            self.position_response_index_responded = []
        elif learning and not recognition:
            self.recognition = False
            self.show_card_learning_absolute_time = []
            self.hide_card_learning_absolute_time = []
            self.cards_learning_order = []
            self.cards_distance_to_correct_card = []
            self.cards_order = []
            self.cards_position = []
            self.position_response_index_responded = []
            self.position_response_reaction_time = []
        elif recognition and not learning:
            self.recognition = True
            self.cards_answer = {}
            self.recognition_cards_order = {}
            self.recognition_answer = {}
            self.recognition_cards_reaction_time = {}
            self.show_recognition_card_absolute_time = {}
            self.hide_recognition_card_absolute_time = {}
            self.recognition_matrix = []


def matrix_index_to_xy_coordinates(matrix_index):
    # this function takes the matrix_index of an image (integer from 0 to 48 in case of a 7-by-7 matrix) and returns
    # the X and Y coord of the image in the matrix
    # (X=1, Y=1) being the top left corner of the matrix, and (X=7, Y=7) being the bottom right corner of the matrix
    # the matrix is populated in columns: as in, matrix_index 0 to 6 are positions (1,1), (1,2), (1,3) ... (1,7),
    # matrix_index 7 to 13 are positions (2,1), (2,2), (2,3) ... (2,6) in (X,Y) coordinates, and so on
    # we add +1 so X and Y are indexed from 1 and not from 0
    matrix_x_coord, matrix_y_coord = divmod(int(matrix_index), matrixSize[1])
    return matrix_x_coord+1, matrix_y_coord+1


def learning_file_name(output_location, suffix):
    return os.getcwd() + os.path.sep + output_location + '_learning_' + suffix +'.csv'


def extract_matrix_and_data(i_file, recognition=False, learning=False):
    header = data_preprocessing.read_datafile(i_file, only_header_and_variable_names=True)

    # Extracting pictures' positions in the matrix
    header2 = header[3].split('\n#e ')
    find_xpd_file_eval = lambda content, title: ast.literal_eval(
        content[content.index(title) + 1].split('\n')[0].split('\n')[0])
    find_xpd_file = lambda content, title: content[content.index(title) + 1]
    for string in header2:
        if 'TTL_RECEIVED_timing_' in string:
            ttl_event = string
            break
    ttl_timestamp = int(re.search('timing_([0-9]+)', ttl_event).group(1))
    try:  # Earlier version of the program
        faces_or_places = find_xpd_file(header2, 'faces_or_places_for_this_experiment:')
    except:
        faces_or_places = find_xpd_file(header2, 'start_by_class1_or_class2:')

    local_matrix_position = faces_or_places + '_only_matrix:'
    if not recognition:
        matrix_position = 'Positions pictures:'
        recognition_matrix = False
    else:
        matrix_position = 'Learning:'
        random_matrix_position = 'RandomMatrix:'
        local_random_matrix_position = faces_or_places + '_only_random_matrix:'
        recognition_matrix = find_xpd_file_eval(header2, random_matrix_position)
        recognition_matrix = [element.rstrip('.png') if element is not None else None for element in recognition_matrix]
        recognition_local_matrix = find_xpd_file_eval(header2, local_random_matrix_position)
        recognition_local_matrix = [element.rstrip('.png') if element is not None else None for element in recognition_local_matrix]

        # recognition_matrix = ast.literal_eval(
        #     header2[header2.index(random_matrix_position) + 1].split('\n')[0].split('\n')[0])
        # recognition_matrix = [element.rstrip('.png') if element is not None else None for element in recognition_matrix]
        cards_order = header2[header2.index('Presentation Order:')+1:header2.index('Presentation Order:')+7]
        cards_order = ''.join(cards_order)
        non_decimal = re.compile(r'[^\d.]+')
        cards_order = non_decimal.sub('', cards_order)
        cards_order = cards_order.split('.')
        cards_order = [int(x) for x in cards_order[0:-1]]
        matrix_rec_or_a = cards_order[int(len(cards_order)/2):]
        presentation_order = cards_order[:int(len(cards_order)/2)]

    # matrix_pictures = ast.literal_eval(
    #     header2[header2.index(matrix_position) + 1].split('\n')[0].split('\n')[0])
    matrix_pictures = find_xpd_file_eval(header2, matrix_position)
    matrix_pictures = [element.rstrip('.png') if element is not None else None for element in matrix_pictures]
    local_matrix = find_xpd_file_eval(header2, local_matrix_position)
    local_matrix = [element.rstrip('.png') if element is not None else None for element in local_matrix]

    classes_order_position = 'Image classes order:'
    classes_order = find_xpd_file_eval(header2, classes_order_position)

    # Extracting data
    events = header[-1].split('\n')
    events = [element.encode('ascii') for element in events]
    events = [event.decode('utf-8') for event in events]

    if len(matrix_pictures) == 48:
        matrix_size = (7, 7)
    elif len(matrix_pictures) == 36:
        matrix_size = (6, 6)
    elif len(matrix_pictures) == 24:
        matrix_size = (5, 5)
    else:
        raise ValueError('Matrix dimensions cannot be identified')

    if recognition:
        return events, matrix_pictures, local_matrix, matrix_size, \
               classes_order, ttl_timestamp, \
               recognition_matrix, recognition_local_matrix, matrix_rec_or_a, presentation_order
    else:
        return events, matrix_pictures, local_matrix, matrix_size, classes_order, ttl_timestamp


def extract_events(events, matrix_size, ttl_timestamp=None, mode=None):
    if ttl_timestamp is None:
        print("WARNING: no events file found, no ttl found")

    cards_position = []  # the position of the card in the matrix
    cards_distance_to_correct_card = []  # the distance between the card clicked and the correct answer (0 if correct)
    cards_order = []  # the order of presentation of the card in the test phase
    position_response_reaction_time = []  # the reaction time of the subject when presented with this card in the test phase
    show_card_absolute_time = []
    hide_card_absolute_time = []
    position_response_x_responded = []
    position_response_y_responded = []
    if mode == 'learning':
        show_card_learning_absolute_time = []
        hide_card_learning_absolute_time = []
        cards_learning_order = []

    for event in events:
        if 'Block' in event and 'Test' in event:
            # we add a dictionary for
            cards_position.append({})
            cards_distance_to_correct_card.append({})
            cards_order.append({})
            position_response_reaction_time.append({})
            hide_card_absolute_time.append({})
            show_card_absolute_time.append({})
            position_response_x_responded.append({})
            position_response_y_responded.append({})
            block_number = len(cards_position) - 1
            register_on = True
            # we start collecting the answers
            order = 0  # we start a 0, first card/image presented during the test
        elif 'Block' in event and 'StartPresentation' in event:
            register_on = False
            try:
                del hidden_card; del card; del position
            except UnboundLocalError:
                pass
            show_card_learning_absolute_time.append({})
            hide_card_learning_absolute_time.append({})
            cards_learning_order.append({})
            learning_block_number = len(cards_learning_order) - 1
            learning_order = 0
        if 'ShowCard' in event and not register_on:
            card = re.search('(?<=card_)\w+', event).group(0)
            show_time = int(re.search('timing_([0-9]+)', event).group(1))
            if ttl_timestamp is not None:
                show_card_learning_absolute_time[learning_block_number][card] = show_time - ttl_timestamp
            else:
                show_card_learning_absolute_time[learning_block_number][card] = show_time
            cards_learning_order[learning_block_number][card] = learning_order
            learning_order += 1
        if 'HideCard' in event and not register_on:
            hidden_card = re.search('(?<=card_)\w+', event).group(0)
            hide_time = int(re.search('timing_([0-9]+)', event).group(1))
            if ttl_timestamp is not None:
                hide_card_learning_absolute_time[learning_block_number][hidden_card] = hide_time - ttl_timestamp
            else:
                hide_card_learning_absolute_time[learning_block_number][hidden_card] = hide_time
        elif 'ShowCueCard' in event and register_on:
            card = re.search('(?<=card_)\w+', event).group(0)
            position = cards_position[block_number][card] = re.search('pos_([0-9]+)_', event).group(1)
            if ttl_timestamp is not None:
                show_card_absolute_time[block_number][card] = int(re.search('timing_([0-9]+)', event).group(1)) - \
                    ttl_timestamp
            else:
                show_card_absolute_time[block_number][card] = int(re.search('timing_([0-9]+)', event).group(1))
            cards_order[block_number][card] = order
            order += 1
            cards_distance_to_correct_card[block_number][card] = 'NaN'
        elif 'HideCueCard' in event and register_on:
            hidden_card = re.search('(?<=card_)\w+', event).group(0)
            hide_card_time = reaction_start = int(re.search('timing_([0-9]+)', event).group(1))
            if ttl_timestamp is not None:
                hide_card_absolute_time[block_number][hidden_card] = hide_card_time - ttl_timestamp
            else:
                hide_card_absolute_time[block_number][hidden_card] = int(re.search('timing_([0-9]+)', event).group(1))
        elif ('NoResponse' in event or 'pos_None_ERROR' in event) and register_on:
            position_response_reaction_time[block_number][card] = 'noResponse'
            cards_distance_to_correct_card[block_number][card] = 'noResponse'
            position_response_x_responded[block_number][card] = 'noResponse'
            position_response_y_responded[block_number][card] = 'noResponse'
        elif 'Response' in event and 'NoResponse' not in event and 'pos_None_ERROR' not in event and register_on:
            response = re.search('(?<=card_)\w+', event).group(0)
            response_time = int(re.search('timing_([0-9]+)', event).group(1))
            position_response_reaction_time[block_number][card] = response_time - reaction_start

            response_position = re.search('pos_([0-9]+)_', event).group(1)
            position_response_x_responded[block_number][card], position_response_y_responded[block_number][card] = \
                matrix_index_to_xy_coordinates(response_position)
            if response == card:
                cards_distance_to_correct_card[block_number][card] = 0
            else:
                cards_distance_to_correct_card[block_number][card] = distance.euclidean(
                    np.unravel_index(int(position), matrix_size),
                    np.unravel_index(int(response_position), matrix_size))

    if mode == 'learning':
        return cards_order, cards_distance_to_correct_card, position_response_reaction_time, block_number + 1, \
               show_card_absolute_time, hide_card_absolute_time, show_card_learning_absolute_time, \
               hide_card_learning_absolute_time, cards_learning_order, cards_position, \
               position_response_x_responded, position_response_y_responded
    else:
        return cards_order, cards_distance_to_correct_card, position_response_reaction_time, block_number + 1, \
            show_card_absolute_time, hide_card_absolute_time, cards_position, position_response_x_responded, \
            position_response_y_responded


def recognition_extract_events(events, matrix_pictures, local_matrix, recognition_matrix, local_recognition_matrix,
                               matrix_rec_or_a, presentation_order,
                               matrix_size, ttl_timestamp=None):
    experiment_started = 0
    counter = 0
    cards = np.sort(local_matrix)
    recognition_distance_matrix_a = {}
    recognition_cards_order = {}
    cards_order = {}
    # taking into account the center where there is no card:
    if len(removeCards) == 1 and removeCards[0] == int(floor(matrixSize[0]*matrixSize[1]/2)):
        for i in range(len(presentation_order)):
            if presentation_order[i] > removeCards[0]:
                presentation_order[i] = presentation_order[i] - 1
    for i in range(len(cards)*2):
        if matrix_rec_or_a[i]:
            recognition_cards_order[recognition_matrix[presentation_order[i]]] = i
        else:
            cards_order[matrix_pictures[presentation_order[i]]] = i

    # Assigning cards_order
    # cards_order = [presentation_order[i] for i in range(len(presentation_order)) if matrix_rec_or_a[i]]
    # cards_order = {cards_no_none[i]: cards_order[i] for i in range(len(cards_order))}
    # Assigning recognition_cards_order
    # recognition_cards_order = [presentation_order[i] for i in range(len(presentation_order)) if not matrix_rec_or_a[i]]
    # recognition_cards_order = {cards_no_none[i]: recognition_cards_order[i] for i in range(len(recognition_cards_order))}

    cards_position = {}
    recognition_cards_position = {}
    cards_answer = {}
    recognition_answer = {}
    cards_reaction_time = {}
    # cards_absolute_time = {}
    hide_card_absolute_time = {}
    show_card_absolute_time = {}
    recognition_cards_reaction_time = {}
    # recognition_cards_absolute_time = {}
    hide_recognition_card_absolute_time = {}
    show_recognition_card_absolute_time = {}
    for event in events:
        if experiment_started:
            if 'ShowCard' in event:
                card = re.search('(?<=card_)\w+', event).group(0)
                card = card.rstrip('.png')
                card_position = re.search('pos_([0-9]+)_', event).group(1)

                # Checking if there was no response in the last card
                expected_card = recognition_matrix[presentation_order[counter]] if matrix_rec_or_a[counter]\
                    else matrix_pictures[presentation_order[counter]]
                if card != expected_card:
                    if matrix_rec_or_a[counter]:
                        recognition_answer[last_card] = 'noResponse'
                        recognition_cards_reaction_time[last_card] = 'noResponse'
                    else:
                        cards_answer[last_card] = 'noResponse'
                        cards_reaction_time[last_card] = 'noResponse'
                    counter += 1
                if ttl_timestamp is None:
                    if matrix_rec_or_a[counter]:
                        show_recognition_card_absolute_time[card] = int(re.search('timing_([0-9]+)', event).group(1))
                    else:

                        show_card_absolute_time[card] = int(re.search('timing_([0-9]+)', event).group(1))
                else:
                    if matrix_rec_or_a[counter]:
                        show_recognition_card_absolute_time[card] = \
                            int(re.search('timing_([0-9]+)', event).group(1)) - ttl_timestamp
                    else:
                        show_card_absolute_time[card] = \
                            int(re.search('timing_([0-9]+)', event).group(1)) - ttl_timestamp

                if matrix_rec_or_a[counter]:
                    recognition_cards_position[card] = card_position
                else:
                    cards_position[card] = card_position

                last_card = card
            if 'HideCard' in event:
                hidden_card = re.search('(?<=card_)\w+', event).group(0)
                hidden_card_position = re.search('pos_([0-9]+)_', event).group(1)
                reaction_start = int(re.search('timing_([0-9]+)', event).group(1))
                if ttl_timestamp is None:
                    if matrix_rec_or_a[counter]:
                        hide_recognition_card_absolute_time[hidden_card] = int(re.search('timing_([0-9]+)', event).group(1))
                    else:
                        hide_card_absolute_time[hidden_card] = int(re.search('timing_([0-9]+)', event).group(1))
                else:
                    if matrix_rec_or_a[counter]:
                        hide_recognition_card_absolute_time[hidden_card] = \
                            int(re.search('timing_([0-9]+)', event).group(1)) - ttl_timestamp
                    else:
                        hide_card_absolute_time[hidden_card] = \
                            int(re.search('timing_([0-9]+)', event).group(1)) - ttl_timestamp
                if dont_suppress_card_double_checking and\
                        (hidden_card != card or hidden_card_position != card_position):
                    raise Exception("""It seems a card was not hidden after being shown. Something may be wrong with
                    the .xpd files you're using as input. You may skip this double-checking by changing
                    `dont_suppress_card_double_checking` to `False` in ld_utils.py if you know what you're doing""")
            if 'Response_NoRT' in event:
                if matrix_rec_or_a[counter]:
                    recognition_answer[card] = 'noResponse'
                    recognition_cards_reaction_time[card] = 'noResponse'
                elif not matrix_rec_or_a[counter]:
                    cards_answer[card] = 'noResponse'
                    cards_reaction_time[card] = 'noResponse'
            if 'Response' in event and 'Response_NoRT' not in event:
                # response = re.search('(?<=Response_)\w+', event).group(0)
                response = re.search('Response_([a-zA-Z]+)_', event).group(1)
                response_time = int(re.search('timing_([0-9]+)', event).group(1))
                # matrix_rec_or_a[counter] == 1 means a recognition picture was shown
                # matrix_rec_or_a[counter] == 0 means a matrixA picture was shown
                if not matrix_rec_or_a[counter] and response == 'MatrixA':
                    cards_answer[card] = 1
                    cards_reaction_time[card] = response_time - reaction_start
                elif not matrix_rec_or_a[counter] and response == 'None':
                    cards_answer[card] = 0
                    cards_reaction_time[card] = response_time - reaction_start
                elif matrix_rec_or_a[counter] and response == 'None':
                    recognition_answer[card] = 1
                    recognition_cards_reaction_time[card] = response_time - reaction_start
                elif matrix_rec_or_a[counter] and response == 'MatrixA':
                    recognition_answer[card] = 0
                    recognition_cards_reaction_time[card] = response_time - reaction_start
                counter += 1
        if 'StartExp' in event:
            experiment_started = 1

    # Edge case: If there is no response at the very last card in the presentation:
    try:
        test = recognition_answer[card]
        test = recognition_cards_reaction_time[card]
    except KeyError:
        recognition_answer[card] = 'noResponse'
        recognition_cards_reaction_time[card] = 'noResponse'
    try:
        test = cards_answer[card]
        test = cards_reaction_time[card]
    except KeyError:
        cards_answer[card] = 'noResponse'
        cards_reaction_time[card] = 'noResponse'
    # (END OF) Edge case: If there is no response at the very last card in the presentation:

    for card in cards:
        recognition_distance_matrix_a[card] = distance.euclidean(
            np.unravel_index(int(cards_position[card]), matrix_size),
            np.unravel_index(int(recognition_cards_position[card]), matrix_size))
    return cards_order, cards_answer, cards_reaction_time, show_card_absolute_time, hide_card_absolute_time,\
        recognition_cards_order, recognition_answer, recognition_cards_reaction_time,\
        show_recognition_card_absolute_time, hide_recognition_card_absolute_time, recognition_distance_matrix_a


def write_csv(output_file, matrix_pictures,
              classes_order=None,
              days=None, number_blocks=0,
              cards_order=None, cards_distance_to_correct_card=None, position_response_reaction_time=None,
              show_card_absolute_time=None,
              hide_card_absolute_time=None,
              cards_learning_order=None,
              show_card_learning_absolute_time=None,
              hide_card_learning_absolute_time=None,
              position_response_x_responded=None,
              position_response_y_responded=None,
              days_not_reached=[False]*5):

    if days is None:
        days = []
    i_csv = csv.writer(open(output_file, "w", newline=''))

    first_row = list(first_columns)
    if not days:
        block_range = range(number_blocks)
        for i in block_range:
            first_row.extend(
                ['Learning_Block' + str(i) + '_' + element for element in learning_suffixes])
    else:
        preTest_recall_titles = ['PreTest_Recall_' + item for item in test_recall_suffixes]
        postTest1_recall_titles = ['PostTest1_Recall_' + item for item in test_recall_suffixes]
        PostRecog1_recall_titles = ['PostRecog1_' + item for item in test_recognition_suffixes]
        postTest2_recall_titles = ['PostTest2_Recall_' + item for item in test_recall_suffixes]
        PostRecog2_recall_titles = ['PostRecog2_' + item for item in test_recognition_suffixes]
        first_row.extend(preTest_recall_titles + postTest1_recall_titles + PostRecog1_recall_titles +
                         postTest2_recall_titles + PostRecog2_recall_titles)
    i_csv.writerow(first_row)
    if not days:
        write_csv_learning(i_csv, matrix_pictures, cards_order, cards_distance_to_correct_card, position_response_reaction_time,
                           show_card_absolute_time, hide_card_absolute_time, number_blocks,
                           cards_learning_order, show_card_learning_absolute_time, hide_card_learning_absolute_time,
                           position_response_x_responded, position_response_y_responded,
                           classes_order=classes_order)
    else:
        write_csv_test(i_csv, matrix_pictures, classes_order, days, days_not_reached)


def write_csv_learning(i_csv, matrix_pictures, cards_order, cards_distance_to_correct_card, position_response_reaction_time,
                       show_card_absolute_time, hide_card_absolute_time, number_blocks,
                       cards_learning_order, show_card_learning_absolute_time, hide_card_learning_absolute_time,
                       position_response_x_responded, position_response_y_responded,
                       classes_order=None):
    cards = [card for card in np.sort(matrix_pictures) if card is not None]
    for card in cards:
        # Add item; Add category
        card = card.rstrip('.png')
        card_class = card[:2]
        card_index = matrix_pictures.index(card)

        if card_index > min(removeCards):
            removeCards_sorted = sorted(removeCards)
            for remove_card in removeCards_sorted:
                if card_index > remove_card:
                    card_index += 1

        card_x_coord, card_y_coord = matrix_index_to_xy_coordinates(card_index)
        item_list = [card, card_class, card_x_coord, card_y_coord]
        # add answers and card orders
        for block_number in range(number_blocks):
            try:
                item_list.extend([
                    cards_order[block_number][card], cards_distance_to_correct_card[block_number][card],
                    position_response_x_responded[block_number][card],
                    position_response_y_responded[block_number][card],
                    position_response_reaction_time[block_number][card], show_card_absolute_time[block_number][card],
                    hide_card_absolute_time[block_number][card],

                    cards_learning_order[block_number][card], show_card_learning_absolute_time[block_number][card],
                    hide_card_learning_absolute_time[block_number][card]
                     ])
            except KeyError:
                item_list.extend(['script_failed_extract_data']*len(learning_suffixes))
        i_csv.writerow(item_list)


def write_csv_test(i_csv, matrix_pictures, classes_order, days, days_not_reached):
    cards = [card for card in np.sort(matrix_pictures) if card is not None]
    for card in cards:
        # Add item; Add category
        try:
            card = card.rstrip('.png')
        except AttributeError:
            pass
        card_class = card[:2]
        position = matrix_pictures.index(card)
        item_list = [card, card_class, position]
        for i in range(len(days)):
            day = days[i]
            if days_not_reached[i]:
                if not day.recognition:
                    item_list.extend(['noFile']*len(test_recall_suffixes))
                else:
                    item_list.extend(['noFile']*len(test_recognition_suffixes))
            else:
                try:
                    if not day.recognition:
                        item_list.extend([day.cards_order[0][card], day.cards_distance_to_correct_card[0][card],
                                          day.position_response_x_responded[0][card],
                                          day.position_response_y_responded[0][card],
                                          day.position_response_reaction_time[0][card], day.show_card_absolute_time[0][card],
                                          day.hide_card_absolute_time[0][card]])
                    else:
                        item_list.extend([day.cards_order[card], day.cards_answer[card],
                                          day.cards_reaction_time[card], day.show_card_absolute_time[card],
                                          day.hide_card_absolute_time[card],

                                          day.recognition_cards_order[card], day.recognition_answer[card],
                                          day.recognition_cards_reaction_time[card],
                                          day.show_recognition_card_absolute_time[card],
                                          day.hide_recognition_card_absolute_time[card],
                                          day.cards_distance_to_correct_card[card]])
                except KeyError:
                    if not day.recognition:
                        item_list.extend(['script_failed_extract_data']*len(test_recall_suffixes))
                    else:
                        item_list.extend(['script_failed_extract_data']*len(test_recognition_suffixes))

        i_csv.writerow(item_list)


def extract_correct_answers(i_folder, i_file):
    agg = data_preprocessing.Aggregator(data_folder=i_folder, file_name=i_file)
    header = data_preprocessing.read_datafile(i_folder + i_file, only_header_and_variable_names=True)

    # Extracting pictures' positions in the matrix
    header = header[3].split('\n#e ')
    matrix_pictures = ast.literal_eval(header[header.index('Positions pictures:') + 1].split('\n')[0].split('\n')[0])
    matrix_pictures = [element for element in matrix_pictures if element is not None]

    # Extracting data
    data = {}
    for variable in agg.variables:
        data[variable] = agg.get_variable_data(variable)

    block_indexes = np.unique(data['NBlock'])
    for block in block_indexes:
        correct_answers = np.logical_and(data['Picture'] == data['Answers'], data['NBlock'] == block)
        wrong_answers = np.logical_and(data['Picture'] != data['Answers'], data['NBlock'] == block)

    # list(set(my_list)) is one of the smoothest way to eliminate duplicates
    classes = list(set([element[0] for element in matrix_pictures if element is not None]))
    classes = list(np.sort(classes))  # Order the classes

    valid_cards = CorrectCards()
    invalid_cards = WrongCards()
    for idx, val in enumerate(correct_answers):
        if val:
            valid_cards.answer.append(data['Answers'][idx][0])
            valid_cards.position.append(matrix_pictures.index(data['Answers'][idx]))

    for idx, val in enumerate(wrong_answers):
        if val:
            invalid_cards.answer.append(data['Answers'][idx][0])
            invalid_cards.picture.append(data['Picture'][idx][0])
            if 'None' in data['Answers'][idx][0]:
                invalid_cards.position.append(100)
            else:
                invalid_cards.position.append(matrix_pictures.index(data['Answers'][idx]))

    for idx, val in enumerate(wrong_answers):
        if val:
            invalid_cards.answer.append(data['Answers'][idx][0])
            invalid_cards.picture.append(data['Picture'][idx][0])
            if 'None' in data['Answers'][idx][0]:
                invalid_cards.position.append(100)
            else:
                invalid_cards.position.append(matrix_pictures.index(data['Answers'][idx]))

    for element in classes:
        valid_cards.element = [word for word in valid_cards.answer if word[0] == element]
        invalid_cards.element = [word for word in invalid_cards.picture if word[0] == element]

    return matrix_pictures, data, valid_cards, invalid_cards, len(block_indexes)


def merge_csv(output_file, csv_list):
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        rows = {k: [] for k in range(1+len(matrixTemplate))}
        for i, fname in enumerate(csv_list):
            try:
                with open(fname, 'r', newline='') as infile:
                    reader = csv.reader(infile)
                    for j, row in enumerate(reader):
                        if i == 0:
                            rows[j] += row
                        else:
                            rows[j] += row[len(first_columns):]
            except IOError:
                pass
        for j in range(len(rows)):
            writer.writerow(rows[j])


def delete_temp_csv(temp_csv):
    for temp_file in temp_csv:
        try:
            os.remove(temp_file)
        except IOError:
            pass
        except WindowsError:
            pass
