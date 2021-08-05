import os
import sys

from expyriment.misc import data_preprocessing

from ld_utils import Day, extract_matrix_and_data, extract_events, recognition_extract_events, write_csv, merge_csv, \
    delete_temp_csv
from ld_utils import learning_file_name

# ***INSTRUCTIONS***
# Please input the location of the subject folder containing the data you wish to convert to .csv format
# e.g. You are in DeCoNap/ and you wish to convert data located in DeCoNap/sourcedata/subject_41/
# Please input: python ld_analysis.py sourcedata/subject_41

# Output csv file will be created in the rawdata folder and will have the same name as the directory you
# specified
# In this example, Output will be:  <subject_41_preprocessed_data.csv> <DeCoNap/rawdata/subject_41_preprocessed_data.csv>

sep = os.path.sep
#
# Declaring <subject_folder> and <outputFile> variables, which are self-explanatory
subject_location = sys.argv[1]
input_location = 'sourcedata'

if subject_location[-1] == sep:  # removing path separator if not present. e.g. <data/> to <data>
    subject_location = subject_location[:-1]
if subject_location[:len(input_location + sep)] == (input_location + sep):
    output_location = 'rawdata' + sep + subject_location[len(input_location + sep):]
else:
    raise Exception("""Can't identify output location""")

subject_folder = os.getcwd() + sep + subject_location + sep

output_file_tests = os.getcwd() + sep + output_location + '_tests&recognition.csv'
output_file = os.getcwd() + sep + output_location + '_preprocessed_data.csv'

# Gathering all subject files
allFiles = os.listdir(subject_folder)
participant_files = []
for single_pt_file in allFiles:
    if 'EXCLUDED' not in single_pt_file and os.path.isfile(subject_location + sep + single_pt_file):
        if 'ld_recognition' in single_pt_file:
            participant_files.append(single_pt_file)
        elif 'ld_encoding' in single_pt_file:
            participant_files.append(single_pt_file)

day1_PreLearn = Day(learning=True)

day1_PreTest = Day()
day1_PreTest_not_reached = True
day2_PostTest1 = Day()
day2_PostTest1_not_reached = True
day2_PostRecog1 = Day(recognition=True)
day2_PostRecog1_not_reached = True
day2_PostTest2 = Day()
day2_PostTest2_not_reached = True
day2_PostRecog2 = Day(recognition=True)
day2_PostRecog2_not_reached = True
day2_PostLearn = Day(learning=True)
day2_PostLearn_not_reached = True

# for single_pt_file in allFiles:
for single_pt_file in participant_files:
    try:
        header = data_preprocessing.read_datafile(subject_folder + single_pt_file, only_header_and_variable_names=True)
    except TypeError:
        continue
    header[3].split('\n#e ')

    for field in header:
        if "PreLearn" in field and "Experiment" in field:
            events, matrix_pictures, local_matrix, matrix_size, classes_orders, day1_PreLearn.ttl_in_data =\
                extract_matrix_and_data(subject_folder, single_pt_file, learning=True)

            day1_PreLearn.cards_order, day1_PreLearn.cards_distance_to_correct_card,\
                day1_PreLearn.position_response_reaction_time,\
                day1_PreLearn.number_blocks, day1_PreLearn.show_card_absolute_time, \
                day1_PreLearn.hide_card_absolute_time,\
                day1_PreLearn.show_card_learning_absolute_time,\
                day1_PreLearn.hide_card_learning_absolute_time,\
                day1_PreLearn.cards_learning_order, \
                day1_PreLearn.cards_position, \
                day1_PreLearn.position_response_index_responded = \
                extract_events(events, matrix_size, ttl_timestamp=day1_PreLearn.ttl_in_data, mode='learning')

            output_file_learning_prelearn = learning_file_name(output_location, "PreLearn")

            write_csv(output_file_learning_prelearn, matrix_pictures, number_blocks=day1_PreLearn.number_blocks,
                      cards_order=day1_PreLearn.cards_order,
                      cards_distance_to_correct_card=day1_PreLearn.cards_distance_to_correct_card,
                      position_response_reaction_time=day1_PreLearn.position_response_reaction_time,
                      show_card_absolute_time=day1_PreLearn.show_card_absolute_time,
                      hide_card_absolute_time=day1_PreLearn.hide_card_absolute_time,
                      show_card_learning_absolute_time=day1_PreLearn.show_card_learning_absolute_time,
                      hide_card_learning_absolute_time=day1_PreLearn.hide_card_learning_absolute_time,
                      cards_learning_order=day1_PreLearn.cards_learning_order,
                      classes_order=classes_orders)

            break

        if "PreTest" in field and "Experiment" in field:
            day1_PreTest.events, day1_PreTest.matrix_pictures, day1_PreTest.local_matrix, day1_PreTest.matrix_size, \
                day1_PreTest.classes_order, day1_PreTest.ttl_in_data =\
                extract_matrix_and_data(subject_folder, single_pt_file)

            day1_PreTest.cards_order, day1_PreTest.cards_distance_to_correct_card,\
                day1_PreTest.position_response_reaction_time,\
                day1_PreTest.number_blocks, day1_PreTest.show_card_absolute_time, \
                day1_PreTest.hide_card_absolute_time,\
                day1_PreTest.cards_position, \
                day1_PreTest.position_response_index_responded =\
                extract_events(day1_PreTest.events, day1_PreTest.matrix_size)
            day1_PreTest_not_reached = False
            break

        if "PostTest1" in field and "Experiment" in field:
            day2_PostTest1.events, day2_PostTest1.matrix_pictures, day2_PostTest1.local_matrix,\
                day2_PostTest1.matrix_size, day2_PostTest1.classes_order, day2_PostTest1.ttl_in_data = \
                extract_matrix_and_data(subject_folder, single_pt_file)

            day2_PostTest1.cards_order, day2_PostTest1.cards_distance_to_correct_card,\
                day2_PostTest1.position_response_reaction_time,\
                day2_PostTest1.number_blocks, day2_PostTest1.show_card_absolute_time, \
                day2_PostTest1.hide_card_absolute_time,\
                day2_PostTest1.cards_position, day2_PostTest1.position_response_index_responded = \
                extract_events(day2_PostTest1.events, day2_PostTest1.matrix_size,
                               ttl_timestamp=day2_PostTest1.ttl_in_data)
            day2_PostTest1_not_reached = False
            break

        if "PostRecog1" in field and "Experiment" in field:
            day2_PostRecog1.events, day2_PostRecog1.matrix_pictures, day2_PostRecog1.local_matrix,\
                day2_PostRecog1.matrix_size, day2_PostRecog1.classes_order, day2_PostRecog1.ttl_in_data, \
                day2_PostRecog1.recognition_matrix, day2_PostRecog1.recognition_local_matrix,\
                day2_PostRecog1.matrix_a_or_rec, day2_PostRecog1.presentation_order =\
                extract_matrix_and_data(subject_folder, single_pt_file, recognition=True)

            day2_PostRecog1.cards_order, day2_PostRecog1.cards_answer, day2_PostRecog1.cards_reaction_time, \
                day2_PostRecog1.show_card_absolute_time, day2_PostRecog1.hide_card_absolute_time,\
                day2_PostRecog1.recognition_cards_order, day2_PostRecog1.recognition_answer,\
                day2_PostRecog1.recognition_cards_reaction_time,\
                day2_PostRecog1.show_recognition_card_absolute_time,\
                day2_PostRecog1.hide_recognition_card_absolute_time,\
                day2_PostRecog1.cards_distance_to_correct_card\
                = recognition_extract_events(day2_PostRecog1.events, day2_PostRecog1.matrix_pictures,
                                             day2_PostRecog1.local_matrix, day2_PostRecog1.recognition_matrix,
                                             day2_PostRecog1.recognition_local_matrix, day2_PostRecog1.matrix_a_or_rec,
                                             day2_PostRecog1.presentation_order,
                                             day2_PostRecog1.matrix_size, ttl_timestamp=day2_PostRecog1.ttl_in_data)
            day2_PostRecog1_not_reached = False
            break

        if "PostTest2" in field and "Experiment" in field:
            day2_PostTest2.events, day2_PostTest2.matrix_pictures, day2_PostTest2.matrix_size,\
                day2_PostTest2.local_matrix, day2_PostTest2.classes_order = \
                extract_matrix_and_data(subject_folder, single_pt_file)

            day2_PostTest2.cards_order, day2_PostTest2.cards_distance_to_correct_card, day2_PostTest2.position_response_reaction_time,\
                day2_PostTest2.number_blocks, day2_PostTest2.show_card_absolute_time, \
                day2_PostTest2.hide_card_absolute_time, day2_PostTest2.cards_position,\
                day2_PostTest2.position_response_index_responded = \
                extract_events(day2_PostTest2.events, day2_PostTest2.matrix_size, ttl_timestamp=day2_PostTest2.ttl_in_data)
            day2_PostTest2_not_reached = False
            break

        if "PostRecog2" in field and "Experiment" in field:
            day2_PostRecog2.events, day2_PostRecog2.matrix_pictures, day2_PostRecog2.local_matrix,\
                day2_PostRecog2.matrix_size, day2_PostRecog2.classes_order, day2_PostRecog2.recognition_matrix,\
                day2_PostRecog2.recognition_local_matrix,\
                day2_PostRecog2.matrix_a_or_rec, day2_PostRecog2.presentation_order =\
                extract_matrix_and_data(subject_folder, single_pt_file, recognition=True)

            day2_PostRecog2.cards_order, day2_PostRecog2.cards_answer, day2_PostRecog2.cards_reaction_time, \
                day2_PostRecog2.show_card_absolute_time, day2_PostRecog2.hide_card_absolute_time,\
                day2_PostRecog2.recognition_cards_order, day2_PostRecog2.recognition_answer,\
                day2_PostRecog2.recognition_cards_reaction_time,\
                day2_PostRecog2.show_recognition_card_absolute_time,\
                day2_PostRecog2.hide_recognition_card_absolute_time,\
                day2_PostRecog2.cards_distance_to_correct_card\
                = recognition_extract_events(day2_PostRecog2.events, day2_PostRecog2.matrix_pictures,
                                             day2_PostRecog2.local_matrix, day2_PostRecog2.recognition_matrix,
                                             day2_PostRecog2.recognition_local_matrix,
                                             day2_PostRecog2.matrix_size, ttl_timestamp=day2_PostRecog2.ttl_in_data)
            day2_PostRecog2_not_reached = False
            break
        if "PostLearn" in field and "Experiment" in field:
            day2_PostLearn.events, day2_PostLearn.matrix_pictures, day2_PostLearn.local_matrix,\
                day2_PostLearn.matrix_size, day2_PostLearn.classes_orders, day2_PostLearn.ttl_in_data =\
                extract_matrix_and_data(subject_folder, single_pt_file, learning=True)

            day2_PostLearn.cards_order, day2_PostLearn.cards_distance_to_correct_card,\
                day2_PostLearn.position_response_reaction_time,\
                day2_PostLearn.number_blocks, day2_PostLearn.show_card_absolute_time, \
                day2_PostLearn.hide_card_absolute_time,\
                day2_PostLearn.show_card_learning_absolute_time,\
                day2_PostLearn.hide_card_learning_absolute_time,\
                day2_PostLearn.cards_learning_order, \
                day2_PostLearn.cards_position, \
                day2_PostLearn.position_response_index_responded = \
                extract_events(day2_PostLearn.events, day2_PostLearn.matrix_size,
                               ttl_timestamp=day2_PostLearn.ttl_in_data, mode='learning')

            output_file_learning_postlearn = learning_file_name(output_location, "PostLearn")

            write_csv(output_file_learning_postlearn, day2_PostLearn.matrix_pictures, number_blocks=day2_PostLearn.number_blocks,
                      cards_order=day2_PostLearn.cards_order,
                      cards_distance_to_correct_card=day2_PostLearn.cards_distance_to_correct_card,
                      position_response_reaction_time=day2_PostLearn.position_response_reaction_time,
                      show_card_absolute_time=day2_PostLearn.show_card_absolute_time,
                      hide_card_absolute_time=day2_PostLearn.hide_card_absolute_time,
                      show_card_learning_absolute_time=day2_PostLearn.show_card_learning_absolute_time,
                      hide_card_learning_absolute_time=day2_PostLearn.hide_card_learning_absolute_time,
                      cards_learning_order=day2_PostLearn.cards_learning_order,
                      classes_order=day2_PostLearn.classes_orders)
            day2_PostLearn_not_reached = False
            break

write_csv(output_file_tests, matrix_pictures, days=[day1_PreTest, day2_PostTest1, day2_PostRecog1,
                                                    day2_PostTest2, day2_PostRecog2],
          days_not_reached=[day1_PreTest_not_reached, day2_PostTest1_not_reached, day2_PostRecog1_not_reached,
                            day2_PostTest2_not_reached, day2_PostRecog2_not_reached],
          classes_order=classes_orders)

temp_csv = [output_file_tests] + [output_file_learning_prelearn] + [output_file_learning_postlearn]

merge_csv(output_file, temp_csv)

# delete_temp_csv(temp_csv)

# as a rule of thumb, for 'DayRec_MatrixA_answer' and 'DayRec_matrixRec_answer', remember that
# 0 means "the subject made a mistake"
# 1 means "the subject got it right"
# 1 in 'DayRec_matrixRec_answer' means the subject clicked "Wrong" when presented with the wrong position. And 0, that
# they were mistaken
