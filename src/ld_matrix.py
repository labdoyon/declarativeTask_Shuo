import random
import numpy as np
import subprocess
from expyriment.stimuli import Circle, Rectangle, Shape
from expyriment.misc import constants, geometry
from playsound import playsound
from math import ceil

from ld_card import LdCard
from config import cardSize, linesThickness, cueCardColor, matrixTemplate, listPictures, removeCards, dotColor, bgColor
from config import numberClasses, classPictures, picturesFolderClass, picturesFolder
# from config import sounds, soundsFolder, tempSounds
from config import feedback_frame_correct_color, feedback_frame_wrong_color, templatePicture
from ld_utils import vertices_frame

class LdMatrix(object):
    def __init__(self, size, windowSize, override_remove_cards=None):
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
        self._override_remove_cards = override_remove_cards

        self.populate()  # Populate with cards
        self.isValidMatrix()  # Check Matrix validity
        self.setPositions()  # Set cards positions

    def populate(self):

        for nCard in range(self._matrix.size):
            self._matrix.itemset(nCard, LdCard(cardSize))

        self._cueCard = LdCard(cardSize, cueCardColor)

    def isValidMatrix(self):
        # spaceRowLeft = window width (windowscreen x dimension, integer, number of pixels) - \
        # matrix X size (an integer, the number of cards per row) * card x dimension (integer, number of pixels)
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

            cueRowPosition = -self._windowSize[0] / 2 + rowGap + self.gap * 3 + 3 * sizeRows + sizeRows / 2
            cueColumnPosition = self._windowSize[1] / 2 - (
                        columnGap + self.gap * 3 + 3 * sizeColumns + sizeColumns / 2)

            self._cueCard.position = (cueRowPosition, cueColumnPosition)
            self._cueCard.stimuli[0].reposition(self._cueCard.position)
            self._cueCard.stimuli[1].reposition(self._cueCard.position)
        else:
            print('Matrix is not valid')

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

    def plotDefault(self, bs, draw=False, show_matrix=True):
        # We plot all cards, even if they are in removeCards, as the matrix should appear complete and regular.
        for nCard in range(self._matrix.size):
            # if nCard in removeCards or not show_matrix:
            if not show_matrix:
                self._matrix.item(nCard).color = bgColor

            bs = self.plotCard(nCard, False, bs)

        bs = self.plotCueCard(False, bs)

        if (self.size[0] % 2 == 0) and (self.size[1] % 2 == 0):
            if show_matrix:
                local_color = dotColor
            else:
                local_color = bgColor
            centerDot = Circle(self.gap/2, colour=local_color, position=(0, 0))
            centerDot.plot(bs)
        elif (self.size[0] % 2 == 1) and (self.size[1] % 2 == 1):
            if show_matrix:
                local_color = constants.C_WHITE
            else:
                local_color = bgColor
            centerSquare = Rectangle(cardSize, colour=local_color, position=(0, 0))
            centerSquare.plot(bs)

        # Show black vertices around cue card in the middle of the screen:
        if show_matrix:
            cue_card_surrounding_vertices = Shape(position=self._cueCard.position,
                                                  vertex_list=vertices_frame(size=(100, 100), frame_thickness=10),
                                                  colour=constants.C_BLACK)
        else:
            cue_card_surrounding_vertices = Shape(position=self._cueCard.position,
                                                  vertex_list=vertices_frame(size=(100, 100), frame_thickness=10),
                                                  colour=bgColor)
        cue_card_surrounding_vertices.plot(bs)

        if draw:
            bs.present(False, True)
        else:
            return bs

    def findMatrix(self, previousMatrix=None, keep=False):

        newMatrix = []
        # This means faces will always be in the the squares spots allocated to faces. Faces images will be shuffled
        # within spaces allocated to faces. Same for places
        faces_categories = list(range(ceil(numberClasses/2)))
        building_categories = list(range(ceil(numberClasses/2), numberClasses))
        perm = np.hstack((np.random.permutation(faces_categories), np.random.permutation(building_categories)))
        newListPictures = []
        for category in classPictures:
            newListPictures.append(listPictures[category])
        newClassesPictures = np.asarray(newListPictures)[perm]
        newClassesPictures = np.ndarray.tolist(newClassesPictures)
        if previousMatrix is None:   # New Matrix
            for itemMatrix in matrixTemplate:
                currentClass = newClassesPictures[itemMatrix]
                randomIndex = np.random.randint(0, len(currentClass))
                newMatrix.append(currentClass[randomIndex])
                newClassesPictures[itemMatrix].remove(currentClass[randomIndex])
                # else:
                #     newMatrix.append(None)
        elif keep:  # Keep previous Matrix
            previousMatrix = np.asarray(previousMatrix)
            newMatrix = list(previousMatrix)
        else:    # New Matrix different from previous matrix
            newMatrix = previousMatrix
            while np.any(newMatrix == previousMatrix):
                newMatrix = []
                perm = np.random.permutation(numberClasses)
                newClassesPictures = np.asarray(newListPictures)[perm]
                newClassesPictures = np.ndarray.tolist(newClassesPictures)
                for itemMatrix in matrixTemplate:
                    currentClass = newClassesPictures[itemMatrix]
                    randomIndex = np.random.randint(0, len(currentClass))
                    newMatrix.append(currentClass[randomIndex])
                    newClassesPictures[itemMatrix].remove(currentClass[randomIndex])

        return newMatrix

    def associatePictures(self, newMatrix):
        nPict = 0
        if self._override_remove_cards is not None:
            removeCards = self._override_remove_cards
        else:
            from config import removeCards
        for nCard in range(self._matrix.size):
            if nCard not in removeCards:  # and nPict < 24:
                if newMatrix[nPict][:2] in classPictures:
                    self._matrix.item(nCard).setPicture(
                        picturesFolderClass[newMatrix[nPict][:2]] + newMatrix[nPict], False, picture=newMatrix[nPict])
                else:
                    self._matrix.item(nCard).setPicture(
                        templatePicture, False, picture=newMatrix[nPict])
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
        # perm = np.random.permutation(numberClasses).tolist()
        faces_categories = list(range(ceil(numberClasses / 2)))
        building_categories = list(range(ceil(numberClasses / 2), numberClasses))
        perm = np.hstack((np.random.permutation(faces_categories), np.random.permutation(building_categories))).tolist()
        while any(perm[i] == range(numberClasses)[i] for i in range(numberClasses)):
            perm = np.hstack(
                (np.random.permutation(faces_categories), np.random.permutation(building_categories))).tolist()
        dummyMatrix = [perm[i] for i in dummyMatrix]

        # copying class Pictures to a different object
        tempListPictures = dict(listPictures)
        number_of_images_per_category = int(len(matrixTemplate)/numberClasses)
        CategoryIndexes = {key: list(range(number_of_images_per_category)) for key in listPictures.keys()}

        # Filling matrix with images
        newMatrix = [0] * len(previousMatrix)
        for i in range(len(previousMatrix)):
            category = classPictures[dummyMatrix[i]]
            category_image_index = random.choice(CategoryIndexes[category])
            newMatrix[i] = tempListPictures[category][category_image_index]
            CategoryIndexes[category].remove(category_image_index)

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

    def checkPosition(self, position, cue_card=False):
        if self._override_remove_cards is not None:
            removeCards = self._override_remove_cards
        if not cue_card:
            for nCard in range(self._matrix.size):
                # if nCard not in removeCards:
                if self._matrix.item(nCard).stimuli[1].overlapping_with_position(position):
                    return nCard
            return None
        else:
            for cuecard_index in range(len(classPictures)):
                if (self._cueCard[cuecard_index]).stimuli[1].overlapping_with_position(position):
                    return cuecard_index
            return None

    def response_feedback_stimuli_frame(self, bs, position, subject_correct, show_or_hide=True, draw=False,
                                        no_feedback=False):
        if show_or_hide:
            if not no_feedback:
                if subject_correct:
                    color = feedback_frame_correct_color
                else:
                    color = feedback_frame_wrong_color
            else:
                color = constants.C_BLACK
        else:
            color = bgColor

        geometry.vertices_frame(size=(100, 100), frame_thickness=10)
        response_stimuli = Shape(position=position,
                                 vertex_list=geometry.vertices_frame(size=(100, 100), frame_thickness=10),
                                 colour=color)

        response_stimuli.plot(bs)
        if draw:
            bs.present(False, True)
        else:
            return bs

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