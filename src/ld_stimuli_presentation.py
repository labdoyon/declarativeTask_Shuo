import sys
import os
import glob
import numpy as np

from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants

from ld_matrix import LdMatrix
from config import windowMode, windowSize, bgColor, textColor, cardSize, textSize, \
    classPictures, matrixSize, classPicture, shortRest, presentationCard, \
    picturesFolder
from ld_stimuli_names import pictureNames, language

# This script is part of declarative Task 3 and is meant to present and name all the stimulis used in the experiment
# in order to prepare the participant for all subsequent phases
# TODO use config.py wherever possible
# TODO define functions in ld_utils.py, especially graphical functions
# TODO write all graphical interface
# TODO check all resting times
# TODO describe the whole process at the beginning of the script, presentation, waiting times
# TODO exp.add_experiment_info so all necessary informations are saved

# get experiment's name and subject's name from command line arguments
arguments = str(''.join(sys.argv[1:])).split(',')
experimentName = arguments[0]
subjectName = arguments[1]

# Create experiment
exp = design.Experiment(experimentName)  # Save experiment name
exp.add_experiment_info('Subject: ')
exp.add_experiment_info(subjectName)  # Save Subject Code

# save image categories used for experiment
exp.add_experiment_info('Image categories (original order; src/config.py order): ' + str(classPictures))

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

# start experiment
control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

# randomising presentation order of the categories
classPicturesPresentationOrder = list(np.random.permutation(classPictures))
exp.add_experiment_info('presentation order (Image categories): ' + str(classPicturesPresentationOrder))

# Graphical instructions
bs = stimuli.BlankScreen(bgColor)  # Create blank screen

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], m.gap * 2 + cardSize[1]), position=(
    0, -windowSize[1]/float(2) + (2 * m.gap + cardSize[1])/float(2)), colour=constants.C_DARKGREY)

instructions = stimuli.TextLine(' PRESENTATION: PRESENTING ALL STIMULIS ',
                                position=(0, -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                text_underline=None, text_colour=textColor,
                                background_colour=bgColor,
                                max_width=None)

instructionRectangle.plot(bs)
instructions.plot(bs)
bs.present(False, True)

exp.clock.wait(shortRest)  # Short Rest between presentation and cue-recall

instructionRectangle.plot(bs)
bs.present(False, True)

# PRESENTATION
for category in classPicturesPresentationOrder:
    # pictures belonging to a category always start by the category's letter
    # TODO use config.py moving forward instead of copy pasting config.py 's expressions
    category_pictures = glob.glob(picturesFolder + category + '*[0-9][0-9][0-9].png')
    # randomise pictures' presentation order
    category_pictures = np.random.permutation(category_pictures)

    instructionRectangle.plot(bs)
    instructions.plot(bs)
    bs.present(False, True)

    exp.clock.wait(shortRest)  # Short Rest between presentation and cue-recall

    instructionRectangle.plot(bs)
    bs.present(False, True)

    for picture_fullpath in category_pictures:
        m._cueCard.setPicture(picture_fullpath)  # Associate Picture to CueCard
        picture_filename = os.path.basename(picture_fullpath)
        picture_name = picture_filename.replace('.png', '')
        picture_title = pictureNames[language][picture_name]

        m.plotCueCard(True, bs, True)  # Show Cue
        exp.clock.wait(presentationCard)  # Wait presentationCard
        m.plotCueCard(False, bs, True)  # Hide Cue

        exp.clock.wait(shortRest)

control.end()
