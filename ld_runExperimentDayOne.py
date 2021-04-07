from cursesmenu import *
from cursesmenu.items import *
import sys
import os

# '1': Example
# '2': Matrix A
# '3': Rest
# '4': Show Config

python = 'py'

# Create the menu
menu = CursesMenu("Declarative Task - Day One", 'Subject: ' + sys.argv[1])

dayOneExample = CommandItem(text='Example',
                            command=python + " src" + os.path.sep + "ld_example.py",
                            arguments='Example, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneStimuliPresentation = CommandItem(text='stimulti presentation',
                            command=python + " src" + os.path.sep + "ld_stimuli_presentation.py",
                            arguments='stimulti-presentation, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

soundVolumeAdjustment = CommandItem(text='sound Volume Adjustment',
                            command=python + " src" + os.path.sep + "ld_calibrateSoundVolumeSubprocess.py",
                            arguments=sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOnePreLearning = CommandItem(text="PreLearning",
                                command=python + " src" + os.path.sep + "ld_declarativeTask.py ",
                                arguments="DayOne-PreLearning, " + sys.argv[1],
                                menu=menu,
                                should_exit=False)

dayOneLearning = CommandItem(text="Matrix A",
                             command=python + " src" + os.path.sep + "ld_declarativeTask_relauncher.py ",
                             arguments="DayOne-Learning, " + sys.argv[1],
                             menu=menu,
                             should_exit=False)

dayOneTestMatrixA = CommandItem(text="Test Matrix A",
                                command=python + " src" + os.path.sep + "ld_declarativeTask.py ",
                                arguments="Day One - Test Learning, " + sys.argv[1],
                                menu=menu,
                                should_exit=False)

dayOneConsolidationMatrixA = CommandItem(text="Consolidation Matrix A",
                                command=python + " src" + os.path.sep + "ld_declarativeTask.py ",
                                arguments="Day One - Test Consolidation, " + sys.argv[1],
                                menu=menu,
                                should_exit=False)

dayOneRecognition = CommandItem(text="Recognition",
                                  command=python + " src" + os.path.sep + "ld_recognition.py ",
                                  arguments="Day One - Recognition, " + sys.argv[1],
                                  menu=menu,
                                  should_exit=False)

dayOneAssociation = CommandItem(text="Association",
                                  command=python + " src" + os.path.sep + "ld_association.py ",
                                  arguments="DayOne-Association, " + sys.argv[1],
                                  menu=menu,
                                  should_exit=False)

dayOneConfig = CommandItem(text='Show config file',
                           command=python + " src" + os.path.sep + "ld_showConfigFile.py",
                           menu=menu,
                           should_exit=False)

menu.append_item(dayOneExample)
menu.append_item(dayOneStimuliPresentation)
menu.append_item(dayOnePreLearning)
menu.append_item(soundVolumeAdjustment)
menu.append_item(dayOneLearning)
menu.append_item(dayOneTestMatrixA)
menu.append_item(dayOneConsolidationMatrixA)
menu.append_item(dayOneRecognition)
menu.append_item(dayOneAssociation)
menu.append_item(dayOneConfig)

menu.show()
