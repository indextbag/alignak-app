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

import sys

import unittest2

from alignak_app.core.utils import set_app_config
from alignak_app.widgets.popup import AppPopup

try:
    __import__('PyQt5')
    from PyQt5.QtWidgets import QApplication
except ImportError:
    from PyQt4.Qt import QApplication


class TestPopup(unittest2.TestCase):
    """
        This file test the AppPopup class.
    """

    set_app_config()

    @classmethod
    def setUpClass(cls):
        """Create QApplication"""
        try:
            cls.app = QApplication(sys.argv)
        except:
            pass

    def test_initialize_notification(self):
        """Inititalize Notification"""

        under_test = AppPopup()

        self.assertIsNone(under_test.notification_type)
        self.assertIsNotNone(under_test.popup_factory)

        # Create all the label
        under_test.initialize_notification()

        self.assertEqual('state', under_test.notification_type.objectName())
        self.assertIsNotNone(under_test.popup_factory)

    def test_send_notifications(self):
        """Send Notification"""
        under_test = AppPopup()

        under_test.initialize_notification()

        self.assertEqual('', under_test.notification_type.text())

        # Simulate dicts of states
        hosts_states = dict(
            up= 1,
            down=1,
            unreachable=1
        )
        services_states = dict(
            ok=-1,
            warning=1,
            critical=1,
            unknown=1
        )

        # Send a CRITICAL notification
        changes = {
            'hosts': {
                'up': 'no changes',
                'down': 'no changes',
                'unreachable': 'no changes'
            },
            'services': {
                'ok': 'no changes',
                'warning': 'no changes',
                'critical': 'no changes',
                'unknown': 'no changes'
            }
        }
        under_test.send_notification('CRITICAL', hosts_states, services_states, changes)
        expected_content = 'AlignakApp has something broken... \nPlease Check your logs !'

        self.assertEqual('CRITICAL', under_test.notification_type.text())
        self.assertEqual(expected_content, under_test.popup_factory.text())

    def test_get_style_sheet(self):
        """Get Style Sheet according to States"""
        ok_css = "Background-color: #27ae60;"
        warning_css = "Background-color: #e67e22;"
        critical_css = "Background-color: #e74c3c;"
        none_css = "Background-color: #EEE;"

        under_test = AppPopup()

        css = {
            'OK': ok_css,
            'WARNING': warning_css,
            'CRITICAL': critical_css,
            'NONE': none_css,
        }
        states = ('OK', 'WARNING', 'CRITICAL', 'NONE')

        for state in states:
            expected_css = css[state]
            under_test.set_style_sheet(state)
            current_css = under_test.styleSheet()
            assert expected_css in current_css

    def test_set_position(self):
        """Position Change from Initial Position"""
        under_test = AppPopup()

        initial_position = under_test.pos()

        under_test.set_position()

        self.assertNotEqual(under_test.pos(), initial_position)