import keyboard
import mouse
import sys
from ld_sound import *

########################################################################################################################
subject_name = ''.join(sys.argv[1:])
soundsVolumeAdjustmentIndB = [0] * len(sounds)

for i in range(len(sounds)):
    dontMoveOn = True
    firstPresentation = True
    while dontMoveOn:
        if firstPresentation:
            firstPresentation = False
            event_happened = True
        else:
            event_happened = False  # True if the user has pressed a key or clicked the mouse
            if mouse.is_pressed(button='left'):
                event_happened = True
                if soundsVolumeAdjustmentIndB[i] + 5 <= 0:
                    soundsVolumeAdjustmentIndB[i] += 5
            elif mouse.is_pressed(button='right'):
                event_happened = True
                soundsVolumeAdjustmentIndB[i] -= 5
            elif keyboard.is_pressed('q'):
                dontMoveOn = False
            elif keyboard.is_pressed('w'):
                event_happened = True
        if event_happened:
            print("it is now " + str(soundsVolumeAdjustmentIndB) + " dB")
            change_volume(i, volume_adjustment_db=soundsVolumeAdjustmentIndB[i])
            play_sound(i)
            present_options(i)

delete_temp_files()

# Saving sounds adjustment: (this script is supposed to be executed in src)
subject_file = 'soundsVolumeAdjustmentIndB_' + subject_name + '.pkl'

with open(dataFolder + subject_file, 'wb') as f:
    pickle.dump(soundsVolumeAdjustmentIndB, f)
