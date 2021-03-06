#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2018:
#   Matthieu Estrada, ttamalfor@gmail.com
#
# This file is part of (AlignakApp).
#
# (AlignakApp) is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# (AlignakApp) is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with (AlignakApp).  If not, see <http://www.gnu.org/licenses/>.

"""
    Frames
    ++++++
    Frames manage global QFrames for Alignak-app
"""


from logging import getLogger

from PyQt5.Qt import QFrame

logger = getLogger(__name__)


def get_frame_separator(vertical=False):
    """
    Return a frame separator

    :param vertical: define if separator is vertical or horizontal
    :type vertical: bool
    :return: frame separator
    :rtype: QFrame
    """

    line = QFrame()
    if vertical:
        line.setObjectName('vseparator')
        line.setFrameShape(QFrame.VLine)
    else:
        line.setObjectName('hseparator')
        line.setFrameShape(QFrame.HLine)

    return line
