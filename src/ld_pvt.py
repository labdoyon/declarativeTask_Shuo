import sys
import random
import expyriment
from expyriment.misc._timer import get_time

from ld_matrix import LdMatrix
from config import *
from ld_utils import getLanguage, setCursor, rename_output_files_to_BIDS


if not windowMode:  # Check WindowMode and Resolution
    expyriment.control.defaults.window_mode = windowMode
    expyriment.control.defaults.window_size = expyriment.misc.get_monitor_resolution()
    windowSize = expyriment.control.defaults.window_size
else:
    expyriment.control.defaults.window_mode = windowMode
    expyriment.control.defaults.window_size = windowSize

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject

experimentName = arguments[0]
subjectName = arguments[1]

exp = expyriment.design.Experiment(experimentName)  # Save experiment name

session = experiment_session[experimentName]
output_dir = 'sourcedata' + os.path.sep +\
             'sub-' + subjectName + os.path.sep +\
             'ses-' + session + os.path.sep +\
             'beh'
expyriment.io.defaults.datafile_directory = output_dir
expyriment.io.defaults.eventfile_directory = output_dir

exp.add_experiment_info('Subject:')
exp.add_experiment_info(subjectName)
language = str(getLanguage(subjectName, 0, 'choose-language'))
exp.add_experiment_info('language:')
exp.add_experiment_info(language)

if not windowMode:  # Check WindowMode and Resolution
    expyriment.control.defaults.window_mode = windowMode
    expyriment.control.defaults.window_size = expyriment.misc.get_monitor_resolution()
    windowSize = expyriment.control.defaults.window_size
else:
    expyriment.control.defaults.window_mode = windowMode
    expyriment.control.defaults.window_size = windowSize

exp = expyriment.design.Experiment(name="PVT_B")
expyriment.control.initialize(exp)
expyriment.control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

bids_datafile, bids_eventfile = rename_output_files_to_BIDS(subjectName, session, experimentName,
                                                            expyriment.io.defaults.datafile_directory,
                                                            expyriment.io.defaults.eventfile_directory)
exp.data.rename(bids_datafile)
exp.events.rename(bids_eventfile)

m = LdMatrix(matrixSize, windowSize)  # Create Matrix
keyboard = expyriment.io.Keyboard
mouse = expyriment.io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

setCursor(arrow)

bs = expyriment.stimuli.BlankScreen(bgColor)  # Create blank screen
m.plotDefault(bs, True)  # Draw default grid

# TODO add instructions for the participant

exp.add_data_variable_names(['Trial', 'Start_Time', 'ResponseTime', 'ISI-before-next-trial', 'clicked_before_start'])
# random amount of time before the subject is prompted to respond as fast as he can
skip_next_trial = False
isi_before_next_trial = random.randint(pvt_min_max_ISI[0], pvt_min_max_ISI[1])
inter_trial_start_time = get_time()
mouse.clear()
exp.keyboard.clear()

for i in range(pvt_number_trials):
    exp.add_experiment_info(f'Trial_{i}')
    # Inter-Trial section
    # exp.clock.wait(isi_before_next_trial, process_control_events=True)
    while get_time() < inter_trial_start_time + isi_before_next_trial/1000:
        if mouse.get_last_button_down_event(process_quit_event=True) is not None:
            exp.add_experiment_info(f'Trial_{i}_clicked-before-trial-start-time_{get_time()}')
            exp.data.add([i, None, None, None, True])

            isi_before_next_trial = random.randint(pvt_min_max_ISI[0], pvt_min_max_ISI[1])

            # Show feedback
            negative_feedback = expyriment.stimuli.FixCross(size=(cardSize[0] / 2, cardSize[1] / 2),
                                                            colour=expyriment.misc.constants.C_RED,
                                                            line_width=fixation_cross_thickness)
            m.plotCueCard(False, bs, draw=False, nocross=True)  # Show Cue
            negative_feedback.plot(bs)
            bs.present(False, True)
            exp.clock.wait(pvt_show_feedback_duration, process_control_events=True)
            m.plotCueCard(False, bs, True)  # Show default fixation cross

            skip_next_trial = True
            break
        if exp.keyboard.process_control_keys():
            exp.keyboard.process_control_keys()

    if skip_next_trial:
        skip_next_trial = False
        mouse.clear()
        isi_before_next_trial = random.randint(pvt_min_max_ISI[0], pvt_min_max_ISI[1])
        inter_trial_start_time = get_time()
        continue  # skip to next Trial

    # Trial section
    mouse.clear()
    response = None
    start_time = get_time()
    exp.add_experiment_info(f'Trial_{i}_start-time_{int(start_time*1000)}')
    while response is None:
        time_to_present = str(int((get_time() - start_time) * 1000))  # display in ms
        number_to_display = expyriment.stimuli.TextLine(time_to_present, position=(0, 0),
                                                        text_size=45, text_colour=textColor,
                                                        background_colour=bgColor, max_width=None)
        number_to_display.plot(bs)
        bs.present(False, True)
        response = mouse.get_last_button_down_event(process_quit_event=False)
        exp.keyboard.process_control_keys()

    rt = get_time() - start_time
    isi_before_next_trial = random.randint(pvt_min_max_ISI[0], pvt_min_max_ISI[1])
    exp.add_experiment_info(f'Trial_{i}_ResponseTime_{rt}_isi-before-next-trial_isi_before_next_trial_'
                            f'{isi_before_next_trial}')
    exp.data.add([i, start_time, rt, isi_before_next_trial, False])

    # show score as feedback
    exp.clock.wait(pvt_show_feedback_duration, process_control_events=True)

    m.plotCueCard(False, bs, True)  # Show Cue
    del rt, start_time, response
    mouse.clear()

    inter_trial_start_time = get_time()
