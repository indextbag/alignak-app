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
    Panel QWidget manage the creation of Hosts and Services QWidgets
"""

from logging import getLogger

from PyQt5.Qt import QApplication, QPushButton  # pylint: disable=no-name-in-module
from PyQt5.Qt import QCompleter, QLineEdit, QIcon, QHBoxLayout  # pylint: disable=no-name-in-module
from PyQt5.Qt import QStringListModel, Qt, QVBoxLayout, QWidget  # pylint: disable=no-name-in-module

from alignak_app.core.data_manager import data_manager
from alignak_app.core.utils import app_css, get_image
from alignak_app.widgets.common.frames import AppQFrame, get_frame_separator
from alignak_app.widgets.panel.dashboard import DashboardQWidget
from alignak_app.widgets.panel.host import HostQWidget
from alignak_app.widgets.panel.services import ServicesQWidget

logger = getLogger(__name__)


class PanelQWidget(QWidget):
    """
        Class who manage Panel with Host and Services QWidgets
    """

    def __init__(self, parent=None):
        super(PanelQWidget, self).__init__(parent)
        self.setStyleSheet(app_css)
        self.setWindowIcon(QIcon(get_image('icon')))
        # Fields
        self.layout = QVBoxLayout()
        self.line_search = QLineEdit()
        self.completer = QCompleter()
        self.app_widget = AppQFrame()
        self.hostnames_list = []
        self.dashboard_widget = DashboardQWidget()
        self.host_widget = HostQWidget()
        self.services_widget = ServicesQWidget()

    def initialize(self, dock_width):
        """
        Create the QWidget with its items and layout.

        """

        logger.info('Create Panel View...')
        self.setLayout(self.layout)

        # Dashboard widget
        self.dashboard_widget.initialize()
        self.layout.addWidget(self.dashboard_widget)
        self.layout.addWidget(get_frame_separator())

        # Search widget
        search_widget = self.get_search_widget()
        self.layout.addWidget(search_widget)

        # Host widget
        self.host_widget.initialize()
        self.layout.addWidget(self.host_widget)

        # Services widget
        self.services_widget.initialize()
        self.layout.addWidget(self.services_widget)

        # Align all widgets to Top
        self.layout.setAlignment(Qt.AlignTop)

        # Apply size and position on AppQWidget
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        desktop = QApplication.desktop().availableGeometry(screen)

        self.app_widget.initialize(_('Hosts Synthesis View'))
        self.app_widget.add_widget(self)
        self.app_widget.resize(desktop.width() - dock_width, desktop.height())
        self.app_widget.move(0, 0)

        # Hide widgets for first start
        self.host_widget.hide()
        self.services_widget.hide()

    def get_search_widget(self):
        """
        Create and return the search QWidget

        :return: search QWidget
        :rtype: QWidget
        """

        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)

        # Search button
        button = QPushButton(_('Search Host'), self)
        button.setObjectName('search')
        button.setFixedHeight(25)
        button.setToolTip(_('Search Host'))
        button.clicked.connect(self.display_host)
        layout.addWidget(button)

        self.line_search.setFixedHeight(button.height())
        self.line_search.returnPressed.connect(button.click)
        self.line_search.cursorPositionChanged.connect(button.click)
        layout.addWidget(self.line_search)

        self.create_line_search()

        return widget

    def create_line_search(self, hostnames_list=None):
        """
        Add all hosts to QLineEdit and set QCompleter

        :param hostnames_list: list of host names
        :type hostnames_list: list
        """

        # Get QStringListModel
        model = self.completer.model()
        if not model:
            model = QStringListModel()

        if not hostnames_list:
            self.hostnames_list = data_manager.get_all_hostnames()
        else:
            self.hostnames_list = hostnames_list

        model.setStringList(self.hostnames_list)

        # Configure QCompleter from model
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setModel(model)

        # Add completer to QLineEdit
        self.line_search.setCompleter(self.completer)
        self.line_search.setPlaceholderText(_('Type a host name to display its data'))
        self.line_search.setToolTip(_('Type a host name to display its data'))

    def display_host(self):
        """
        Display and update HostQWidget

        """

        if self.line_search.text() in self.hostnames_list:
            # Update linesearch if needed
            hostnames_list = data_manager.get_all_hostnames()
            if hostnames_list != self.hostnames_list:
                self.create_line_search(hostnames_list)

            # Update QWidgets
            self.dashboard_widget.update_dashboard()
            self.dashboard_widget.show()
            self.host_widget.update_widget(self.line_search.text())
            self.host_widget.show()
            self.services_widget.set_data(self.line_search.text())
            self.services_widget.update_widget()
            self.services_widget.show()
        else:
            self.host_widget.hide()
            self.services_widget.hide()