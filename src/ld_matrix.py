import random
import numpy as np
import subprocess
from expyriment.stimuli import Shape, FixCross, TextLine, Rectangle
from expyriment.misc import constants, geometry
from playsound import playsound
from math import ceil

from ld_card import LdCard
from config import cardSize, linesThickness, cueCardColor, matrixTemplate, listPictures, removeCards, dotColor, bgColor
from config import numberClasses, classPictures, picturesFolderClass, picturesFolder, cardColor, textSize, textColor

# from config import sounds, soundsFolder, tempSounds
from config import feedback_frame_correct_color, feedback_frame_wrong_color, templatePicture, fixation_cross_thickness
from ld_utils import vertices_frame


class LdMatrix(object):
    def __init__(self, size, windowSize, override_remove_cards=None, recognition_bigger_cuecard=False):
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
        self._cross = None
        self._recognition_bigger_cuecard = recognition_bigger_cuecard

        self.populate()  # Populate with cards
        self.isValidMatrix()  # Check Matrix validity
        self.setPositions()  # Set cards positions

    def populate(self):

        for nCard in range(self._matrix.size):
            self._matrix.itemset(nCard, LdCard(cardSize))

        self._cueCard = LdCard(cardSize, bgColor)
        self._cross = FixCross(size=(cardSize[0]/2, cardSize[1]/2), colour=cardColor,
                               line_width=fixation_cross_thickness)

    def isValidMatrix(self):
        # spaceRowLeft = window width (windowscreen x dimension, integer, number of pixels) - \
        # matrix X size (an integer, the number of cards per row) * card x dimension (integer, number of pixels)
        spaceRowLeft = self.windowSize[0] - (self.size[0] * self._matrix.item(0).size[0])
        spaceColumnLeft = self.windowSize[1] - (self.size[1] * self._matrix.item(0).size[1]) - 2 * linesThickness

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

            cue_row_position = -self._windowSize[0] / 2 + rowGap + self.gap * 3 + 3 * sizeRows + sizeRows / 2
            cue_column_position = self._windowSize[1] / 2 - (
                        columnGap + self.gap * 3 + 3 * sizeColumns + sizeColumns / 2)

            if self._recognition_bigger_cuecard:
                self._cueCard = LdCard((cardSize[0]+self.gap/2, cardSize[1]+self.gap/2), bgColor)

            self._cueCard.position = (cue_row_position, cue_column_position)
            self._cueCard.stimuli[0].reposition(self._cueCard.position)
            self._cueCard.stimuli[1].reposition(self._cueCard.position)

            fix_cross_row_position = -self._windowSize[0] / 2 + rowGap + self.gap * 3 + 3 * sizeRows + sizeRows / 2
            fix_cross_column_position = self._windowSize[1] / 2 - (
                    columnGap + self.gap * 3 + 3 * sizeColumns + sizeColumns / 2)

            self._cross.reposition((fix_cross_row_position, fix_cross_column_position))
        else:
            print('Matrix is not valid')

    def plot_instructions_rectangle(self, bs, instructions_card, draw=True):
        x_length = len(instructions_card)*cardSize[0] + (len(instructions_card)+1) * self.gap
        position = (0, None)

        # taking the lowest possible x coordinate
        for card_index in instructions_card:
            if position[1] is None:
                position = (0, self._matrix.item(card_index).position[1])
            elif position[1] < self._matrix.item(card_index).position[1]:
                position = (0, self._matrix.item(card_index).position[1])
        position = (position[0], position[1])

        instruction_rectangle = Rectangle(size=(x_length, self.gap * 2 + cardSize[1]), position=position, colour=constants.C_DARKGREY)

        instruction_rectangle.plot(bs)

        if draw:
            bs.present(False, True)
        else:
            return bs

    def plot_instructions(self, bs, instructions_card, instructions_text, draw=True):
        x_length = len(instructions_card)*cardSize[0] + (len(instructions_card)-1) * self.gap+10
        position = (0, None)

        # taking the lowest possible x coordinate
        for card_index in instructions_card:
            if position[1] is None:
                position = (0, self._matrix.item(card_index).position[1])
            elif position[1] < self._matrix.item(card_index).position[1]:
                position = (0, self._matrix.item(card_index).position[1])

        instructions = TextLine(instructions_text, position=position,
                                text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                text_underline=None, text_colour=textColor,
                                background_colour=bgColor, max_width=None)

        instructions.plot(bs)

        if draw:
            bs.present(False, True)
        else:
            return bs

    def plot_instructions_card(self, bs, instructions_card, draw=True):
        for card_index in instructions_card:
            bs = self.plotCard(card_index, False, bs)

        if draw:
            bs.present(False, True)
        else:
            return bs
        return None

    def plotCueCard(self, showPicture, bs, draw=False, nocross=False):  # Plot cue Card
        if showPicture is True:
            self._cueCard.stimuli[0].plot(bs)
        elif nocross:
            self._cueCard.color = bgColor
            self._cueCard.stimuli[1].plot(bs)
        else:
            self._cueCard.color = bgColor
            self._cueCard.stimuli[1].plot(bs)
            self._cross.plot(bs)
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
        # edit: plotting fixation cross instead of plotting all cards, therefore not plotting removeCards
        for nCard in range(self._matrix.size):
            # if not show_matrix:
            if nCard in removeCards or not show_matrix:
                self._matrix.item(nCard).color = bgColor
            else:
                self._matrix.item(nCard).color = cardColor

            bs = self.plotCard(nCard, False, bs)

        bs = self.plotCueCard(False, bs)

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

        geometry.vertices_frame(size=(105, 105), frame_thickness=5)
        response_stimuli = Shape(position=position,
                                 vertex_list=geometry.vertices_frame(size=(105, 105), frame_thickness=5),
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