#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017:
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
    Buttons QWidget manage the buttons for:
     dashboard, host, problems, user and webui
"""

import webbrowser

from logging import getLogger

from alignak_app.core.utils import get_image_path, get_css, get_app_config
from alignak_app.widgets.host_widget import host_widget
from alignak_app.mainpanel.panel_widget import panel_widget

from PyQt5.Qt import QPushButton, QWidget, QIcon, QHBoxLayout  # pylint: disable=no-name-in-module
from PyQt5.Qt import QTimer  # pylint: disable=no-name-in-module

logger = getLogger(__name__)


class ButtonsQWidget(QWidget):
    """
        Class who create buttons for Dock QWidget
    """

    def __init__(self, parent=None):
        super(ButtonsQWidget, self).__init__(parent)
        self.setStyleSheet(get_css())
        # Fields
        self.update_timer = QTimer()
        self.webui_btn = QPushButton()
        self.profile_btn = QPushButton()
        self.problems_btn = QPushButton()
        self.host_btn = QPushButton()
        self.dashboard_btn = QPushButton()

    def initialize(self):
        """
        Initialize QWidget

        """

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.dashboard_btn.setIcon(QIcon(get_image_path('dashboard')))
        self.dashboard_btn.setFixedSize(40, 40)
        layout.addWidget(self.dashboard_btn)

        self.host_btn.setIcon(QIcon(get_image_path('host')))
        self.host_btn.setFixedSize(40, 40)
        self.host_btn.clicked.connect(self.open_host_widget)
        layout.addWidget(self.host_btn)

        self.problems_btn.setIcon(QIcon(get_image_path('problem')))
        self.problems_btn.setFixedSize(40, 40)
        layout.addWidget(self.problems_btn)

        self.profile_btn.setIcon(QIcon(get_image_path('user')))
        self.profile_btn.setFixedSize(40, 40)
        layout.addWidget(self.profile_btn)

        self.webui_btn.setIcon(QIcon(get_image_path('web')))
        self.webui_btn.setFixedSize(40, 40)
        self.webui_btn.clicked.connect(self.open_url)
        layout.addWidget(self.webui_btn)

        self.update_widget()

        self.update_timer.setInterval(15000)
        self.update_timer.start()
        self.update_timer.timeout.connect(self.update_widget)

    def update_widget(self):
        """
        Update the QWidget buttons

        """

        webui_url = get_app_config('Alignak', 'webui')

        if webui_url:
            self.webui_btn.setEnabled(True)
            self.webui_btn.setToolTip(_("Open WebUI in browser"))
        else:
            self.webui_btn.setEnabled(False)
            self.webui_btn.setToolTip(_("WebUI is not set in configuration file."))

    @staticmethod
    def open_host_widget():
        """
        Create and manage HostQWidget

        """

        panel_widget.app_widget.show()

    @staticmethod
    def open_url():  # pragma: no cover
        """
        Add a link to Alignak-WebUI on every menu

        """

        webui_url = get_app_config('Alignak', 'webui')
        if webui_url:
            logger.debug('Open url : ' + webui_url + '/login')
            webbrowser.open(webui_url + '/login')
