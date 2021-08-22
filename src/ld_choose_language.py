import os
import sys
import expyriment
from cursesmenu import *
from cursesmenu.items import *
from config import experiment_session
from ld_utils import generate_bids_filename
from ld_stimuli_names import supported_languages

sep = os.path.sep

arguments = str(''.join(sys.argv[1:])).split(',')
experimentName = arguments[0]
subject_name = arguments[1]
language = arguments[2]

if language == 'None':
    python = 'py'
    menu = CursesMenu(title="choose a language")

    choose_language = []
    for i, supported_language in enumerate(supported_languages):
        choose_language.append(
            CommandItem(text='choose ' + supported_language + ' for the experiment for this participant',
                        command=python + " src" + os.path.sep + "ld_choose_language.py",
                        arguments='choose-language, ' + subject_name + ', ' + supported_language,
                        menu=menu,
                        should_exit=True)
                               )
        menu.append_item(choose_language[i])
    menu.show()

else:
    expyriment.control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=True)
    exp = expyriment.design.Experiment(experimentName)  # Save experiment name

    session = experiment_session[experimentName]
    session_dir = 'sourcedata' + os.path.sep + \
                  'sub-' + subject_name + os.path.sep + \
                  'ses-' + session + os.path.sep
    output_dir = session_dir + 'beh'
    if not os.path.isdir(session_dir):
        os.mkdir(session_dir)
    expyriment.io.defaults.datafile_directory = output_dir
    expyriment.io.defaults.eventfile_directory = output_dir

    exp.add_experiment_info('Subject: ')  # Save Subject Code
    exp.add_experiment_info(subject_name)
    exp.add_experiment_info('language: ')
    exp.add_experiment_info(language)
    expyriment.control.initialize(exp)
    expyriment.control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

    i = 1
    wouldbe_datafile = generate_bids_filename(
        subject_name, session, experimentName, filename_suffix='_beh', filename_extension='.xpd')
    wouldbe_eventfile = generate_bids_filename(
        subject_name, session, experimentName, filename_suffix='_events', filename_extension='.xpe')

    while os.path.isfile(expyriment.io.defaults.datafile_directory + sep + wouldbe_datafile) or \
            os.path.isfile(expyriment.io.defaults.eventfile_directory + sep + wouldbe_eventfile):
        i += 1
        i_string = '0' * (2 - len(str(i))) + str(i)  # 0 padding, assuming 2-digits number
        wouldbe_datafile = generate_bids_filename(subject_name, session, experimentName, filename_suffix='_beh',
                                                  filename_extension='.xpd', run=i_string)
        wouldbe_eventfile = generate_bids_filename(subject_name, session, experimentName, filename_suffix='_events',
                                                   filename_extension='.xpe', run=i_string)

    exp.data.rename(wouldbe_datafile)
    exp.events.rename(wouldbe_eventfile)

    expyriment.control.end()
