import numpy as np
import subprocess
from expyriment.stimuli import Circle, Rectangle
from expyriment.misc import constants
from playsound import playsound

from ld_card import LdCard
from config import cardSize, linesThickness, cueCardColor, matrixTemplate, listPictures, removeCards, dotColor, bgColor
from config import numberClasses, picturesFolder, classPictures
from config import sounds, soundsFolder, tempSounds

class LdMatrix(object):
    def __init__(self, size, windowSize):
        self._windowSize = windowSize
        self._size = size
        self._threshold = 0
        self._isFill = False
        self._isValid = False
        self._gap = None
        self._cueCard = None
        self._matrix = np.ndarray(shape=self._size, dtype=object)
        self._listPictures = []
        self._rowGap = 0
        self._columnGap = 0
        self._category = None

        self.populate()  # Populate with cards
        self.isValidMatrix()  # Check Matrix validity
        self.setPositions()  # Set cards positions

    def populate(self):

        for nCard in range(self._matrix.size):
                self._matrix.itemset(nCard, LdCard(cardSize))

        self._cueCard = LdCard(cardSize, cueCardColor)

    def isValidMatrix(self):
        spaceRowLeft = self.windowSize[0] - (self.size[0] * self._matrix.item(0).size[0])
        spaceColumnLeft = self.windowSize[1] - ((self.size[1] + 2) * self._matrix.item(0).size[1]) - 2 * linesThickness

        spaceRowLeftPerGap = spaceRowLeft/(self.size[0] + 1)
        spaceColumnLeftPerGap = spaceColumnLeft/(self.size[1] + 1 + 4)  # 4: gaps top and bottom

        self._gap = min(spaceColumnLeftPerGap, spaceRowLeftPerGap)

        if self._gap > self._threshold:
            self._isValid = True
            return self._isValid
        else:
            print('This matrix is not Valid')
            import sys
            sys.exit()


    def scale(self):
        for nCard in range(self._matrix.size):
            self._matrix.item(nCard).stimuli[0].scale(self._matrix.item(nCard).size[0]/float(300))

    def setPositions(self):

        if self._isValid:
            sizeRows = self._matrix.item(0).size[0]  # Size of a card
            sizeColumns = self._matrix.item(0).size[1]  # Size of a card

            rowGap = (self.windowSize[0] - (self.size[0] * sizeRows + (self.size[0] - 1) * self.gap))/2
            columnGap = (self.windowSize[1] - (self.size[1] * sizeColumns + (self.size[1] - 1) * self.gap))/2  # Validated

            self._rowGap = rowGap  # Save Row Gap
            self._columnGap = columnGap  # Save Column Gap

            iCard = 0  # Loop over cards

            for iRow in range(self._size[0]):
                for iColumn in range(self._size[1]):
                    rowPosition = -self._windowSize[0]/2 + rowGap + self.gap * iRow + iRow * sizeRows + sizeRows/2
                    columnPosition = self._windowSize[1]/2 - (columnGap + self.gap * iColumn + iColumn*sizeColumns + sizeColumns/2)
                    self._matrix.item(iCard).position = (rowPosition, columnPosition)
                    self._matrix.item(iCard).stimuli[0].reposition(self._matrix.item(iCard).position)
                    self._matrix.item(iCard).stimuli[1].reposition(self._matrix.item(iCard).position)
                    iCard += 1

            self._cueCard.position = (0, self._windowSize[1]/float(2) - self.gap - sizeRows/float(2.0))
            self._cueCard.stimuli[0].reposition(self._cueCard.position)
            self._cueCard.stimuli[1].reposition(self._cueCard.position)
        else:
            print('Matrix is not valid')

    def associateCategory(self, category):
        self._category = category

    def changeCueCardPosition(self, position):
        sizeRows = self._matrix.item(0).size[0]  # Size of a card
        self._cueCard.position = position

    def plotCueCard(self, showPicture, bs, draw=False):  # Plot cue Card
        if showPicture is True:
            self._cueCard.stimuli[0].plot(bs)
        else:
            self._cueCard.stimuli[1].plot(bs)
        if draw:
            bs.present(False, True)
        else:
            return bs

    def plotCard(self, nCard, showPicture, bs, draw=False):  # Plot specific card
        if showPicture is True:
            self._matrix.item(nCard).stimuli[0].plot(bs)
        else:
            self._matrix.item(nCard).stimuli[1].plot(bs)

        if draw:
            bs.present(False, True)
        else:
            return bs

    def returnPicture(self, nCard):
        return self._matrix.item(nCard).picture

    def playSound(self, soundsAllocation_index, volumeAdjusted = False):
        if volumeAdjusted:
            command = 'ffplay -nodisp -loglevel quiet -autoexit ' + soundsFolder +\
                      tempSounds[soundsAllocation_index[self._category]]
            subprocess.call(command)
        else:
            command = 'ffplay -nodisp -loglevel quiet -autoexit ' + soundsFolder +\
                      sounds[soundsAllocation_index[self._category]]
            subprocess.call(command)

    def playCueSound(self, volumeAdjusted = False):
        if volumeAdjusted:
            command = 'ffplay -nodisp -loglevel quiet -autoexit ' + soundsFolder + \
                      tempSounds[self._cueCard.sound]
            subprocess.call(command)
        else:
            command = 'ffplay -nodisp -loglevel quiet -autoexit ' + soundsFolder + \
                      sounds[self._cueCard.sound]
            subprocess.call(command)

    def plotDefault(self, bs, draw=False):
        for nCard in range(self._matrix.size):
            if nCard in removeCards:
                 self._matrix.item(nCard).color = bgColor

            bs = self.plotCard(nCard, False, bs)

        bs = self.plotCueCard(False, bs)

        if (self.size[0] % 2 == 0) and (self.size[1] % 2 == 0):
            centerDot = Circle(self.gap/2, colour=dotColor, position=(0, 0))
            centerDot.plot(bs)
        elif (self.size[0] % 2 == 1) and (self.size[1] % 2 == 1):
            centerSquare = Rectangle(cardSize, colour=constants.C_WHITE, position=(0, 0))
            centerSquare.plot(bs)

        if draw:
            bs.present(False, True)
        else:
            return bs

    def findMatrix(self, category, previousMatrix=None, keep=False):

        newMatrix = []

        if previousMatrix is None:   # New Matrix
            pictures = list(listPictures[category])
            for itemMatrix in range(self._size[0]*self._size[1]):
                randomIndex = np.random.randint(0, len(pictures))
                newMatrix.append(pictures[randomIndex])
                pictures.remove(pictures[randomIndex])
        elif keep:  # Keep previous Matrix
            previousMatrix = np.asarray(previousMatrix)
            newMatrix = previousMatrix
        else:    # New Matrix different from previous matrix
            newMatrix = previousMatrix
            while np.any(newMatrix == previousMatrix):
                newMatrix = []
                perm = np.random.permutation(numberClasses)
                newClassesPictures = np.asarray(listPictures)[perm]
                newClassesPictures = np.ndarray.tolist(newClassesPictures)
                for itemMatrix in matrixTemplate:
                    currentClass = newClassesPictures[itemMatrix]
                    randomIndex = np.random.randint(0, len(currentClass))
                    newMatrix.append(currentClass[randomIndex])
                    newClassesPictures[itemMatrix].remove(currentClass[randomIndex])

        return newMatrix

    def associatePictures(self, newMatrix, picturesFolder):
        nPict = 0
        for nCard in range(self._matrix.size):
            if nCard not in removeCards:
                self._matrix.item(nCard).setPicture(picturesFolder + newMatrix[nPict], False, picture=newMatrix[nPict])
                self._matrix.item(nCard).stimuli[0].scale(self._matrix.item(nCard).size[0]/float(300))
                self._listPictures.append(newMatrix[nPict])
                nPict += 1

    def newRecognitionMatrix(self, previousMatrix):
        # dummyMatrix is a matrix the size of previousMatrix that stores only the pictures category under 0,1,2 int format
        # 0 = first category (often a images), 1 = second category (often b), etc.
        dummyMatrix = [None] * len(previousMatrix)
        for i in range(len(previousMatrix)):
            for j in range(len(classPictures)):
                if classPictures[j] in previousMatrix[i]:
                    dummyMatrix[i] = j

        # Shifting categories
        perm = np.random.permutation(3).tolist()  # WARNING: PARAMETER HARD CODED
        while any(perm[i] == range(3)[i] for i in range(3)):  # WARNING: PARAMETER HARD CODED
            perm = np.random.permutation(3).tolist()  # WARNING: PARAMETER HARD CODED
        dummyMatrix = [perm[i] for i in dummyMatrix]

        # copying class Pictures to a different object
        tempListPictures = list(listPictures)

        currentCategoryIndex = [0] * len(tempListPictures)

        # Filling matrix with images
        newMatrix = [0] * len(previousMatrix)
        for i in range(len(previousMatrix)):
            category = dummyMatrix[i]
            newMatrix[i] = tempListPictures[category][currentCategoryIndex[dummyMatrix[i]]]
            currentCategoryIndex[category] += 1

        return newMatrix

    def associateSounds(self, newMatrix, soundsAllocation):
        nPict = 0
        for nCard in range(self._matrix.size):
            if nCard not in removeCards:
                picture = newMatrix[nPict].rstrip('.png')
                for i in range(numberClasses):
                    if classPictures[i] in picture:  # if card belongs to the the i-th class of pictures
                        # associate this class' sound to the card
                        self._matrix.item(nCard).setSound(soundsAllocation[i])
                nPict += 1

    def checkPosition(self, position):
        for nCard in range(self._matrix.size):
            if nCard not in removeCards:
                if self._matrix.item(nCard).stimuli[1].overlapping_with_position(position):
                    return nCard

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._matrix = np.ndarray(shape=value, dtype=np.object)
        self._size = value

    @property
    def gap(self):
        return self._gap

    @property
    def windowSize(self):
        return self._windowSize

    @property
    def listPictures(self):
        return self._listPictures