import os
import sys
import numpy as np
from datetime import datetime
from dateutil.parser import parse

from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants

from ld_matrix import LdMatrix
from config import windowMode, windowSize, bgColor, textColor, cardSize, textSize, \
    classPictures, matrixSize, listPictures, shortRest, presentationCard, \
    dataFolder, picturesFolderClass, min_max_ISI, restPeriod
from ld_stimuli_names import pictureNames

# This script is part of declarative Task 3 and is meant to present and name all the stimulis used in the experiment
# in order to prepare the participant for all subsequent phases
# TODO bug: if participant name is contained within other participant's name (e.g. test and test2), test2 may get test's
# previous values
# TODO use config.py wherever possible
# TODO define functions in ld_utils.py, especially graphical functions
# TODO write all graphical interface
# TODO check all resting times
# TODO describe the whole process at the beginning of the script, presentation, waiting times
# TODO exp.add_experiment_info so all necessary informations are saved


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

# Save time, nblocks, position, correctAnswer, RT
exp.add_data_variable_names(['show_or_hide', 'Time', 'category', 'Picture', 'picture_name'])

# save image categories used for experiment
exp.add_experiment_info('Image categories (original order; src/config.py order): ')
exp.add_experiment_info(str(classPictures))

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
m.changeCueCardPosition((0, 0))

# start experiment
control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

# randomising presentation order of the categories
classPicturesPresentationOrder = list(np.random.permutation(classPictures))
exp.add_experiment_info('presentation order (Image categories): ')
exp.add_experiment_info(str(classPicturesPresentationOrder))

# Graphical instructions
bs = stimuli.BlankScreen(bgColor)  # Create blank screen

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], cardSize[1]), position=(
    0, -(cardSize[1])), colour=constants.C_DARKGREY)


def create_instructions_box(box_text):
    instructions_box = stimuli.TextLine(box_text,
                                        position=(0, -(cardSize[1])),  # -windowSize[1]/float(2) +
                                        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                        text_underline=None, text_colour=textColor,
                                        background_colour=bgColor,
                                        max_width=None)
    return instructions_box


def show_and_hide_text_box(background, instructions_box, onscreen_time, just_show=False, just_hide=False):
    if not just_hide:
        instructionRectangle.plot(background)
        instructions_box.plot(background)
        background.present(False, True)
        exp.clock.wait(onscreen_time)  # Short Rest between presentation and cue-recall
    if not just_show:
        instructionRectangle.plot(background)
        background.present(False, True)


exp.add_experiment_info('Presentation start')
instructions = create_instructions_box(' PRESENTATION: PRESENTING ALL STIMULIS ')
show_and_hide_text_box(bs, instructions, shortRest)

ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
exp.clock.wait(ISI)

# PRESENTATION
for category in classPicturesPresentationOrder:
    # pictures belonging to a category always start by the category's letter
    category_pictures = listPictures[category]
    # randomise pictures' presentation order
    category_pictures = np.random.permutation(category_pictures)

    exp.add_experiment_info(' PRESENTATION: PRESENTING CATEGORY ' + category)
    instructions = create_instructions_box(' PRESENTATION: PRESENTING CATEGORY ' + category.upper() + ' ')
    show_and_hide_text_box(bs, instructions, shortRest)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI)

    for picture in category_pictures:
        m._cueCard.setPicture(picturesFolderClass[category] + picture)  # Associate Picture to CueCard

        picture_name = picture.replace('.png', '')
        picture_title = pictureNames[language][picture_name]

        m.plotCueCard(True, bs, True)  # Show Cue
        instructions = create_instructions_box(picture_title)
        show_and_hide_text_box(bs, instructions, 0, just_show=True, just_hide=False)
        exp.add_experiment_info(
            'ShowCard_pos_{}_card_{}_name_{}_timing_{}'.format('None', picture, picture_title, exp.clock.time))
        exp.data.add(['show', exp.clock.time, category, picture, picture_title])
        exp.clock.wait(presentationCard)  # Wait presentationCard
        show_and_hide_text_box(bs, instructions, 0, just_show=False, just_hide=True)
        m.plotCueCard(False, bs, True)  # Hide Cue
        exp.add_experiment_info(
            'HideCard_pos_{}_card_{}_name_{}__timing_{}'.format('None', picture, picture_title, exp.clock.time))
        exp.data.add(['hide', exp.clock.time, category, picture, picture_title])

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI)

instructions = stimuli.TextLine(
    ' REST ',
    position=(0, -windowSize[1] / float(2) + (2 * m.gap + cardSize[1]) / float(2)),
    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
    text_underline=None, text_colour=textColor, background_colour=bgColor,
    max_width=None)

instructions.plot(bs)
bs.present(False, True)

exp.clock.wait(restPeriod)

instructionRectangle.plot(bs)
bs.present(False, True)

control.end()
