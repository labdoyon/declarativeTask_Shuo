from cursesmenu import *
from cursesmenu.items import *
import sys
import os

from datetime import datetime
from expyriment import misc
from dateutil.parser import parse


rawFolder = os.getcwd() + os.path.sep
dataFolder = rawFolder + 'data' + os.path.sep


def getLanguage(subjectName, daysBefore, experienceName):
    currentDate = datetime.now()
    dataFiles = [file for file in os.listdir(dataFolder) if file.endswith('.xpd')]

    output = None

    for dataFile in dataFiles:
        agg = misc.data_preprocessing.read_datafile(dataFolder + dataFile, only_header_and_variable_names=True)
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

    # This ensures the latest language choice is used
    return output


subjectName = sys.argv[1]

language = str(getLanguage(subjectName, 0, 'choose-language'))
# 'None' if no languages were chosen previously, said language otherwise, e.g. 'french'

python = 'py'

# Create the menu
menu = CursesMenu(title="Declarative Task - Day One", subtitle='Subject: ' + sys.argv[1] + ' ; language: ' + language)

dayOneChooseLanguage = CommandItem(text='choose language',
                            command=python + " src" + os.path.sep + "ld_choose_language.py",
                            arguments='choose-language, ' + sys.argv[1] + ', ' + 'None',
                            menu=menu,
                            should_exit=False)

dayOneExample = CommandItem(text='Example',
                            command=python + " src" + os.path.sep + "ld_example.py",
                            arguments='Example, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneStimuliPresentation = CommandItem(text='stimulti presentation',
                            command=python + " src" + os.path.sep + "ld_stimuli_presentation.py",
                            arguments='stimuli-presentation, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

soundVolumeAdjustment = CommandItem(text='sound Volume Adjustment',
                            command=python + " src" + os.path.sep + "ld_calibrateSoundVolumeSubprocess.py",
                            arguments=sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneEncoding = CommandItem(text='Encoding',
                            command=python + " src" + os.path.sep + "ld_encoding.py",
                            arguments='Encoding, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneTestEncoding = CommandItem(text='Test Encoding',
                            command=python + " src" + os.path.sep + "ld_encoding.py",
                            arguments='Test-Encoding, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

# dayOnePreLearning = CommandItem(text="PreLearning",
#                                 command=python + " src" + os.path.sep + "ld_declarativeTask.py ",
#                                 arguments="DayOne-PreLearning, " + sys.argv[1],
#                                 menu=menu,
#                                 should_exit=False)

# dayOneLearning = CommandItem(text="Matrix A",
#                              command=python + " src" + os.path.sep + "ld_declarativeTask_relauncher.py ",
#                              arguments="DayOne-Learning, " + sys.argv[1],
#                              menu=menu,
#                              should_exit=False)

# dayOneTestMatrixA = CommandItem(text="Test Matrix A",
#                                 command=python + " src" + os.path.sep + "ld_declarativeTask.py ",
#                                 arguments="Day One - Test Learning, " + sys.argv[1],
#                                 menu=menu,
#                                 should_exit=False)

# dayOneConsolidationMatrixA = CommandItem(text="Consolidation Matrix A",
#                                 command=python + " src" + os.path.sep + "ld_declarativeTask.py ",
#                                 arguments="Day One - Test Consolidation, " + sys.argv[1],
#                                 menu=menu,
#                                 should_exit=False)

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

menu.append_item(dayOneChooseLanguage)
menu.append_item(dayOneExample)
menu.append_item(dayOneStimuliPresentation)
menu.append_item(dayOneEncoding)
menu.append_item(dayOneTestEncoding)
# menu.append_item(dayOnePreLearning)
menu.append_item(soundVolumeAdjustment)
# menu.append_item(dayOneLearning)
# menu.append_item(dayOneTestMatrixA)
# menu.append_item(dayOneConsolidationMatrixA)
menu.append_item(dayOneRecognition)
menu.append_item(dayOneAssociation)
menu.append_item(dayOneConfig)

menu.show()
