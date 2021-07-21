import glob
import os
# from math import ceil
from expyriment.misc import constants

rawFolder = os.getcwd() + os.path.sep

picturesFolder = rawFolder + 'stimulis' + os.path.sep
picturesExamplesFolder = rawFolder + 'stimulisExample' + os.path.sep
dataFolder = rawFolder + 'data' + os.path.sep

mouseButton = 1

windowMode = False  # if False use FullScreen
windowSize = (1024, 768)  # if windowMode is True then use windowSize

picturesExamples = ['triangle.png', 'square.png', 'circle.png']
sounds = ['shortest-1-100ms.wav', 'shortest-2-100ms.wav', 'shortest-3-100ms.wav']
tempSounds = ['sound' + str(i) + '.wav' for i in range(len(sounds))]

templatePicture = picturesFolder + 'class-faces' + os.path.sep + 'class-hf' + os.path.sep + 'hf001.png'

linesThickness = 0
colorLine = (0, 0, 0)  # expyriment.misc.constants.C_BLACK

cueCardColor = (255, 255, 255)   # expyriment.misc.constants.C_WHITE
cardColor = (255, 255, 255)  # expyriment.misc.constants.C_WHITE

clickColor = (200, 200, 200)
restBGColor = (0, 0, 0)  # expyriment.misc.constants.C_BLACK
restCrossColor = (255, 255, 255)  # expyriment.misc.constants.C_WHITE
restCrossSize = (100, 100)
restCrossThickness = 20
dotColor = (0, 0, 0)  # expyriment.misc.constants.C_BLACK
bgColor = (150, 150, 150)
textColor = (0, 0, 0)  # expyriment.misc.constants.C_BLACK


textSize = 50
matrixSize = (7, 7)
cardSize = (80, 80)

''' Circles '''

startSpace = cardSize[1] + 20

nbBlocksMax = 10

presentationCard = 2000

responseTime = 5000
AssociationResponseTime = 10000
shortRest = 2500
thankYouRest = 5000
restPeriod = 15000
clicPeriod = 200

min_max_ISI = [500, 1500]  # [min, max] inter_stimulus interval

##

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


arrow = ("xX                      ",
         "X.X                     ",
         "X..X                    ",
         "X...X                   ",
         "X....X                  ",
         "X.....X                 ",
         "X......X                ",
         "X.......X               ",
         "X........X              ",
         "X.........X             ",
         "X......XXXXX            ",
         "X...X..X                ",
         "X..XX..X                ",
         "X.X XX..X               ",
         "XX   X..X               ",
         "X     X..X              ",
         "      X..X              ",
         "       X..X             ",
         "       X..X             ",
         "        XX              ",
         "                        ",
         "                        ",
         "                        ",
         "                        ")

arrow1 = (' XX                                                                             ',
          ' XXXX                                                                           ',
          ' XX.XXX                                                                         ',
          ' XX...XXX                                                                       ',
          ' XX.....XXX                                                                     ',
          ' XX.......XXX                                                                   ',
          ' XX.........XXX                                                                 ',
          ' XX...........XXX                                                               ',
          ' XX.............XXX                                                             ',
          ' XX...............XXX                                                           ',
          ' XX.................XXX                                                         ',
          ' XX...............XXXX                                                          ',
          ' XX..............XX                                                             ',
          ' XX....  ......XX                                                               ',
          ' XX..XX......XX                                                                 ',
          ' XXX   XX......XX                                                               ',
          '        XX......XX                                                              ',
          '         XX......XX                                                             ',
          '          XX......XX                                                            ',
          '           XX......XX                                                           ',
          '            XX......XX                                                          ',
          '             XX......XX                                                         ',
          '              XX......XX                                                        ',
          '               XX......XX                                                       ',
          '                XX......XX                                                      ',
          '                 XXXXXXXXXX                                                     ',
          '                                                                                ',
          '                                                                                ',
          '                                                                                ',
          '                                                                                ',
          '                                                                                ',
          '                                                                                ')

if matrixSize == (4, 4):
    matrixTemplate = [0]*16
    removeCards = []
elif matrixSize == (5, 5):
    matrixTemplate = [2,0,2,1,1,1,1,0,2,0,2,2,0,1,2,1,2,2,0,0,0,1,0,1]
    removeCards = [12]
elif matrixSize == (6, 6):
    removeCards = []
    matrixTemplate = [0, 1, 1, 2, 0, 2,
                      2, 0, 0, 2, 1, 1,
                      1, 0, 2, 1, 2, 0,
                      0, 2, 1, 0, 1, 2,
                      1, 2, 1, 2, 0, 1,
                      0, 1, 0, 2, 2, 0]
elif matrixSize == (7, 7):
    matrixTemplate = [7, 0, 4, 3, 6, 1, 5,
                      3, 2, 6, 5, 0, 7, 2,
                      1, 5, 1, 2, 6, 4, 3,
                      4, 7, 0,    7, 0, 1,
                      6, 1, 3, 5, 4, 2, 4,
                      5, 0, 7, 2, 3, 5, 6,
                      2, 4, 3, 6, 1, 7, 0]
    # matrixTemplate = [matrixTemplate[i * 7:(i + 1) * 7] for i in range(7)]
    # matrixTemplate = np.array([np.array(matrixTemplate[0:(i + 1) * 7]) for i in range(7)])
    removeCards = [24]
    # removeCards = [index for index, category in enumerate(matrixTemplate) if category > 3]
    # if category > len(classPictures) /2
elif matrixSize == (5, 4):
    matrixTemplate = [0] * 20
    removeCards = []

# correctAnswersMax = int(ceil((matrixSize[0]*matrixSize[0] - len(removeCards))*7./10))
correctAnswersMax = 18
numberBlocksLearning = 10
numberBlocksSubUnit = 2
numberLearningSubUnits = 5
if numberBlocksSubUnit * numberLearningSubUnits != numberBlocksLearning:
    raise ValueError("""the number of blocks of learning is not equal to
    its number of subUnits * the number of blocks during a subUnit""")

classPictures = ['hf', 'hm', 'am', 'af', 'bc', 'bo', 'sc', 'so']
classPicturesAboveFolder = {'hf': 'class-faces', 'hm': 'class-faces', 'am': 'class-faces', 'af': 'class-faces',
                                   'bc': 'class-places', 'bo': 'class-places', 'sc': 'class-places', 'so': 'class-places'}
picturesFolderClass = {category: picturesFolder + classPicturesAboveFolder[category] + os.path.sep +
                                 'class-' + category + os.path.sep for category in classPictures}
# one category (as we'll later rename (refactor) classes) should always be a single lowercase letter
numberClasses = len(classPictures)
# The setting below allows the experimenter to prevent a learned matrix (currentCorrectAnswers > correctAnswersMax)
# from appearing again during the Encoding Phase. In other words, as soon as this matrix is learned, during the encoding
# phase, it won't appear again, during the encoding phase, again. The Encoding phase will continue, using only unlearned
# matrices during the Encoding phase
ignore_learned_matrices = False

listPictures = {}
for classPicture in classPictures:
    listPictures[classPicture] =\
        glob.glob(picturesFolderClass[classPicture] + classPicture + '*[0-9][0-9][0-9].png')

for category in classPictures:
    listPictures[category] = [p.replace(picturesFolderClass[category], '') for p in listPictures[category]]

feedback_frame_correct_color = constants.C_GREEN
feedback_frame_wrong_color = constants.C_RED
feedback_time = 1000
inter_feedback_delay_time = 1000
choose_location_minimum_response_time = 3000

debug = False

supported_start_by_choices = ['start_with_faces', 'start_with_places']
experiment_use_faces_or_places = {
    # start with faces
    'start_with_faces':
        {'PreLearn':    'faces',
         'PreTest':     'faces',
         'PostTest1':   'faces',
         'PostRecog1':  'faces',
         'PostTest2: ': 'faces',
         'PostRecog2':  'faces',
         'PostLearn':   'places'},
    # start with places
    'start_with_places':
        {'PreLearn':    'places',
         'PreTest':     'places',
         'PostTest1':   'places',
         'PostRecog1':  'places',
         'PostTest2: ': 'places',
         'PostRecog2':  'places',
         'PostLearn':   'faces'}
}
