import sys

import numpy as np
from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants
from expyriment.misc._timer import get_time

from ld_matrix import LdMatrix
from ld_utils import setCursor, newRandomPresentation, readMouse, path_leaf, getLanguage, generate_bids_filename
from ttl_catch_keyboard import wait_for_ttl_keyboard
from config import *
from ld_stimuli_names import presentation_screen_text

if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject

experimentName = arguments[0]
subjectName = arguments[1]

exp = design.Experiment(experimentName)  # Save experiment name

session = experiment_session[experimentName]
output_dir = 'sourcedata' + os.path.sep +\
             'sub-' + subjectName + os.path.sep +\
             'ses-' + session + os.path.sep +\
             'beh'
io.defaults.datafile_directory = output_dir
io.defaults.eventfile_directory = output_dir

exp.add_experiment_info(['Subject: '])  # Save Subject Code
exp.add_experiment_info([subjectName])  # Save Subject Code
language = str(getLanguage(subjectName, 0, 'choose-language'))
exp.add_experiment_info('language: ')
exp.add_experiment_info(language)  # Save Subject Code

# Save time, nblocks, position, correctAnswer, RT
exp.add_data_variable_names(['Time', 'NBlock', 'Picture', 'Answers', 'RT'])

m = LdMatrix(matrixSize, windowSize)  # Create Matrix

picturesExamples = np.random.permutation(picturesExamples)

presentationOrder = newRandomPresentation()
presentationOrder = presentationOrder[0:3]

control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

i = 1
wouldbe_datafile = generate_bids_filename(
        subjectName, session, experimentName, filename_suffix='_beh', filename_extension='.xpd')
wouldbe_eventfile = generate_bids_filename(
    subjectName, session, experimentName, filename_suffix='_events', filename_extension='.xpe')

while os.path.isfile(io.defaults.datafile_directory + os.path.sep + wouldbe_datafile) or \
        os.path.isfile(io.defaults.eventfile_directory + os.path.sep + wouldbe_eventfile):
    i += 1
    i_string = '0' * (2 - len(str(i))) + str(i)  # 0 padding, assuming 2-digits number
    wouldbe_datafile = generate_bids_filename(subjectName, session, experimentName, filename_suffix='_beh',
                                              filename_extension='.xpd', run=i_string)
    wouldbe_eventfile = generate_bids_filename(subjectName, session, experimentName, filename_suffix='_events',
                                               filename_extension='.xpe', run=i_string)
exp.data.rename(wouldbe_datafile)
exp.events.rename(wouldbe_eventfile)

nPict = 0
for nCard in presentationOrder:
    m._matrix.item(nCard).setPicture(picturesExamplesFolder + picturesExamples[nPict])
    nPict += 1

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

setCursor(arrow)

bs = stimuli.BlankScreen(bgColor)  # Create blank screen
m.plotDefault(bs, True)  # Draw default grid

exp.clock.wait(shortRest, process_control_events=True)

wait_for_ttl_keyboard()

exp.add_experiment_info(['Block {} - Presentation'.format(0)])  # Add listPictures
exp.add_experiment_info(str(list(presentationOrder)))  # Add listPictures

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, presentation_screen_text[language], draw=False)
bs.present(False, True)

exp.clock.wait(shortRest, process_control_events=True)  # Short Rest between presentation and cue-recall

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

exp.clock.wait(shortRest, process_control_events=True)

for nCard in presentationOrder:
    mouse.hide_cursor(True, True)
    m.plotCard(nCard, True, bs, True)  # Show Location for ( 2s )
    exp.clock.wait(presentationCard, process_control_events=True)
    m.plotCard(nCard, False, bs, True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)

presentationOrder = np.random.permutation(presentationOrder)
exp.clock.wait(shortRest, process_control_events=True)  # Short Rest between presentation and cue-recall

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions(bs, instructions_card, ' TEST ', draw=False)
bs.present(False, True)

exp.clock.wait(shortRest, process_control_events=True)  # Short Rest between presentation and cue-recall

m.plot_instructions_rectangle(bs, instructions_card, draw=False)
m.plot_instructions_card(bs, instructions_card, draw=False)
bs.present(False, True)

correctAnswers = 0

exp.add_experiment_info(['Block {} - Test'.format(0)])  # Add listPictures
exp.add_experiment_info(str(list(presentationOrder)))  # Add listPictures

cuecard_index = int(len(classPictures)/2)

for nCard in presentationOrder:

    m._cueCard.setPicture(m._matrix.item(nCard).stimuli[0].filename)  # Associate Picture to CueCard

    m.plotCueCard(True, bs, True)  # Show Cue

    exp.clock.wait(presentationCard, process_control_events=True)  # Wait presentationCard

    m.plotCueCard(False, bs, True)  # Hide Cue

    mouse.show_cursor(True, True)

    start = get_time()
    rt, position = readMouse(start, mouseButton, responseTime)

    mouse.hide_cursor(True, True)

    if rt is not None:

        currentCard = m.checkPosition(position)

        if currentCard is not None:
            m._matrix.item(currentCard).color = clickColor
            m.plotCard(currentCard, False, bs, True)

            exp.clock.wait(clicPeriod, process_control_events=True)  # Wait 500ms

            m._matrix.item(currentCard).color = cardColor
            m.plotCard(currentCard, False, bs, True)

        if currentCard == nCard:
            correctAnswers += 1
            exp.data.add([exp.clock.time, 0,
                          path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                          path_leaf(m._matrix.item(currentCard).stimuli[0].filename),
                          rt])

        elif currentCard is None:
            exp.data.add([exp.clock.time, 0,
                          path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                          None,
                          rt])
        else:
            exp.data.add([exp.clock.time, 0,
                          path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                          path_leaf(m._matrix.item(currentCard).stimuli[0].filename),
                          rt])
    else:
        exp.data.add([exp.clock.time, 0,
                      path_leaf(m._matrix.item(nCard).stimuli[0].filename),
                      None,
                      rt])

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)


if correctAnswers == 3:
    m.plot_instructions_rectangle(bs, instructions_card, draw=False)
    m.plot_instructions(bs, instructions_card, ' PERFECT ', draw=False)
    bs.present(False, True)

    exp.clock.wait(responseTime, process_control_events=True)


