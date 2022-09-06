from cursesmenu import *
from cursesmenu.items import *
import sys
import os

from declarativeTask3.config import python, rawFolder
from declarativeTask3.ld_utils import getPrevious

subjectName = sys.argv[1]
subject_dir = os.path.normpath(os.path.join(rawFolder, 'sourcedata', 'sub-' + subjectName))
if not os.path.isdir(subject_dir):
    os.mkdir(subject_dir)

# DEBUGGING
# take a menu element (say Example, 'ses_D1_task_Example = CommandItem()')
# take the 'command' and 'arguments' element of the menu element
# e.g.
# command=python + " " + os.path.join("src", "declarativeTask3", "ld_example.py"),
#     arguments='ses-D1_task-Example,' + sys.argv[1]
#
# run the following in the command line
# py src\declarativeTask3\ld_example.py 'ses-D1_task-Example,<subject_id>'
# You will see any error the program generates much faster

language = getPrevious(subjectName, 0, 'choose-language', 'language:')
# 'None' if no languages were chosen previously, said language otherwise, e.g. 'french'

faces_places_choice = getPrevious(subjectName, 0, 'choose-faces-places', 'start_by_class1_or_class2:')
# 'None' if no choice was selected previously, said choice otherwise, e.g. 'start_with_faces'

# Create the menu
menu = CursesMenu(title="DeMo", subtitle='Subject: ' + sys.argv[1] + ' ; language: ' + str(language) +
                                         ' ; class1_or_class2: ' + str(faces_places_choice))

ChooseLanguage = CommandItem(
    text='choose language', command=python + " " + os.path.join("src", "declarativeTask3", "ld_choose_language.py"),
    arguments='ses-D1_task-choose-language, ' + sys.argv[1] + ', ' + 'None', menu=menu, should_exit=False)

ChooseFacesPlaces = CommandItem(
    text='choose: start by class1 or class2?',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_choose_faces_places.py"),
    arguments='ses-D1_task-choose-faces-places, ' + sys.argv[1] + ', ' + 'None', menu=menu, should_exit=False)

ses_D1_task_Example = CommandItem(
    text='ses-D1_task-Example', command=python + " " + os.path.join("src", "declarativeTask3", "ld_example.py"),
    arguments='ses-D1_task-Example,' + sys.argv[1], menu=menu, should_exit=False)

ses_D1_task_learnA = CommandItem(
    text='ses-D1_task-learnA',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='ses-D1_task-learnA, ' + sys.argv[1], menu=menu, should_exit=False)

ses_D1_task_PVT = CommandItem(
    text='ses-D1_task-PVT', command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
    arguments='ses-D1_task-PVT, ' + sys.argv[1], menu=menu, should_exit=False)

ses_D1_task_testA = CommandItem(
    text='ses-D1_task-testA',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='ses-D1_task-testA, ' + sys.argv[1], menu=menu, should_exit=False)

# ### SLEEP IN THE SCANNER ###

ses_Test_task_PVT = CommandItem(
    text='ses-Test_task-PVT', command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
    arguments='ses-Test_task-PVT, ' + sys.argv[1], menu=menu, should_exit=False)

ses_Test_task_testA = CommandItem(
    text='ses-Test_task-testA',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='ses-Test_task-testA, ' + sys.argv[1], menu=menu, should_exit=False)

ses_Test_task_recognition = CommandItem(
    text="ses-Test_task-recognition",
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_recognition.py"),
    arguments="ses-Test_task-recognition, " + sys.argv[1], menu=menu, should_exit=False)

# ### SLEEP IN THE LAB (no recording) ###

ses_D2_task_PVT1 = CommandItem(
    text='ses-D2_task-PVT1', command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
    arguments='ses-D2_task-PVT1, ' + sys.argv[1], menu=menu, should_exit=False)

ses_D2_task_testA = CommandItem(
    text='ses-D2_task-testA',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='ses-D2_task-testA, ' + sys.argv[1], menu=menu, should_exit=False)

ses_D2_task_learnB = CommandItem(
    text="ses-D2_task-learnB",
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments="ses-D2_task-learnB, " + sys.argv[1], menu=menu, should_exit=False)

ses_D2_task_PVT2 = CommandItem(
    text='ses-D2_task-PVT2', command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
    arguments='ses-D2_task-PVT2, ' + sys.argv[1], menu=menu, should_exit=False)

ses_D2_task_testB = CommandItem(
    text='ses-D2_task-testB',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='ses-D2_task-testB, ' + sys.argv[1], menu=menu, should_exit=False)

# ses_MVPA_task_testA = CommandItem(
#     text='ses-MVPA_task-testA', command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
#     arguments='ses-MVPA_task-testA, ' + sys.argv[1], menu=menu, should_exit=False)

ses_MVPA_task_generate_MVPA_trials = CommandItem(
    text="ses-MVPA_NOT-A-TASK-generate-mvpa-trials",
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_generate_mvpa_trials.py"),
    arguments="ses-MVPA_NOT-A-TASK-generate-mvpa-trials," + sys.argv[1], menu=menu, should_exit=False)

ses_MVPA_task_block_1 = CommandItem(
    text="ses-MVPA_task-block-1", command=python + " " + os.path.join("src", "declarativeTask3", "ld_recognition.py"),
    arguments="ses-MVPA_task-block-1, " + sys.argv[1], menu=menu, should_exit=False)

ses_MVPA_task_block_2 = CommandItem(
    text="ses-MVPA_task-block-2", command=python + " " + os.path.join("src", "declarativeTask3", "ld_recognition.py"),
    arguments="ses-MVPA_task-block-2, " + sys.argv[1], menu=menu, should_exit=False)

ses_MVPA_task_block_3 = CommandItem(
    text="ses-MVPA_task-block-3", command=python + " " + os.path.join("src", "declarativeTask3", "ld_recognition.py"),
    arguments="ses-MVPA_task-block-3, " + sys.argv[1], menu=menu, should_exit=False)

ses_MVPA_task_block_4 = CommandItem(
    text="ses-MVPA_task-block-4", command=python + " " + os.path.join("src", "declarativeTask3", "ld_recognition.py"),
    arguments="ses-MVPA_task-block-4, " + sys.argv[1], menu=menu, should_exit=False)

ses_MVPA_task_block_5 = CommandItem(
    text="ses-MVPA_task-block-5", command=python + " " + os.path.join("src", "declarativeTask3", "ld_recognition.py"),
    arguments="ses-MVPA_task-block-5, " + sys.argv[1], menu=menu, should_exit=False)

menu.append_item(ChooseLanguage)
menu.append_item(ChooseFacesPlaces)

# ###  EXPERIMENTAL NIGHT ###
# Set Up
# Rest
menu.append_item(ses_D1_task_Example)
menu.append_item(ses_D1_task_learnA)
# Rest
menu.append_item(ses_D1_task_PVT)  # PrePVT # The first PVT is _after_ learning, not before, correct?
menu.append_item(ses_D1_task_testA)  # Pretest# EEG SetUp Wear Cap
# ### SLEEP IN THE SCANNER ###
# Remove Cap
# Rest
menu.append_item(ses_Test_task_PVT)
menu.append_item(ses_Test_task_testA)
menu.append_item(ses_Test_task_recognition)

# ### SLEEP IN THE LAB (no recording) ###
# Set Up
# Rest
menu.append_item(ses_D2_task_PVT1)
menu.append_item(ses_D2_task_testA)
menu.append_item(ses_D2_task_learnB)
# Rest
menu.append_item(ses_D2_task_PVT2)
menu.append_item(ses_D2_task_testB)
# menu.append_item(ses_MVPA_task_testA)

menu.append_item(ses_MVPA_task_generate_MVPA_trials)
menu.append_item(ses_MVPA_task_block_1)
menu.append_item(ses_MVPA_task_block_2)
menu.append_item(ses_MVPA_task_block_3)
menu.append_item(ses_MVPA_task_block_4)
menu.append_item(ses_MVPA_task_block_5)

menu.show()
