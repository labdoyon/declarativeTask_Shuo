import sys
import os
import random
import math

from expyriment import control, io, design

from declarativeTask3.config import experiment_session, \
    experiment_use_faces_or_places, mvpa_equalize_number_correctly_recalled_images, \
    center_card_position, removeCards, mvpa_number_blocks, mvpa_number_trials_correct_position, \
    mvpa_number_trials_wrong_position, only_faces_remove_cards, only_places_remove_cards, \
    mvpa_block_number_TRs_to_wait_inter_trials_for_correct_positions, \
    mvpa_block_number_TRs_to_wait_inter_trials_for_wrong_positions, \
    matrixSize, windowSize
from declarativeTask3.ld_matrix import LdMatrix
from declarativeTask3.ld_utils import getPreviousMatrix, getPlacesOrFacesChoice, \
    getPreviouslyCorrectlyRecalledImages, newRandomPresentation, rename_output_files_to_BIDS


arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject
experimentName = arguments[0]
subjectName = arguments[1]

learningMatrix = getPreviousMatrix(subjectName, 0, 'PreLearn')
faces_places_choice = getPlacesOrFacesChoice(subjectName, 0, 'choose-faces-places')

if experiment_use_faces_or_places[faces_places_choice]['PreTest'] == 'faces' and \
        experiment_use_faces_or_places[faces_places_choice]['PostLearn'] == 'places':
    correctly_recalled_faces = getPreviouslyCorrectlyRecalledImages(subjectName, experienceName='PreTest')
    correctly_recalled_places = getPreviouslyCorrectlyRecalledImages(subjectName, experienceName='PostLearn')
elif experiment_use_faces_or_places[faces_places_choice]['PreTest'] == 'places' and \
        experiment_use_faces_or_places[faces_places_choice]['PostLearn'] == 'faces':
    correctly_recalled_faces = getPreviouslyCorrectlyRecalledImages(subjectName, experienceName='PreTest')
    correctly_recalled_places = getPreviouslyCorrectlyRecalledImages(subjectName, experienceName='PostLearn')

FACEs_c_rem = [learningMatrix[position_index] if position_index < center_card_position
               else learningMatrix[position_index - 1]
               for position_index, correct_remembered in correctly_recalled_faces.items() if correct_remembered is True]
PLACEs_c_rem = [learningMatrix[position_index] if position_index < center_card_position
                else learningMatrix[position_index - 1]
                for position_index, correct_remembered in correctly_recalled_places.items() if correct_remembered is True]

if len(FACEs_c_rem) > len(PLACEs_c_rem):
   FACEs_c_rem = random.sample(FACEs_c_rem, len(PLACEs_c_rem))
elif len(FACEs_c_rem) < len(PLACEs_c_rem):
   PLACEs_c_rem = random.sample(PLACEs_c_rem, len(FACEs_c_rem))

FACEs_mat = [learningMatrix.index(image) for image in FACEs_c_rem]
PLACEs_mat = [learningMatrix.index(image) for image in PLACEs_c_rem]
FACEs_mat = [element if element < center_card_position else element+1 for element in FACEs_mat]
PLACEs_mat = [element if element < center_card_position else element+1 for element in PLACEs_mat]
FACEs_mat += list(set(range(49)) - set(only_faces_remove_cards) - set(FACEs_mat))
PLACEs_mat += list(set(range(49)) - set(only_places_remove_cards) - set(PLACEs_mat))

blk_n = 5
trials_n = 48
ratio_correct = 3/4
left_n = len(FACEs_c_rem)
correct_first_n = math.floor(trials_n*ratio_correct/2/left_n)*left_n # >=1 repetition, in case e.g. left_n = 7, repeat twice then
n_w_trials = int(trials_n-trials_n*ratio_correct)

# prepare 5 big vectors output
V_imgID = [['NaN']*trials_n]*blk_n
V_CorW = [['NaN']*trials_n]*blk_n
V_ForP = [['NaN']*trials_n]*blk_n
V_TR_ITI = [[-1]*trials_n]*blk_n
V_Loca = [[-1]*trials_n]*blk_n


# make sure each "remembered" images are shown at least once in each block.
fill_runs = math.floor(trials_n*ratio_correct/2/left_n)
for blk in range(0,blk_n):
    v_imgID = ['NaN'] * trials_n
    for fr in range(0,fill_runs):
        v_imgID[fr*left_n*2:(fr+1)*left_n*2:2] = random.sample(FACEs_c_rem, left_n) # start from the correct trials first, may take wrong spots with random assignments in the end
        v_imgID[fr*left_n*2+1:(fr+1)*left_n*2:2] = random.sample(PLACEs_c_rem, left_n)
    V_imgID[blk] = v_imgID


# working on the left correct trials ID to fill in
if correct_first_n < ratio_correct*trials_n/2:
    n_c_left_allblk = int(((ratio_correct*trials_n/2)-correct_first_n)*blk_n)
    V_c_FACEsID = ['NaN'] * n_c_left_allblk
    V_c_PLACEsID = ['NaN'] * n_c_left_allblk

    fill_c_runs = math.ceil(n_c_left_allblk/left_n) # step, selecting from left images
    trials_n_lastrun = n_c_left_allblk % left_n # last few remainer to fill
    if trials_n_lastrun == 0:
        trials_n_lastrun = left_n # the step to fill in

    for ii in range(1,fill_c_runs+1):
        if ii == fill_c_runs : # last run, left with a few to fill in
            V_c_FACEsID[-trials_n_lastrun:] = random.sample(FACEs_c_rem, trials_n_lastrun)
            V_c_PLACEsID[-trials_n_lastrun:] = random.sample(PLACEs_c_rem, trials_n_lastrun)
        else:
            item_head = (ii-1)*left_n
            item_tail = ii*left_n
            V_c_FACEsID[item_head:item_tail] = random.sample(FACEs_c_rem, left_n)
            V_c_PLACEsID[item_head:item_tail] = random.sample(PLACEs_c_rem, left_n)

# working on the all/left wrong trials ID and all the wrong location decisions
n_w_left_allblk = int(((trials_n/2)-correct_first_n)*blk_n)
V_w_FACEsID = ['NaN'] * n_w_left_allblk
V_w_PLACEsID = ['NaN'] * n_w_left_allblk
V_w_FACEsLoc = [-1] * int(n_w_trials/2*blk_n)
V_w_PLACEsLoc = [-1] * int(n_w_trials/2*blk_n)

fill_w_runs = math.ceil(n_w_left_allblk/left_n) # step, selecting from left images
trials_n_lastrun = n_w_left_allblk % left_n # last few remainer to fill
if trials_n_lastrun == 0:
    trials_n_lastrun = left_n # the step to fill in

for ii in range(1,fill_w_runs+1):

    if ii == fill_w_runs : # last run, left with a few to fill in
        V_w_FACEsID[-trials_n_lastrun:] = random.sample(FACEs_c_rem, trials_n_lastrun)
        V_w_PLACEsID[-trials_n_lastrun:] = random.sample(PLACEs_c_rem, trials_n_lastrun)
    else:
        item_head = (ii-1)*left_n+0
        item_tail = ii*left_n
        V_w_FACEsID[item_head:item_tail] = random.sample(FACEs_c_rem, left_n)
        V_w_PLACEsID[item_head:item_tail] = random.sample(PLACEs_c_rem, left_n)

# extend the wrong ones from the begining, if first run presentation of all "remembered" items are > correct trials, meaning it takes the trials ID for wrong spots
if correct_first_n > ratio_correct*trials_n/2:
    V_w_FACEsID_all = []
    V_w_PLACEsID_all = []

    for blk in range(0,blk_n):
        w_ext_f = list(V_imgID[blk][int(trials_n*ratio_correct):correct_first_n*2:2]) + V_w_FACEsID[blk*(int(trials_n/2-correct_first_n)):(blk+1)*int(trials_n/2-correct_first_n)]
        V_w_FACEsID_all = V_w_FACEsID_all + w_ext_f
        w_ext_p = list(V_imgID[blk][int(trials_n*ratio_correct)+1:correct_first_n*2:2]) + V_w_PLACEsID[blk*(int(trials_n/2-correct_first_n)):(blk+1)*int(trials_n/2-correct_first_n)]
        V_w_PLACEsID_all = V_w_PLACEsID_all + w_ext_p
else: # e.g. correct_first_n = 16,
    V_w_FACEsID_all = V_w_FACEsID;
    V_w_PLACEsID_all = V_w_PLACEsID;

# prepare the wrong location, by step 24
repeat_runs = math.ceil(len(V_w_FACEsID_all)/len(FACEs_mat))
loc_n_lastrun = len(V_w_FACEsID_all) % len(FACEs_mat)
if loc_n_lastrun == 0:
    loc_n_lastrun = 24

for rr in range(1,repeat_runs+1):
    if rr == repeat_runs : # last run, left with a few to select
        loca_n_2select = loc_n_lastrun
    else:
        loca_n_2select = 24

    # select wrong location and avoid spatial contiguity
    need_select = 1 # 0 = no, 1 = yes (default, it needs for the first entering)
    while need_select == 1:
        loca_f_thisrun = random.sample(FACEs_mat, loca_n_2select)
        need_select = 0 # done once

        # checking then
        for wi in range(0,len(loca_f_thisrun)):
            w_f_currIMG = V_w_FACEsID_all[(rr-1)*24+wi]
            w_f_loca = loca_f_thisrun[wi]
            c_f_loca = FACEs_mat[FACEs_c_rem.index(w_f_currIMG)]

            coordi_w_col = int(math.floor(w_f_loca/7)+1)
            coordi_w_row = int((w_f_loca % 7)+1)
            coordi_c_col = int(math.floor(c_f_loca/7)+1)
            coordi_c_row = int((c_f_loca % 7)+1)

            if ((coordi_w_col-coordi_c_col)**2+(coordi_w_row-coordi_c_row)**2)**0.5 <= 2**0.5:
                print('Oops, got one location for wrong image assigned attached with its correct location.')
                print('FAILED selection - ' + ' wrong trial : ' + w_f_currIMG +
                  ', corr_loc - ' + str(coordi_c_row) + ', ' + str(coordi_c_col) +
                  ', wrong_loc - ' + str(coordi_w_row) + ', ' + str(coordi_w_col))
                need_select = 1 # do one more, because not satisfied
                break
#             else:
#                 print('  wrong trial : ' + w_f_currIMG +
#                       ', corr_loc - ' + str(coordi_c_row) + ', ' + str(coordi_c_col) +
#                       ', wrong_loc - ' + str(coordi_w_row) + ', ' + str(coordi_w_col))
#
    # select wrong location and avoid spatial contiguity
    need_select = 1 # 0 = no, 1 = yes (default, it needs for the first entering)
    while need_select == 1:

        loca_p_thisrun = random.sample(PLACEs_mat, loca_n_2select)
        need_select = 0 # done once

        # checking then
        for wi in range(0,len(loca_p_thisrun)):
            w_p_currIMG = V_w_PLACEsID_all[(rr-1)*24+wi]
            w_p_loca = loca_p_thisrun[wi]
            c_p_loca = PLACEs_mat[PLACEs_c_rem.index(w_p_currIMG)]

            coordi_w_col = int(math.floor(w_p_loca/7)+1)
            coordi_w_row = int((w_p_loca % 7)+1)
            coordi_c_col = int(math.floor(c_p_loca/7)+1)
            coordi_c_row = int((c_p_loca % 7)+1)

            if ((coordi_w_col-coordi_c_col)**2+(coordi_w_row-coordi_c_row)**2)**0.5 <= 2**0.5:
                print('Oops, got one location for wrong image assigned attached with its correct location.')
                print('FAILED selection - ' + ' wrong trial : ' + w_p_currIMG +
                  ', corr_loc - ' + str(coordi_c_row) + ', ' + str(coordi_c_col) +
                  ', wrong_loc - ' + str(coordi_w_row) + ', ' + str(coordi_w_col))
                need_select = 1 # do one more, because not satisfied
                break
#             else:
#                 print('  wrong trial : ' + w_p_currIMG +
#                       ', corr_loc - ' + str(coordi_c_row) + ', ' + str(coordi_c_col) +
#                       ', wrong_loc - ' + str(coordi_w_row) + ', ' + str(coordi_w_col))

    if rr == repeat_runs : # last run, left with a few to select
        V_w_FACEsLoc[-loc_n_lastrun:] = loca_f_thisrun
        V_w_PLACEsLoc[-loc_n_lastrun:] = loca_p_thisrun
    else:
        item_head = (rr-1)*24+0
        item_tail = (rr-1)*24+loca_n_2select
        V_w_FACEsLoc[item_head:item_tail] = loca_f_thisrun
        V_w_PLACEsLoc[item_head:item_tail] = loca_p_thisrun

step_ID2fill_in1blk = trials_n/2-correct_first_n
step_loc2fill_in1blk = (n_w_trials)/2

for blk in range(0,blk_n):

    v_imgID = V_imgID[blk]
    v_CorW = ['c'] * int(trials_n*ratio_correct) + ['w'] * (trials_n-int(trials_n*ratio_correct))
    v_ForP = ['f','p'] * int(trials_n/2)
    v_TR_ITI = [2,2,3,3,4,4] * int(trials_n/6)


    # fill in wrong images ID, also may complete some un-filled correct images ID too, if needed
    v_imgID[correct_first_n*2:trials_n:2] = V_w_FACEsID_all[int(blk*step_ID2fill_in1blk):int((blk+1)*step_ID2fill_in1blk)]
    v_imgID[correct_first_n*2+1:trials_n:2] = V_w_PLACEsID_all[int(blk*step_ID2fill_in1blk):int((blk+1)*step_ID2fill_in1blk)]

    # fix the remainder, if correct_first_n < 18;
    step_cID2fill_remain = int(ratio_correct*trials_n/2-correct_first_n)
    if correct_first_n < ratio_correct*trials_n/2:
        v_imgID[correct_first_n*2:int(ratio_correct*trials_n):2] = V_c_FACEsID[int(blk*step_cID2fill_remain):int((blk+1)*step_cID2fill_remain)]
        v_imgID[correct_first_n*2+1:int(ratio_correct*trials_n):2] = V_c_PLACEsID[int(blk*step_cID2fill_remain):int((blk+1)*step_cID2fill_remain)]

    # assign the locations, first for the correct ones; for the wrong trials, will do later
    v_Loca = [-1] * trials_n

    for ll in range(0,int(trials_n*ratio_correct)):
        if v_CorW[ll]=='c':
            if v_ForP[ll]=='f':
                v_Loca[ll] = FACEs_mat[FACEs_c_rem.index(v_imgID[ll])]
            elif v_ForP[ll]=='p':
                v_Loca[ll] = PLACEs_mat[PLACEs_c_rem.index(v_imgID[ll])]

    v_Loca[int(trials_n*ratio_correct):trials_n:2] = V_w_FACEsLoc[int(blk*step_loc2fill_in1blk):int((blk+1)*step_loc2fill_in1blk)]
    v_Loca[int(trials_n*ratio_correct)+1:trials_n:2] = V_w_PLACEsLoc[int(blk*step_loc2fill_in1blk):int((blk+1)*step_loc2fill_in1blk)]

    # test and shuffle for same-image and/or same-location contiguity
    need_shuffle = 1 # 0 = no, 1 = yes (default, it needs for the first entering)
    v_5comb = list(zip(v_imgID, v_CorW, v_ForP, v_TR_ITI, v_Loca)) # shuffle together
    while need_shuffle == 1:

        random.shuffle(v_5comb)
        need_shuffle = 0 # done once

        # checking first
        for img in range(1,trials_n):
            if v_5comb[img][0] == v_5comb[img-1][0] or v_5comb[img][4] == v_5comb[img-1][4]: # either if the image ID, or the presentation location is the same, re-shuffling is needed
                print('Oops, got one pair of consecutive trials assigned with the same image or location.')
                need_shuffle = 1 # do one more, because not satisfied
                break
            else:
                if img == trials_n-1:
                    print('Good, presentation order for block ' + str(blk+1) + ' is solid now!')

    v_imgID, v_CorW, v_ForP, v_TR_ITI, v_Loca = zip(*v_5comb)


    V_imgID[blk] = v_imgID
    V_CorW[blk] = v_CorW
    V_ForP[blk] = v_ForP
    V_TR_ITI[blk] = v_TR_ITI
    V_Loca[blk] = v_Loca

print(V_imgID)
import numpy as np
print(np.shape(V_imgID))
print(V_CorW)
print(V_ForP)
print(V_TR_ITI)
print(V_Loca)

# CONVERT RESULTS
presentationOrder = [None] * mvpa_number_blocks
for n_block in range(mvpa_number_blocks):
    V_Loca[n_block] = np.array(V_Loca[n_block], dtype=int)
    V_CorW[n_block] = np.array([0 if element == 'c' else 1 if element == 'w' else [] for element in V_CorW[n_block]],
                               dtype=int)
    V_TR_ITI[n_block] = np.array(V_TR_ITI[n_block], dtype=int)
    presentationOrder[n_block] = np.array([V_Loca[n_block], V_CorW[n_block], V_TR_ITI[n_block], V_imgID[n_block]],
                                          dtype=object)

# SAVE RESULTS

session = experiment_session[experimentName]
session_dir = os.path.normpath(os.path.join('sourcedata', 'sub-' + subjectName, 'ses-' + session))
output_dir = os.path.normpath(os.path.join(session_dir, 'beh'))
if not os.path.isdir(session_dir):
    os.mkdir(session_dir)
io.defaults.datafile_directory = output_dir
io.defaults.eventfile_directory = output_dir

control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=True)
exp = design.Experiment(experimentName)  # Save experiment name
control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

bids_datafile, bids_eventfile = rename_output_files_to_BIDS(subjectName, session, experimentName,
                                                            io.defaults.datafile_directory,
                                                            io.defaults.eventfile_directory)
exp.data.rename(bids_datafile)
exp.events.rename(bids_eventfile)

exp.add_experiment_info('Subject: ')
exp.add_experiment_info(subjectName)
exp.add_experiment_info('Learning: ')
exp.add_experiment_info(str(learningMatrix))
exp.add_experiment_info('PresentationOrder')
exp.add_experiment_info(str(presentationOrder))
exp.add_experiment_info('PresentationOrderEndOf')
exp.add_experiment_info('over')
# exp.add_experiment_info('RandomMatrix')
# exp.add_experiment_info(str(randomMatrix))

control.end()

