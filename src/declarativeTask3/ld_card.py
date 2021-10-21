from expyriment import stimuli
from expyriment.misc import constants

from declarativeTask3.config import templatePicture, cardColor


class LdCard(object):
    def __init__(self, size, color=cardColor):
        self._size = size
        self._stimuli = (stimuli.Picture(templatePicture, position=None),
                         stimuli.Rectangle(size, colour=color, line_width=None, position=None))
        self._picture = None  # the picture's name, e.g. 'a001.png'
        self._sound = None

    @property
    def stimuli(self):
        return self._stimuli

    @property
    def sound(self):
        return self._sound

    @property
    def size(self):
        return self._size

    @property
    def position(self):
        return self._position

    @property
    def color(self):
        return self._stimuli[1].colour

    @property
    def picture(self):
        return self._picture

    @position.setter
    def position(self, value):
        self._position = value
        self._stimuli[0].reposition(value)
        self._stimuli[1].reposition(value)

    @color.setter
    def color(self, value):
        self._stimuli = (
        self.stimuli[0], stimuli.Rectangle(self.size, colour=value, line_width=None, position=self.position))

    def setPicture(self, value, scale=True, picture=None):
        self._stimuli = (stimuli.Picture(value, position=self.position),
                         stimuli.Rectangle(self.size, colour=constants.C_WHITE, line_width=None,
                                           position=self.position))
        self._picture = picture
        if scale:
            self._stimuli[0].scale(self.size[0]/float(300))

    def setSound(self, number):
        self._sound = number
