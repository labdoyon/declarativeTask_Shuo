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

language = getPrevious(subjectName, 0, 'choose-language', 'language:')
# 'None' if no languages were chosen previously, said language otherwise, e.g. 'french'

faces_places_choice = getPrevious(subjectName, 0, 'choose-faces-places', 'start_by_class1_or_class2:')
# 'None' if no choice was selected previously, said choice otherwise, e.g. 'start_with_faces'

# Create the menu
menu = CursesMenu(title="DeMo", subtitle='Subject: ' + sys.argv[1] + ' ; language: ' + str(language) +
                                         ' ; class1_or_class2: ' + str(faces_places_choice))

ChooseLanguage = CommandItem(
    text='choose language', command=python + " " + os.path.join("src", "declarativeTask3", "ld_choose_language.py"),
    arguments='choose-language, ' + sys.argv[1] + ', ' + 'None', menu=menu, should_exit=False)

ChooseFacesPlaces = CommandItem(
    text='choose: start by class1 or class2?',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_choose_faces_places.py"),
    arguments='choose-faces-places, ' + sys.argv[1] + ', ' + 'None', menu=menu, should_exit=False)

ses_ExpD1__task_Example = CommandItem(
    text='ses-ExpD1_task-Example', command=python + " " + os.path.join("src", "declarativeTask3", "ld_example.py"),
    arguments='Example,' + sys.argv[1], menu=menu, should_exit=False)

ses_ExpD1__task_Learn_1stClass = CommandItem(
    text='ses-ExpD1_task-Learn-1stClass',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='PreLearn, ' + sys.argv[1], menu=menu, should_exit=False)

ses_ExpD1__task_PVT = CommandItem(
    text='ses-ExpD1_task-PVT', command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
    arguments='PrePVT, ' + sys.argv[1], menu=menu, should_exit=False)

ses_ExpD1__task_Test_1stClass = CommandItem(
    text='ses-ExpD1_task-Test-1stClass',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='PreTest, ' + sys.argv[1], menu=menu, should_exit=False)

# ### SLEEP IN THE SCANNER ###

ses_ExpTest__task_PVT = CommandItem(
    text='ses-ExpTest_task-PVT', command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
    arguments='PostPVT1, ' + sys.argv[1], menu=menu, should_exit=False)

ses_ExpTest__task_Test_1stClass = CommandItem(
    text='ses-ExpTest_task-Test-1stClass',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='PostTest1, ' + sys.argv[1], menu=menu, should_exit=False)

ses_ExpTest__task_Recognition = CommandItem(
    text="ses-ExpTest_task-Recognition",
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_recognition.py"),
    arguments="Recognition, " + sys.argv[1], menu=menu, should_exit=False)

# ### SLEEP IN THE LAB (no recording) ###

ses_ExpD2__task_PVT = CommandItem(
    text='ses-ExpD2_task-PVT', command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
    arguments='PostPVT2, ' + sys.argv[1], menu=menu, should_exit=False)

ses_ExpD2__task_Test_1stClass = CommandItem(
    text='ses-ExpD2_task-Test-1stClass',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='PostTest2, ' + sys.argv[1], menu=menu, should_exit=False)

ses_ExpD2__task_Learn_2ndClass = CommandItem(
    text="ses-ExpD2_task-Learn-2ndClass",
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments="PostLearn, " + sys.argv[1], menu=menu, should_exit=False)

ses_ExpMVPA__task_PVT = CommandItem(
    text='ses-ExpMVPA_task-PVT', command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
    arguments='PostPVT3, ' + sys.argv[1], menu=menu, should_exit=False)

ses_ExpMVPA__task_Test_2ndClass = CommandItem(
    text='ses-ExpMVPA_task-Test-2ndClass',
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='Test-2ndClassLearned, ' + sys.argv[1], menu=menu, should_exit=False)

ses_ExpMVPA__task_Test_1stClass = CommandItem(
    text='PostTest3', command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
    arguments='PostTest3, ' + sys.argv[1], menu=menu, should_exit=False)

ses_ExpMVPA__task_generate_MVPA_trials = CommandItem(
    text="generate MVPA trials",
    command=python + " " + os.path.join("src", "declarativeTask3", "ld_generate_mvpa_trials.py"),
    arguments="generate_mvpa_trials," + sys.argv[1], menu=menu, should_exit=False)

ses_ExpMVPA__task_MVPA = CommandItem(
    text="MVPA", command=python + " " + os.path.join("src", "declarativeTask3", "ld_recognition.py"),
    arguments="MVPA, " + sys.argv[1], menu=menu, should_exit=False)

menu.append_item(ChooseLanguage)
menu.append_item(ChooseFacesPlaces)

# ###  EXPERIMENTAL NIGHT ###
# Set Up
# Rest
menu.append_item(ses_ExpD1__task_Example)
menu.append_item(ses_ExpD1__task_Learn_1stClass)
# Rest
menu.append_item(ses_ExpD1__task_PVT)  # PrePVT # The first PVT is _after_ learning, not before, correct?
menu.append_item(ses_ExpD1__task_Test_1stClass)  # PreTest# EEG SetUp Wear Cap
# ### SLEEP IN THE SCANNER ###
# Remove Cap
# Rest
menu.append_item(ses_ExpTest__task_PVT)
menu.append_item(ses_ExpTest__task_Test_1stClass)
menu.append_item(ses_ExpTest__task_Recognition)

# ### SLEEP IN THE LAB (no recording) ###
# Set Up
# Rest
menu.append_item(ses_ExpD2__task_PVT)
menu.append_item(ses_ExpD2__task_Test_1stClass)
menu.append_item(ses_ExpD2__task_Learn_2ndClass)
# Rest
menu.append_item(ses_ExpMVPA__task_PVT)
menu.append_item(ses_ExpMVPA__task_Test_2ndClass)
menu.append_item(ses_ExpMVPA__task_Test_1stClass)

menu.append_item(ses_ExpMVPA__task_generate_MVPA_trials)
menu.append_item(ses_ExpMVPA__task_MVPA)

menu.show()
