from cursesmenu import *
from cursesmenu.items import *
import sys
import os
import glob
import numpy as np
from ast import literal_eval

from datetime import datetime
import expyriment
from dateutil.parser import parse

from declarativeTask3.config import rawFolder, sessions
from declarativeTask3.ld_utils import getPrevious

subjectName = sys.argv[1]
subject_dir = os.path.normpath(os.path.join(rawFolder, 'sourcedata', 'sub-' + subjectName))
if not os.path.isdir(subject_dir):
    os.mkdir(subject_dir)

language = getPrevious(subjectName, 0, 'choose-language', 'language:')
# 'None' if no languages were chosen previously, said language otherwise, e.g. 'french'

faces_places_choice = getPrevious(subjectName, 0, 'choose-faces-places', 'start_by_class1_or_class2:')
# 'None' if no choice was selected previously, said choice otherwise, e.g. 'start_with_faces'

python = 'python'

# Create the menu
menu = CursesMenu(
    title="DECOPM", subtitle='Subject: ' + sys.argv[1] + ' ; language: ' + str(language) +
                             ' ; class1_or_class2: ' + str(faces_places_choice))
print(python + " " + os.path.join("src", "declarativeTask3", "ld_choose_language.py"))
dayOneChooseLanguage = CommandItem(text='choose language',
                                   command=python + " " + os.path.join("src", "declarativeTask3", "ld_choose_language.py"),
                                   arguments='choose-language, ' + sys.argv[1] + ', ' + 'None', menu=menu,
                                   should_exit=True)

dayOneChooseFacesPlaces = CommandItem(text='choose: start by class1 or class2?',
                                      command=python + " " + os.path.join("src", "declarativeTask3", "ld_choose_faces_places.py"),
                                      arguments='choose-faces-places, ' + sys.argv[1] + ', ' + 'None', menu=menu,
                                      should_exit=False)

dayOneExample = CommandItem(text='Example',
                            command=python + " " + os.path.join("src", "declarativeTask3", "ld_example.py"),
                            arguments='Example,' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

# dayOneStimuliPresentation = CommandItem(text='stimuli presentation',
#                             command=python + " " + os.path.join("src", "declarativeTask3", "ld_stimuli_presentation.py"),
#                             arguments='stimuli-presentation, ' + sys.argv[1],
#                             menu=menu,
#                             should_exit=False)

dayOnePrePVT = CommandItem(text='4. PrePVT',
                           command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
                           arguments='PrePVT, ' + sys.argv[1],
                           menu=menu,
                           should_exit=False)

dayOnePreLearn = CommandItem(text='2. PreLearn',
                             command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
                             arguments='PreLearn, ' + sys.argv[1],
                             menu=menu,
                             should_exit=False)

dayOnePreTest = CommandItem(text='5. PreTest',
                                 command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
                                 arguments='PreTest, ' + sys.argv[1],
                                 menu=menu,
                                 should_exit=False)

dayOnePostPVT1 = CommandItem(text='7. PostPVT1',
                             command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
                             arguments='PostPVT1, ' + sys.argv[1],
                             menu=menu,
                             should_exit=False)

dayOnePostTest1 = CommandItem(text='8. PostTest1',
                                   command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
                                   arguments='PostTest1, ' + sys.argv[1],
                                   menu=menu,
                                   should_exit=False)

dayOnePostRecog1 = CommandItem(text="9. PostRecog1",
                                command=python + " " + os.path.join("src", "declarativeTask3", "ld_recognition.py"),
                                arguments="PostRecog1, " + sys.argv[1],
                                menu=menu,
                                should_exit=False)

dayOnePostPVT2 = CommandItem(text='7. PostPVT2',
                             command=python + " " + os.path.join("src", "declarativeTask3", "ld_pvt.py"),
                             arguments='PostPVT2, ' + sys.argv[1],
                             menu=menu,
                             should_exit=False)

dayOnePostTest2 = CommandItem(text='12. PostTest2',
                                   command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
                                   arguments='PostTest2, ' + sys.argv[1],
                                   menu=menu,
                                   should_exit=False)

dayOnePostRecog2 = CommandItem(text="13. PostRecog2",
                                command=python + " " + os.path.join("src", "declarativeTask3", "ld_recognition.py"),
                                arguments="PostRecog2, " + sys.argv[1],
                                menu=menu,
                                should_exit=False)

dayOnePostLearn = CommandItem(text="14. PostLearn",
                                command=python + " " + os.path.join("src", "declarativeTask3", "ld_encoding.py"),
                                arguments="PostLearn, " + sys.argv[1],
                                menu=menu,
                                should_exit=False)

dayOneMVPA = CommandItem(text="15. MVPA",
                                command=python + " " + os.path.join("src", "declarativeTask3", "ld_mvpa.py"),
                                arguments="MVPA, " + sys.argv[1],
                                menu=menu,
                                should_exit=False)

menu.append_item(dayOneChooseLanguage)
menu.append_item(dayOneChooseFacesPlaces)
menu.append_item(dayOneExample)
# menu.append_item(dayOneStimuliPresentation)
menu.append_item(dayOnePrePVT)
menu.append_item(dayOnePreLearn)
menu.append_item(dayOnePreTest)
menu.append_item(dayOnePostPVT1)
menu.append_item(dayOnePostTest1)
menu.append_item(dayOnePostRecog1)
menu.append_item(dayOnePostPVT2)
menu.append_item(dayOnePostTest2)
menu.append_item(dayOnePostRecog2)
menu.append_item(dayOnePostLearn)
menu.append_item(dayOneMVPA)

menu.show()
