from expyriment import stimuli, control, design, io, misc

from declarativeTask3.config import windowMode, windowSize, restBGColor, restCrossColor, restCrossSize, restCrossThickness

control.defaults.window_mode = windowMode
control.defaults.window_size = windowSize

exp = design.Experiment('Rest')  # Save experiment name
control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)
bs = stimuli.BlankScreen(restBGColor)  # Create blank screen
cross = stimuli.FixCross(size=restCrossSize, colour=restCrossColor, line_width=restCrossThickness)  # Create cross
cross.plot(bs)
kb=io.Keyboard()
bs.present()


kb.wait(keys=misc.constants.K_q)