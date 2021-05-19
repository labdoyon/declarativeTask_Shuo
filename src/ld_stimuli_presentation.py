import sys
import numpy as np

from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants

from ld_matrix import LdMatrix
from config import windowMode, windowSize, bgColor, textColor, cardSize, textSize, \
    classPictures, matrixSize, listPictures, shortRest, presentationCard, picturesFolderClass,\
    min_max_ISI, debug, thankYouRest, sounds
from ld_stimuli_names import pictureNames, classNames, ending_screen_text, soundNames, ttl_instructions_text
from ld_stimuli_names import sound_textbox
from ld_utils import getLanguage, getPreviousSoundsAllocation
from ld_sound import create_temp_sound_files, delete_temp_files
from ttl_catch_keyboard import wait_for_ttl_keyboard

# This script is part of declarative Task 3 and is meant to present and name all the stimulis used in the experiment
# in order to prepare the participant for all subsequent phases
# TODO use config.py wherever possible
# TODO define functions in ld_utils.py, especially graphical functions
# TODO write all graphical interface
# TODO check all resting times
# TODO describe the whole process at the beginning of the script, presentation, waiting times
# TODO exp.add_experiment_info so all necessary informations are saved

if debug:
    control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=True)


# get experiment's name and subject's name from command line arguments
arguments = str(''.join(sys.argv[1:])).split(',')
experimentName = arguments[0]
subjectName = arguments[1]

# Create experiment
exp = design.Experiment(experimentName)  # Save experiment name
exp.add_experiment_info('Subject: ')
exp.add_experiment_info(subjectName)  # Save Subject Code
language = str(getLanguage(subjectName, 0, 'choose-language'))
exp.add_experiment_info('language: ')
exp.add_experiment_info(language)  # Save Subject Code

soundsAllocation_index = getPreviousSoundsAllocation(subjectName, 0, 'choose-sound-association')
soundsAllocation = {key: sounds[soundsAllocation_index[key]] for key in soundsAllocation_index.keys()}

# Save time, nblocks, position, correctAnswer, RT
exp.add_data_variable_names(['show_or_hide', 'Time', 'category', 'Picture', 'picture_name'])

# save image categories used for experiment
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

exp.add_experiment_info('pictures\'s list: ')
exp.add_experiment_info(str(listPictures))

# Check WindowMode and Resolution
if not windowMode:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

# TODO # this line (below) does too much, but it's okay for now.
m = LdMatrix(matrixSize, windowSize)
cuecard_index = int(len(classPictures)/2)
m.changeCueCardPosition((0, 0), cuecard_index)

# start experiment
control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

# randomising presentation order of the categories
classPicturesPresentationOrder = list(np.random.permutation(classPictures))
exp.add_experiment_info('presentation order (Image categories): ')
exp.add_experiment_info(str(classPicturesPresentationOrder))

# Graphical instructions
bs = stimuli.BlankScreen(bgColor)  # Create blank screen

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], 2*cardSize[1]), position=(
    0, -(2*cardSize[1])), colour=constants.C_DARKGREY)


def create_instructions_box(box_text, position):
    instructions_box = stimuli.TextBox(box_text,
                                       size=(windowSize[0], 2*cardSize[1]),
                                        position=position,  # -windowSize[1]/float(2) +
                                        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                        text_underline=None, text_colour=textColor,
                                        background_colour=bgColor)  # ,
                                        # max_width=None)
    return instructions_box


def show_and_hide_text_box(background, instructions_box, onscreen_time, just_show=False, just_hide=False):
    if not just_hide:
        instructionRectangle.plot(background)
        instructions_box.plot(background)
        background.present(False, True)
        exp.clock.wait(onscreen_time, process_control_events=True)  # Short Rest between presentation and cue-recall
    if not just_show:
        instructionRectangle.plot(background)
        background.present(False, True)


if language == 'french':
    instructions_presentation_text = """ PRÉSENTATION: 
     PRÉSENTATION DE TOUS LES STIMULIS """
    instructions_present1category_text = """ PRÉSENTATION:
    PRÉSENTATION DE LA CATÉGORIE: """
elif language == 'english':
    instructions_presentation_text = """ PRESENTATION:
     PRESENTING ALL STIMULIS """
    instructions_present1category_text = """ PRESENTATION: 
     PRESENTING CATEGORY """

instructions_ttl = create_instructions_box(ttl_instructions_text[language], (0, -(2*cardSize[1])))
show_and_hide_text_box(bs, instructions_ttl, 0, just_show=True)
wait_for_ttl_keyboard()
show_and_hide_text_box(bs, instructions_ttl, 0, just_hide=True)
exp.add_experiment_info(['TTL_RECEIVED_timing_{}'.format(exp.clock.time)])

ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
exp.clock.wait(ISI, process_control_events=True)

exp.add_experiment_info('Presentation start')
instructions_presentation = create_instructions_box(instructions_presentation_text, (0, -(2*cardSize[1])))
show_and_hide_text_box(bs, instructions_presentation, shortRest)

ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
exp.clock.wait(ISI, process_control_events=True)

# PRESENTATION
for category in classPicturesPresentationOrder:
    # pictures belonging to a category always start by the category's letter
    category_pictures = listPictures[category]
    # randomise pictures' presentation order
    category_pictures = np.random.permutation(category_pictures)

    soundIndex = soundsAllocation_index[category]
    sound = soundsAllocation[category]
    m.associateCategory(category)
    exp.add_experiment_info(' PRESENTATION: PRESENTING CATEGORY ' + classNames[language][category])
    instructions_present1category = create_instructions_box(
        instructions_present1category_text + classNames[language][category] + ' ',
        (0, -(2*cardSize[1])))
    show_and_hide_text_box(bs, instructions_present1category, shortRest)

    instructions_listen_sound = create_instructions_box(
        sound_textbox[language] + soundNames[language][soundIndex],
        (0, -(2*cardSize[1])))
    show_and_hide_text_box(bs, instructions_listen_sound, 0, just_show=True)
    m.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
    exp.clock.wait(presentationCard, process_control_events=True)
    exp.add_experiment_info(
        'PlayedSound_category_{}_timing_{}_soundIndex_{}_soundId_{}'.format(
            category, exp.clock.wait, soundIndex, sound, process_control_events=True), process_control_events=True)
    show_and_hide_text_box(bs, instructions_listen_sound, 0, just_hide=True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)

    for i, picture in enumerate(category_pictures):
        m._cueCard[cuecard_index].setPicture(picturesFolderClass[category] + picture)  # Associate Picture to CueCard

        picture_name = picture.replace('.png', '')
        picture_title = pictureNames[language][picture_name]

        m.plotCueCard(cuecard_index, True, bs, True)  # Show Cue
        title = create_instructions_box(picture_title,
                                        (0, -(2*cardSize[1])))
        show_and_hide_text_box(bs, title, 0, just_show=True, just_hide=False)
        exp.add_experiment_info(
            'ShowCard_pos_{}_card_{}_name_{}_timing_{}'.format('None', picture, picture_title, exp.clock.time))
        exp.data.add(['show', exp.clock.time, category, picture, picture_title])
        exp.clock.wait(presentationCard, process_control_events=True)  # Wait presentationCard
        show_and_hide_text_box(bs, title, 0, just_show=False, just_hide=True)
        m.plotCueCard(cuecard_index, False, bs, True)  # Hide Cue
        exp.add_experiment_info(
            'HideCard_pos_{}_card_{}_name_{}__timing_{}'.format('None', picture, picture_title, exp.clock.time))
        exp.data.add(['hide', exp.clock.time, category, picture, picture_title])

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI, process_control_events=True)

instructions_rest = create_instructions_box(ending_screen_text[language],
                                            (0, -windowSize[1] / float(2) + (2 * m.gap + cardSize[1]) / float(2)))
show_and_hide_text_box(bs, instructions_rest, thankYouRest)

control.end()
delete_temp_files()
