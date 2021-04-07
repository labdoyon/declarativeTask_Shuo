import sys

import numpy as np
from expyriment import control, stimuli, io, design, misc
from expyriment.misc._timer import get_time

from ld_matrix import LdMatrix
from ld_utils import setCursor, getPreviousMatrix, newRandomPresentation, readMouse, getPreviousSoundsAllocation
from ttl_catch_keyboard import wait_for_ttl_keyboard
from config import *

from ld_sound import create_temp_sound_files, delete_temp_files, play_sound

if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

# FUNCTION DEFINITION ##################################################################################################


def sound_x_box(sound_number, box_position, display, display_text, show_hide_click=None):
    if sound_number not in [1, 2, 3]:
        print(str(sound_number) + 'should be 1 or 2 or 3')
    if type(box_position) != tuple or len(box_position) != 2:
        if type(box_position[0]) != str or type(box_position[1]) != str:
            print('position should be a tuple containing two numbers')
    if type(display) != bool:
        print('display should be a boolean')
    if show_hide_click is None:
        choose_sound_x = stimuli.TextBox(display_text + str(sound_number),
                                         size=(2 * cardSize[0], 1 * cardSize[1]),
                                         position=box_position,
                                         # text_font=None,
                                         text_size=textSize,
                                         text_colour=textColor,
                                         background_colour=cardColor)
    else:
        choose_sound_x = stimuli.TextBox(display_text + str(sound_number),
                                         size=(2 * cardSize[0], 1 * cardSize[1]),
                                         position=box_position,
                                         text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                         text_underline=None, text_colour=textColor,
                                         background_colour=clickColor)

    choose_sound_x_box = stimuli.Rectangle(size=choose_sound_x.surface_size,
                                           position=choose_sound_x.position,
                                           colour=cardColor)

    return choose_sound_x, choose_sound_x_box


# Overriding src/config.py setting
textSize = 30
m = LdMatrix(matrixSize, windowSize)  # Create Matrix

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject

experimentName = arguments[0]
subjectName = arguments[1]

exp = design.Experiment(experimentName)  # Save experiment name
exp.add_experiment_info('Subject: ')  # Save Subject Code
exp.add_experiment_info([subjectName])  # Save Subject Code

# Save time, Response, boolAnswer, RT
exp.add_data_variable_names(['Time', 'Picture', 'boolAnswer', 'sound', 'RT'])

exp.add_experiment_info('Learning Matrix: ')  # Save Subject Code
learningMatrix = getPreviousMatrix(subjectName, 0, 'DayOne-Learning')
exp.add_experiment_info(str(learningMatrix))  # Add listPictures

exp.add_experiment_info('Image classes order:')
exp.add_experiment_info(str(classPictures))
exp.add_experiment_info('Sounds order:')
exp.add_experiment_info(str(sounds))

soundsAllocation = getPreviousSoundsAllocation(subjectName, 0, 'DayOne-Learning')
exp.add_experiment_info('Image classes to sounds:')
exp.add_experiment_info(str(soundsAllocation))

soundsVolumeAdjustmentIndB = create_temp_sound_files(subjectName)
exp.add_experiment_info('Sounds Volume adjustment (in dB):')
exp.add_experiment_info(str(soundsVolumeAdjustmentIndB))
if soundsVolumeAdjustmentIndB != [0, 0, 0]:
    volumeAdjusted = True
else:
    volumeAdjusted = False

m.associateSounds(learningMatrix, soundsAllocation)

exp.add_experiment_info('Presentation Order: ')  # Save Presentation Order

presentationOrder = newRandomPresentation()

listCards = []
for nCard in range(len(presentationOrder)):
    if removeCards:
        removeCards.sort()
        removeCards = np.asarray(removeCards)
        tempPosition = presentationOrder[nCard]
        index = 0
        try:
            index = int(np.where(removeCards == max(removeCards[removeCards < tempPosition]))[0]) + 1
        except:
            pass

        position = tempPosition - index

    else:
        position = presentationOrder[0][nCard]

    listCards.append(learningMatrix[int(position)])

exp.add_experiment_info(str(list(presentationOrder)))  # Add listPictures

control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

# LOG and SYNC
exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

setCursor(arrow)

# CHOOSE SOUND BOXES
choose_text = """Choose
Sound """
choose_sound1_position = (-windowSize[0]/float(3), -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2))
choose_sound2_position = (0, -windowSize[1] / float(2) + (2 * m.gap + cardSize[1]) / float(2))
choose_sound3_position = (windowSize[0] / float(3), -windowSize[1] / float(2) + (2 * m.gap + cardSize[1]) / float(2))

choose_sound1, choose_sound1_box = sound_x_box(1, choose_sound1_position, True, choose_text)
choose_sound2, choose_sound2_box = sound_x_box(2, choose_sound2_position, True, choose_text)
choose_sound3, choose_sound3_box = sound_x_box(3, choose_sound3_position, True, choose_text)

# PLAY SOUND BOXES
play_text = """Play
Sound """
play_sound1_position = (-windowSize[0] / float(3), windowSize[1] / float(2) - (2 * m.gap + cardSize[1]) / float(2))
play_sound2_position = (0, windowSize[1] / float(2) - (2 * m.gap + cardSize[1]) / float(2))
play_sound3_position = (windowSize[0] / float(3), windowSize[1] / float(2) - (2 * m.gap + cardSize[1]) / float(2))

play_sound1, play_sound1_box = sound_x_box(1, play_sound1_position, True, play_text)

play_sound2, play_sound2_box = sound_x_box(2, play_sound2_position, True, play_text)

play_sound3, play_sound3_box = sound_x_box(3, play_sound3_position, True, play_text)

bs = stimuli.BlankScreen(bgColor)  # Create blank screen
bs = m.plotDefault(bs)  # Draw default grid
choose_sound1_box.plot(bs)
choose_sound1.plot(bs)
choose_sound2.plot(bs)
choose_sound3.plot(bs)
play_sound1.plot(bs)
play_sound2.plot(bs)
play_sound3.plot(bs)
m._cueCard.color = bgColor
# bs = m.plotCueCard(False, bs)

bs.present(False, True)

wait_for_ttl_keyboard()
exp.add_experiment_info(['TTL_RECEIVED_timing_{}'.format(exp.clock.time)])


for nCard in range(len(presentationOrder)):
    locationCard = int(presentationOrder[nCard])

    m._matrix.item(locationCard).setPicture(picturesXFolder + 'X.png')
    picture = listCards[nCard].rstrip(".png")
    m.plotCard(locationCard, True, bs, True)

    exp.add_experiment_info(['ShowCard_pos_{}_card_{}_timing_{}'.format(locationCard,
                                                                        listCards[nCard],
                                                                        exp.clock.time)])  # Add sync info

    exp.clock.wait(presentationCard)
    m.plotCard(locationCard, False, bs, True)
    exp.add_experiment_info(['HideCard_pos_{}_card_{}_timing_{}'.format(locationCard,
                                                                        listCards[nCard],
                                                                        exp.clock.time)])  # Add sync info

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI)

    time_left = rt = AssociationResponseTime
    boolAnswer = None
    while boolAnswer is None and rt is not None:
        mouse.show_cursor(True, True)
        start = get_time()
        rt, position = readMouse(start, mouseButton, time_left)

        mouse.hide_cursor(True, True)

        if rt is not None:
            if play_sound1_box.overlapping_with_position(position):
                play_sound(0)
                exp.add_experiment_info(['Played_sound_number-{}_sound_name-{}_timing-{}'.format(
                    0, sounds[0], exp.clock.time)])
                play_sound1, _ = sound_x_box(1, play_sound1_position, True, play_text, True)
                play_sound1.plot(bs)
                bs.present(False, True)
                exp.clock.wait(clicPeriod)

                play_sound1, _ = sound_x_box(1, play_sound1_position, True, play_text)
                play_sound1.plot(bs)
                bs.present(False, True)
                if time_left - rt > clicPeriod:
                    time_left = time_left - clicPeriod - rt
                else:
                    break
            elif play_sound2_box.overlapping_with_position(position):
                play_sound(1)
                exp.add_experiment_info(['Played_sound_number-{}_sound_name-{}_timing-{}'.format(
                    1, sounds[1], exp.clock.time)])
                play_sound2, _ = sound_x_box(2, play_sound2_position, True, play_text, True)
                play_sound2.plot(bs)
                bs.present(False, True)
                exp.clock.wait(clicPeriod)

                play_sound2, _ = sound_x_box(2, play_sound2_position, True, play_text)
                play_sound2.plot(bs)
                bs.present(False, True)
                if time_left - rt > clicPeriod:
                    time_left = time_left - clicPeriod - rt
                else:
                    break
            elif play_sound3_box.overlapping_with_position(position):
                play_sound(2)
                exp.add_experiment_info(['Played_sound_number-{}_sound_name-{}_timing-{}'.format(
                    2, sounds[2], exp.clock.time)])
                play_sound3, _ = sound_x_box(3, play_sound3_position, True, play_text, True)
                play_sound3.plot(bs)
                bs.present(False, True)
                exp.clock.wait(clicPeriod)

                play_sound3, _ = sound_x_box(3, play_sound3_position, True, play_text)
                play_sound3.plot(bs)
                bs.present(False, True)
                if time_left - rt > clicPeriod:
                    time_left = time_left - clicPeriod - rt
                else:
                    break
            elif choose_sound1_box.overlapping_with_position(position):
                boolAnswer = m._matrix.item(locationCard)._sound == 0
                # bool condition explanation
                # it is called sound 1, but sounds are identified as being 0,1,2 in the code. Therefore, sound 1 is 0,
                # sound 2 is 1, etc.
                choose_sound1, _ = sound_x_box(1, choose_sound1_position, True, choose_text, True)
                choose_sound1.plot(bs)
                bs.present(False, True)
                exp.clock.wait(clicPeriod)

                choose_sound1, _ = sound_x_box(1, choose_sound1_position, True, choose_text)
                choose_sound1.plot(bs)
                bs.present(False, True)

                exp.data.add([exp.clock.time, picture, boolAnswer, sounds[0], rt])
                exp.add_experiment_info(['Response_correct-{}_responded-{}_soundId-{}_timing_{}'.format(
                    boolAnswer, 0, sounds[0], exp.clock.time)])
            elif choose_sound2_box.overlapping_with_position(position):
                boolAnswer = m._matrix.item(locationCard)._sound == 1
                choose_sound2, _ = sound_x_box(2, choose_sound2_position, True, choose_text, True)
                choose_sound2.plot(bs)
                bs.present(False, True)
                exp.clock.wait(clicPeriod)

                choose_sound2, _ = sound_x_box(2, choose_sound2_position, True, choose_text)
                choose_sound2.plot(bs)
                bs.present(False, True)

                exp.data.add([exp.clock.time, picture, boolAnswer, sounds[1], rt])
                exp.add_experiment_info(['Response_correct-{}_responded-{}_soundId-{}_timing_{}'.format(
                    boolAnswer, 1, sounds[1], exp.clock.time)])
            elif choose_sound3_box.overlapping_with_position(position):
                boolAnswer = m._matrix.item(locationCard)._sound == 2
                choose_sound3, _ = sound_x_box(3, choose_sound3_position, True, choose_text, True)
                choose_sound3.plot(bs)
                bs.present(False, True)
                exp.clock.wait(clicPeriod)

                choose_sound3, _ = sound_x_box(3, choose_sound3_position, True, choose_text)
                choose_sound3.plot(bs)
                bs.present(False, True)

                exp.data.add([exp.clock.time, picture, boolAnswer, sounds[2], rt])
                exp.add_experiment_info(['Response_correct-{}_responded-{}_soundId-{}_timing_{}'.format(
                    boolAnswer, 2, sounds[2], exp.clock.time)])
            else:
                if time_left - rt > clicPeriod:
                    time_left = time_left - clicPeriod - rt
                else:
                    break
        elif rt is None:
            exp.data.add([exp.clock.time, picture, None, None, AssociationResponseTime])
            exp.add_experiment_info(['NoResponse'])  # Add sync infoexp.add_experiment_info(['NoResponse'])  # Add sync info
        else:
            exp.data.add([exp.clock.time, picture, 'ERROR', 'ERROR', 'ERROR'])
            exp.add_experiment_info(['ERROR'])
    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI)

delete_temp_files()

exp.clock.wait(5000)
