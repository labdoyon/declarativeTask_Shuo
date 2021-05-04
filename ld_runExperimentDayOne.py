from cursesmenu import *
from cursesmenu.items import *
import sys
import os
import numpy as np
from ast import literal_eval

from datetime import datetime
import expyriment
from dateutil.parser import parse


rawFolder = os.getcwd() + os.path.sep
dataFolder = rawFolder + 'data' + os.path.sep
sounds = ['shortest-1-100ms.wav', 'shortest-2-100ms.wav', 'shortest-3-100ms.wav']
classPictures = ['a', 'b', 'c']
classNames = {'english': {'a': 'animals', 'b': 'household', 'c': 'clothes'},
              'french': {'a': 'animaux', 'b': 'maison', 'c': 'vêtements'},
              None: {'a': 'a', 'b': 'b', 'c': 'c'}}
soundNames = {
    None: {0: 'S1', 1: 'S2', 2: 'S3'},
    'english': {0: 'standard', 1: 'noise', 2: 'high pitch'},
    'french': {0: 'standard', 1: 'bruit', 2: 'aigu'}}


def getPrevious(subjectName, daysBefore, experienceName, target):
    currentDate = datetime.now()
    dataFiles = [file for file in os.listdir(dataFolder) if file.endswith('.xpd')]

    output = None

    for dataFile in dataFiles:
        agg = expyriment.misc.data_preprocessing.read_datafile(dataFolder + dataFile, only_header_and_variable_names=True)
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
                indexPositions = header.index(target) + 1
                previousTarget = header[indexPositions].split('\n')[0].split('\n')[0]
                try:  # dictionary or list
                    output = literal_eval(previousTarget)
                except:  # string
                    output = previousTarget

    # This ensures the latest language choice is used
    return output


def newSoundAllocation():
    # Random permutation to assign sounds to picture classes
    soundToClasses = {}
    soundToClasses_index = {}
    sounds_index = list(range(len(classPictures)))
    for category in classPictures:
        soundToClasses_index[category] = np.random.choice(sounds_index)
        soundToClasses[category] = sounds[soundToClasses_index[category]]
        sounds_index.remove(soundToClasses_index[category])

    return soundToClasses_index, soundToClasses


subjectName = sys.argv[1]
language = getPrevious(subjectName, 0, 'choose-language', 'language:')

soundsAllocation_index = getPrevious(subjectName, 0, 'choose-sound-association', 'Image classes to sounds (index):')
if soundsAllocation_index is None:
    soundsAllocation_index, soundsAllocation = newSoundAllocation()
    expyriment.control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=True)
    exp = expyriment.design.Experiment('choose-sound-association')  # Save experiment name
    exp.add_experiment_info('Subject: ')  # Save Subject Code
    exp.add_experiment_info(subjectName)
    exp.add_experiment_info('Image classes order:')
    exp.add_experiment_info(str(classPictures))
    exp.add_experiment_info('Sounds order:')
    exp.add_experiment_info(str(sounds))
    exp.add_experiment_info('Image classes to sounds:')
    exp.add_experiment_info(str(soundsAllocation))
    exp.add_experiment_info('Image classes to sounds (index):')
    exp.add_experiment_info(str(soundsAllocation_index))
    expyriment.control.initialize(exp)
    expyriment.control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)
    expyriment.control.end()

menu_soundsAllocation_index = {classNames[language][key]: soundNames[language][soundsAllocation_index[key]] for key in soundsAllocation_index.keys()}
# 'None' if no languages were chosen previously, said language otherwise, e.g. 'french'

python = 'py'

# Create the menu
menu = CursesMenu(
    title="Declarative Task - Day One", subtitle='Subject: ' + sys.argv[1] + ' ; language: ' +
                                                 str(language) +
                                                 ' ; Son-Cat: ' + str(menu_soundsAllocation_index).
                                                     replace('{', '').replace('}', ''))

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

dayOneStimuliPresentation = CommandItem(text='stimuli presentation',
                            command=python + " src" + os.path.sep + "ld_stimuli_presentation.py",
                            arguments='stimuli-presentation, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

soundVolumeAdjustment = CommandItem(text='sound Volume Adjustment',
                            command=python + " src" + os.path.sep + "ld_calibrateSoundVolumeSubprocess.py",
                            arguments=sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneAssociationLearning = CommandItem(text='Sound Category Association Learning',
                            command=python + " src" + os.path.sep + "ld_association_learning.py",
                            arguments='Association-Learning, ' + sys.argv[1],
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

dayOneReTestEncoding = CommandItem(text='ReTest Encoding',
                            command=python + " src" + os.path.sep + "ld_encoding.py",
                            arguments='ReTest-Encoding, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneRecognition = CommandItem(text="Recognition",
                                  command=python + " src" + os.path.sep + "ld_recognition.py ",
                                  arguments="Day One - Recognition, " + sys.argv[1],
                                  menu=menu,
                                  should_exit=False)

dayOneTestAssociationLearning = CommandItem(text='Test Sound Category Association Learning',
                            command=python + " src" + os.path.sep + "ld_association_learning.py",
                            arguments='Test-Association-Learning, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneConfig = CommandItem(text='Show config file',
                           command=python + " src" + os.path.sep + "ld_showConfigFile.py",
                           menu=menu,
                           should_exit=False)

menu.append_item(dayOneChooseLanguage)
menu.append_item(dayOneExample)
menu.append_item(soundVolumeAdjustment)
menu.append_item(dayOneStimuliPresentation)
menu.append_item(dayOneAssociationLearning)
menu.append_item(dayOneEncoding)
menu.append_item(dayOneTestEncoding)
menu.append_item(dayOneReTestEncoding)
menu.append_item(dayOneRecognition)
menu.append_item(dayOneTestAssociationLearning)
menu.append_item(dayOneConfig)

menu.show()
