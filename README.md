# declarative task 3
Current developer and curator: thibault.vlieghe@mcgill.ca
Original author: arnaud.bore@gmail.com

# Description
this experiment is made of 8 phases
1. Example
2. StimuliPresentation
3. PreLearning
(Optional) soundVolumeAdjustment
4. Learning
5. TestMatrixA
6. ConsolidationMatrixA
7. Recognition
8. Association

A phase typically has one associated script
e.g. example phase: src/ld_example.py

A subject must go through all phases for the experiment to be complete

# Installation
Please use  python3.8.1
install requirements with pip: <pip install -r requirements.txt>

# Documentation
this task was built using Expyriment 0.10.0, a python library for neuroimaging experiments. More details on this library can be found at: https://docs.expyriment.org/

# Show Matrix:
python src\declarativeTask3\ld_show_matrix.py "show_matrix,<subject_id>"
(replace python by the relevant python interpreter if necessary)

# DEBUGGING
if the program crashes, the information on the error can be found in the .xpe file in sourcedata/sub-<subject-id>/ses-<ses-id>/<task-filename>.xpe

You can also debug faster via command line as follows:
go to ld_runExperimentDayOne.py
take a menu element (say Example, 'ses_ExpD1__task_Example = CommandItem()')
take the 'command' and 'arguments' element of the menu element
e.g.
command=python + " " + os.path.join("src", "declarativeTask3", "ld_example.py"),
    arguments='ses-ExpD1_task-Example,' + sys.argv[1]

You may now run the following in the command line, to run this step of the experiment without the menu provided in ld_runExperimentDayOne.py
py src\declarativeTask3\ld_example.py 'ses-ExpD1_task-Example,<subject_id>'
You will see any error the program generates much faster

# Code examples for installation, initiation and testing:

python -m pip install -e .
% code to install a new version of DeMo task

python -m pip install -r requirements.txt
% code to install the required version of different libaries.

pip install -e .
% initialize the set-up script

python tests\monitor_ttl_interval.py
% code to calibrate a proper TTL interval

python src\declarativeTask3\ld_show_matrix.py "show_matrix,BEPI_001" 
% code to show the image-location assignment result for a given subject

python ld_runExperimentDayOne.py "SUBJ_ID"
% code to initiate the navigation panel

change 1024 x 768 
% change display setting before running the task

python src\declarativeTask3\ld_encoding.py 'ses-ExpD2_task-Test-2ndClass,BEPI_001'
python src\declarativeTask3\ld_generate_mvpa_trials.py "ses-ExpMVPA_NOT-A-TASK-generate-mvpa-trials,BEPI_001" 
% debug on particular task and subject

