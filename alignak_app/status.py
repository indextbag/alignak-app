#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016:
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
    Status manage QWidget who display Alignak status.
"""

from logging import getLogger

import requests
# from requests import ConnectionError

from alignak_app import __application__
from alignak_app.utils import get_image_path, get_app_config

try:
    __import__('PyQt5')
    from PyQt5.QtWidgets import QApplication, QWidget  # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QGridLayout  # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QLabel  # pylint: disable=no-name-in-module
    from PyQt5.QtGui import QIcon, QPixmap  # pylint: disable=no-name-in-module
    from PyQt5.QtCore import Qt  # pylint: disable=no-name-in-module
except ImportError:  # pragma: no cover
    from PyQt4.Qt import QApplication, QWidget  # pylint: disable=import-error
    from PyQt4.Qt import QGridLayout  # pylint: disable=import-error
    from PyQt4.Qt import QLabel  # pylint: disable=import-error
    from PyQt4.QtGui import QIcon, QPixmap  # pylint: disable=import-error
    from PyQt4.QtCore import Qt  # pylint: disable=import-error

logger = getLogger(__name__)


class AlignakStatus(QWidget):
    """
        Class who create QWidget for Alignak status.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # General settings
        self.setWindowTitle(__application__ + ': Alignak-States')
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(425)
        self.setMinimumWidth(425)
        self.setWindowIcon(QIcon(get_image_path('icon')))
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        # Fields
        self.grid = None
        self.start = True
        self.daemons = [
            'poller',
            'receiver',
            'reactionner',
            'arbiter',
            'scheduler',
            'broker'
        ]
        self.ws_request = None
        self.daemons_labels = {}

    def show_at_start(self):
        """
        Show AlignakStatus on start

        """

        self.alignak_ws_request()

        if self.start \
                and get_app_config('Backend', 'web_service_status', boolean=True) \
                and self.ws_request:
            self.show()
        else:
            self.start = False

    def create_status(self):
        """
        Create grid layout for status QWidget

        """

        # Add Layout
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # Display daemons status or info windows
        if get_app_config('Backend', 'web_service_status', boolean=True):
            self.alignak_ws_request()
            if self.ws_request:

                self.create_daemons_labels()
                self.daemons_to_layout()
            else:
                self.web_service_info()

        self.show_at_start()

    def alignak_ws_request(self):
        """
        Request to get json data from alignak web service

        """

        try:
            self.ws_request = requests.get(
                get_app_config('Backend', 'web_service_url') + '/alignak_map'
            )
        except requests.ConnectionError as e:
            logger.error('Bad value in "web_service_url" option : ' + str(e))

    def create_daemons_labels(self):
        """
        Create QLabels and Pixmaps for each daemons

        """

        for daemon in self.daemons:
            # Initialize daemon category dict
            self.daemons_labels[daemon] = {}

            # Get json data from Web_service
            alignak_map = self.ws_request.json()

            # Create QLabel and Pixmap for each sub_daemon
            for sub_daemon in alignak_map[daemon]:
                self.daemons_labels[daemon][sub_daemon] = {
                    'label': QLabel(sub_daemon),
                    'icon': QLabel()
                }

                self.daemons_labels[daemon][sub_daemon]['label'].setObjectName(sub_daemon)
                self.daemons_labels[daemon][sub_daemon]['icon'].setAlignment(Qt.AlignCenter)

                if alignak_map[daemon][sub_daemon]['alive']:
                    self.daemons_labels[daemon][sub_daemon]['icon'].setPixmap(
                        QPixmap(get_image_path('checked'))
                    )
                else:
                    self.daemons_labels[daemon][sub_daemon]['icon'].setPixmap(
                        QPixmap(get_image_path('unvalid'))
                    )

    def web_service_info(self):
        """
        Display information text if "web_service" is not configured

        """

        info_title_label = QLabel(
            '<span style="color: blue;">Alignak <b>Web Service</b> is not available !</span>'
        )
        self.grid.addWidget(info_title_label, 0, 0)

        info_label = QLabel(
            'Install it on your <b>Alignak server</b>. '
            'And configure the <b>settings.cfg</b> accordingly in <b>Alignak-app</b>.'
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignTop)

        self.grid.addWidget(info_label, 1, 0)

    def daemons_to_layout(self):
        """
        Add all daemons label to layout

        """

        if self.ws_request:
            self.grid.addWidget(QLabel('<b>Daemon Name</b> '), 1, 0)

            status_title = QLabel('<b>Status</b>')
            status_title.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(status_title, 1, 1)

            alignak_map = self.ws_request.json()

            for d in self.daemons_labels:
                logger.debug(self.daemons_labels[d])

            line = 2
            for daemon in self.daemons:
                for sub_daemon in alignak_map[daemon]:
                    self.grid.addWidget(
                        self.daemons_labels[daemon][sub_daemon]['label'], line, 0
                    )
                    self.grid.addWidget(
                        self.daemons_labels[daemon][sub_daemon]['icon'], line, 1
                    )
                    line += 1

    def update_status(self):
        """
        Check daemons states and update icons

        """

        # New request
        self.alignak_ws_request()

        for daemon in self.daemons:
            alignak_map = self.ws_request.json()

            # Update daemons QPixmap for each sub_daemon
            for sub_daemon in alignak_map[daemon]:
                if alignak_map[daemon][sub_daemon]['alive']:
                    self.daemons_labels[daemon][sub_daemon]['icon'].setPixmap(
                        QPixmap(get_image_path('checked'))
                    )
                else:
                    self.daemons_labels[daemon][sub_daemon]['icon'].setPixmap(
                        QPixmap(get_image_path('unvalid'))
                    )

    def show_states(self):
        """
        Show AlignakStatus

        """

        if get_app_config('Backend', 'web_service_status', boolean=True) and self.ws_request:
            self.update_status()

        self.show()
