import os
import sys

from time import time

from config import numberLearningSubUnits
from ld_utils import getPreviousState

argument = "".join(sys.argv[1:])

for i in range(numberLearningSubUnits):
    if i == 0:
        firstTime = str(time())
    else:
        arguments = argument.split(',')
        subjectName = arguments[1]
        if getPreviousState(subjectName, 0, 'DayOne-Learning'):
            break
    os.system("py src/ld_declarativeTask.py " + argument + ' ' + str(i) + ' ' + firstTime)
