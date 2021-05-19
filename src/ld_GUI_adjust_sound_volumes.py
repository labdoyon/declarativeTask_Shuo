import sys
import pickle

from expyriment import control, misc, design, stimuli, io
from expyriment.misc import constants
from expyriment.misc._timer import get_time

from config import debug, windowMode, windowSize, classPictures, sounds, \
    bgColor, arrow, textSize, textColor, cardColor, responseTime, mouseButton, clickColor, clicPeriod
from ld_utils import getLanguage, setCursor, cardSize, readMouse
from ld_stimuli_names import soundNames, ttl_instructions_text
from ld_sound import change_volume, play_sound, delete_temp_files, dataFolder
from ttl_catch_keyboard import wait_for_ttl_keyboard
windowMode = True # TEST CODE
if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

if debug:
    control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=True)

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject
experimentName = arguments[0]
subject_name = arguments[1]

exp = design.Experiment(experimentName)  # Save experiment name
control.initialize(exp)
exp.add_experiment_info('Subject: ')
exp.add_experiment_info(subject_name)
language = str(getLanguage(subject_name, 0, 'choose-language'))
exp.add_experiment_info('language: ')
exp.add_experiment_info(language)  # Save Subject Code
exp.add_experiment_info('Image categories (original order; src/config.py order): ')
exp.add_experiment_info(str(classPictures))

# 0. Starting Experiment
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)
exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor
setCursor(arrow)
bs = stimuli.BlankScreen(bgColor)  # Create blank screen
soundsVolumeAdjustmentIndB = [0] * len(sounds)

# 1. PLOT INTERFACE

up_volume_box_contour = stimuli.Rectangle(size=(3*textSize, 3*textSize),
                                          position=(-2.5*cardSize[0], 0),
                                          colour=constants.C_WHITE)

up_volume_box = stimuli.Shape(position=(-2.5*cardSize[0], 0),
                              vertex_list=misc.geometry.vertices_cross((2*textSize, 2*textSize), textSize/2),
                              colour=textColor)

lower_volume_box_contour = stimuli.Rectangle(size=(3*textSize, 3*textSize),
                                             position=(2.5*cardSize[0], 0),
                                             colour=constants.C_WHITE)

lower_volume_box = stimuli.Shape(position=(2.5*cardSize[0], 0),
                                 vertex_list=[(2*textSize, 0), (0, -textSize/2), (-2*textSize, 0)],
                                 colour=textColor)

up_volume_box_contour.plot(bs)
lower_volume_box_contour.plot(bs)
up_volume_box.plot(bs)
lower_volume_box.plot(bs)
bs.present(False, True)

# 2. WAIT FOR TTL
instructions_ttl = stimuli.TextLine(ttl_instructions_text[language],
                                    position=(
                                        0, -windowSize[1] / float(2) + (cardSize[1]) / float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
instructionRectangle = stimuli.Rectangle(size=(windowSize[0], textSize),
                                         position=(0, -windowSize[1]/float(2) + (cardSize[1])/float(2)),
                                         colour=bgColor)
instructionRectangle.plot(bs)
instructions_ttl.plot(bs)
bs.present(False, True)
wait_for_ttl_keyboard()
exp.add_experiment_info(['TTL_RECEIVED_timing_{}'.format(exp.clock.time)])
instructionRectangle.plot(bs)
bs.present(False, True)

for sound_index in range(len(sounds)):
    sound_title_box = stimuli.TextLine(text=' ' + soundNames[language][sound_index] + ' ',
                                       position=(0, windowSize[1] / float(2) - cardSize[1]),
                                       text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                       text_underline=None, text_colour=textColor,
                                       background_colour=cardColor,
                                       max_width=None)
    sound_title_box_hide_rectangle = stimuli.Rectangle(size=(windowSize[0], textSize*1.2),
                                                       position=(0, windowSize[1] / float(2) - cardSize[1]),
                                                       colour=bgColor)
    if sound_index == len(sounds) - 1:
        next_sound_or_end_text = ' End '
    else:
        next_sound_or_end_text = ' Next Sound '
    next_sound_or_end_box = stimuli.TextLine(text=next_sound_or_end_text,
                                             position=(0, -windowSize[1] / float(2) + cardSize[1]),
                                             text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                             text_underline=None, text_colour=textColor,
                                             background_colour=cardColor,
                                             max_width=None)
    next_sound_or_end_box_hide_rectangle = stimuli.Rectangle(size=(windowSize[0], textSize*1.2),
                                                             position=(0, -windowSize[1] / float(2) + cardSize[1]),
                                                             colour=bgColor)
    sound_title_box_hide_rectangle.plot(bs)
    sound_title_box.plot(bs)
    next_sound_or_end_box_hide_rectangle.plot(bs)
    next_sound_or_end_box.plot(bs)
    bs.present(False, True)

    move_on = False
    while not move_on:
        mouse.show_cursor(True, True)
        start = get_time()
        rt, position = readMouse(start, mouseButton, responseTime)
        mouse.hide_cursor(True, True)
        if position is not None:
            if next_sound_or_end_box.overlapping_with_position(position):
                next_sound_or_end_box = stimuli.TextLine(text=next_sound_or_end_text,
                                                         position=(0, -windowSize[1] / float(2) + cardSize[1]),
                                                         text_font=None, text_size=textSize, text_bold=None,
                                                         text_italic=None,
                                                         text_underline=None, text_colour=textColor,
                                                         background_colour=clickColor,
                                                         max_width=None)
                next_sound_or_end_box.plot(bs)
                bs.present(False, True)
                exp.clock.wait(clicPeriod)
                next_sound_or_end_box = stimuli.TextLine(text=next_sound_or_end_text,
                                                         position=(0, -windowSize[1] / float(2) + cardSize[1]),
                                                         text_font=None, text_size=textSize, text_bold=None,
                                                         text_italic=None,
                                                         text_underline=None, text_colour=textColor,
                                                         background_colour=bgColor,
                                                         max_width=None)
                next_sound_or_end_box.plot(bs)
                bs.present(False, True)
                move_on = True
            elif lower_volume_box_contour.overlapping_with_position(position):
                soundsVolumeAdjustmentIndB[sound_index] -= 5
                change_volume(sound_index, volume_adjustment_db=soundsVolumeAdjustmentIndB[sound_index])
                play_sound(sound_index)
            elif up_volume_box_contour.overlapping_with_position(position):
                if soundsVolumeAdjustmentIndB[sound_index] + 5 <= 0:
                    soundsVolumeAdjustmentIndB[sound_index] += 5
                change_volume(sound_index, volume_adjustment_db=soundsVolumeAdjustmentIndB[sound_index])
                play_sound(sound_index)

# Saving sounds adjustment: (this script is supposed to be executed in src)
exp.add_experiment_info('Sounds Volume adjustment (in dB):')
exp.add_experiment_info(str(soundsVolumeAdjustmentIndB))
subject_file = 'soundsVolumeAdjustmentIndB_' + subject_name + '.pkl'
with open(dataFolder + subject_file, 'wb') as f:
    pickle.dump(soundsVolumeAdjustmentIndB, f)

control.end()
delete_temp_files()
