import os
import sys
import expyriment
from cursesmenu import *
from cursesmenu.items import *

from ld_utils import generate_bids_filename
from config import supported_start_by_choices, experiment_session

sep = os.path.sep

arguments = str(''.join(sys.argv[1:])).split(',')
experimentName = arguments[0]
subject_name = arguments[1]
faces_places_choice = arguments[2]

if faces_places_choice == 'None':
    python = 'py'
    menu = CursesMenu(title="choose to start the experiment by class1 or class2")

    choose_language = []
    for i, supported_choice in enumerate(supported_start_by_choices):
        choose_language.append(
            CommandItem(text=supported_choice + ' for the experiment for this participant',
                        command=python + " src" + os.path.sep + "ld_choose_faces_places.py",
                        arguments='choose-faces-places, ' + subject_name + ', ' + supported_choice,
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

    exp.add_experiment_info('Subject:')  # Save Subject Code
    exp.add_experiment_info(subject_name)
    exp.add_experiment_info('start_by_class1_or_class2:')
    exp.add_experiment_info(faces_places_choice)
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
