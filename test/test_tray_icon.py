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

import sys

import unittest2

from alignak_app.core.backend import AppBackend
from alignak_app.core.utils import get_image_path
from alignak_app.core.utils import init_config
from alignak_app.systray.tray_icon import TrayIcon

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction


class TestTrayIcon(unittest2.TestCase):
    """
        TODO This file test the TrayIcon class.
    """

    init_config()

    icon = QIcon(get_image_path('icon'))

    backend = AppBackend()
    backend.login()

    @classmethod
    def setUpClass(cls):
        """Create QApplication"""
        try:
            cls.app = QApplication(sys.argv)
        except:
            pass

    def test_tray_icon(self):
        """Init TrayIcon and QMenu"""
        under_test = TrayIcon(TestTrayIcon.icon)

        self.assertIsInstance(under_test.menu, QMenu)

    def test_about_action(self):
        """About QAction is created"""
        under_test = TrayIcon(TestTrayIcon.icon)

        self.assertFalse(under_test.qaction_factory.actions)

        under_test.create_about_action()

        self.assertIsNotNone(under_test.qaction_factory)
        self.assertIsInstance(under_test.qaction_factory.get('about'), QAction)

    def test_quit_action(self):
        """Quit QAction is created"""
        under_test = TrayIcon(TestTrayIcon.icon)

        self.assertFalse(under_test.qaction_factory.actions)

        under_test.create_quit_action()

        self.assertIsNotNone(under_test.qaction_factory.get('exit'))
        self.assertIsInstance(under_test.qaction_factory.get('exit'), QAction)

    def test_build_menu(self):
        """Build Menu add QActions"""
        from alignak_app.dock.dock_widget import DockQWidget

        under_test = TrayIcon(TestTrayIcon.icon)
        dock_test = DockQWidget()

        # Assert no actions in Menu
        self.assertFalse(under_test.menu.actions())
        self.assertIsNone(under_test.app_about)
        self.assertIsNone(under_test.dock)
        self.assertIsNotNone(under_test.qaction_factory)

        under_test.build_menu(dock_test)

        # Assert actions are added in Menu
        self.assertTrue(under_test.menu.actions())
        self.assertIsNotNone(under_test.app_about)
        self.assertIsNotNone(under_test.dock)
        self.assertIsNotNone(under_test.qaction_factory)
