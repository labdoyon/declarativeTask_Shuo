import sys
import random

from expyriment import control, stimuli, design, misc, io
from expyriment.misc import constants
from expyriment.misc._timer import get_time

from ld_sound import create_temp_sound_files, delete_temp_files
from ld_utils import getPreviousSoundsAllocation, readMouse
from ld_matrix import LdMatrix
from config import *

if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

if debug:
    control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=True)


def vertices_frame(size, frame_thickness):
    return [(size[0]-frame_thickness, 0),
            (0, -size[1]),
            (-size[0], 0),
            (0, size[1]),
            (frame_thickness, 0),
            (0, -(size[1]-frame_thickness)),
            (size[0]-2*frame_thickness, 0),
            (0, size[1]-2*frame_thickness),
            (-(size[0]-2*frame_thickness), 0)]


arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject
# arguments = ['Encoding', 'test']
experimentName = arguments[0]
subjectName = arguments[1]

exp = design.Experiment(experimentName)  # Save experiment name
exp.add_experiment_info('Subject: ')
exp.add_experiment_info(subjectName)

# Save time, nblocks, position, correctAnswer, RT
data_variables_names = ['sound_played', 'Time', 'category']
data_variables_names.extend(['Picture' + str(i) for i in range(len(classPictures))])
exp.add_data_variable_names(data_variables_names)

soundsAllocation_index = getPreviousSoundsAllocation(subjectName, 0, 'choose-sound-association')
soundsAllocation = {key: sounds[soundsAllocation_index[key]] for key in soundsAllocation_index.keys()}

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

control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)
exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

m = LdMatrix((len(classPictures), 1), windowSize)
bs = stimuli.BlankScreen(bgColor)  # Create blank screen
m.plotDefault(bs, True)

sounds_order = []
[sounds_order.extend([i]*3) for i in range(len(sounds))]
random.shuffle(sounds_order)  # this randomized sounds presentation order

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], m.gap * 2 + cardSize[1]), position=(
    0, -windowSize[1]/float(2) + (2 * m.gap + cardSize[1])/float(2)), colour=constants.C_DARKGREY)
instructions = stimuli.TextLine(' PRESENTATION ',
                                        position=(0, -windowSize[1]/float(2) + (2*m.gap + cardSize[1])/float(2)),
                                        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                        text_underline=None, text_colour=textColor,
                                        background_colour=bgColor,
                                        max_width=None)
        instructionRectangle.plot(bs)
        instructions.plot(bs)
        bs.present(False, True)

        exp.clock.wait(shortRest)
        instructionRectangle.plot(bs)
        bs.present(False, True)

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI)

for j, sound_index in enumerate(sounds_order):
    sound = sounds[sound_index]
    category = [key for key in soundsAllocation_index.keys() if soundsAllocation_index[key] == sound_index][0]
    m.associateCategory(category)
    exp.add_experiment_info('Trial_{}_PlaySound_soundIndex_{}_soundId_{}'.format(j, sound_index, sound))

    shuffled_categories = random.sample(classPictures, len(classPictures))
    pictures_allocation = []
    for i, temp_category in enumerate(shuffled_categories):
        picture = random.choice(listPictures[temp_category])
        pictures_allocation.append(picture)
        listPictures[temp_category].remove(picture)

        if temp_category == category:
            correctCard = i

    m.associatePictures(pictures_allocation)
    exp.add_experiment_info(str(m.listPictures))
    for i in range(len(classPictures)):
        m.plotCard(i, True, bs, True)
        exp.add_experiment_info('ShowCard_pos_{}_card_{}_timing_{}'.format(
            i, m.listPictures[i], exp.clock.time))

    exp.clock.wait(2000)

    noValidResponse = True
    time_to_respond = 2000
    while noValidResponse:  # The subject
        rt = None
        currentCard = None
        while rt is None or currentCard is None:
            currentCard = None
            position = None
            if rt is None:
                m.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
                time_to_respond = 2000
            else:
                time_to_respond = time_to_respond - rt - clicPeriod
            mouse.show_cursor(True, True)
            start = get_time()
            rt, position = readMouse(start, mouseButton, time_to_respond)
            mouse.hide_cursor(True, True)
            if position is not None:
                currentCard = m.checkPosition(position)

        exp.add_experiment_info('Response_pos_{}_card_{}_timing_{}'.format(
            currentCard,
            m.listPictures[currentCard],
            exp.clock.time))  # Add sync info

        # graphical clic effect block
        m._matrix.item(currentCard).color = clickColor
        m.plotCard(currentCard, False, bs, True)
        exp.clock.wait(clicPeriod)  # Wait 200ms
        m._matrix.item(currentCard).color = cardColor
        m.plotCard(currentCard, True, bs, True)

        card = m._matrix.item(currentCard)
        if currentCard == correctCard:
            noValidResponse = False
            m.plotCard(correctCard, True, bs, True)

            correct_response_stimuli = stimuli.Shape(position=card.position,
                                                     vertex_list=vertices_frame(size=(110, 110),
                                                                                frame_thickness=10),
                                                     colour=misc.constants.C_GREEN)
            correct_response_stimuli.plot(bs)
            bs.present(False, True)
            exp.clock.wait(shortRest)
            correct_response_stimuli = stimuli.Shape(position=card.position,
                                                     vertex_list=vertices_frame(size=(110, 110),
                                                                                frame_thickness=10),
                                                     colour=bgColor)
            correct_response_stimuli.plot(bs)
            bs.present(False, True)
            m.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
            exp.add_experiment_info('ResponseCorrect_pos_{}_card_{}_timing_{}'.format(
                currentCard,
                m.listPictures[currentCard],
                exp.clock.time))  # Add sync info
        else:
            wrong_response_stimuli = stimuli.Shape(position=card.position,
                                                     vertex_list=vertices_frame(size=(110, 110),
                                                                                frame_thickness=10),
                                                     colour=misc.constants.C_RED)
            wrong_response_stimuli.plot(bs)
            bs.present(False, True)
            exp.clock.wait(shortRest)
            wrong_response_stimuli = stimuli.Shape(position=card.position,
                                                     vertex_list=vertices_frame(size=(110, 110),
                                                                                frame_thickness=10),
                                                     colour=bgColor)
            wrong_response_stimuli.plot(bs)
            bs.present(False, True)

    exp.clock.wait(shortRest)

instructions = stimuli.TextLine(
    ' THANK YOU ',
    position=(0, -windowSize[1] / float(2) + (2 * m[0].gap + cardSize[1]) / float(2)),
    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
    text_underline=None, text_colour=textColor, background_colour=bgColor,
    max_width=None)

instructions.plot(bs)
bs.present(False, True)

exp.clock.wait(restPeriod)

control.end()
