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
    Notifier manage notifications and collect data from backend.
"""

from logging import getLogger

from alignak_app.alignak_data import AlignakData
from alignak_app.popup import AppPopup

from PyQt5.QtWidgets import QSystemTrayIcon  # pylint: disable=no-name-in-module
from PyQt5.QtCore import QTimer  # pylint: disable=no-name-in-module
from PyQt5.QtGui import QIcon  # pylint: disable=no-name-in-module

logger = getLogger(__name__)


class AppNotifier(QSystemTrayIcon):  # pragma: no cover
    """
    Class who manage notifications and states of hosts and services.
    """

    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.backend_client = None
        self.config = None
        self.hosts_states = {}
        self.services_states = {}
        self.tray_icon = None
        self.popup = AppPopup()

    def start_process(self, config, tray_icon):
        """
        Start process loop of application with a QTimer.

        :param config: config parser.
        :type config: :class:`~configparser.ConfigParser`
        :param tray_icon: QSystemTrayIcon menu.
        :type tray_icon: :class:`~alignak_app.tray_icon.TrayIcon`
        """

        self.tray_icon = tray_icon

        self.config = config

        check_interval = int(config.get('Alignak-App', 'check_interval'))
        check_interval *= 1000

        timer = QTimer(self)
        timer.start(check_interval)

        self.popup.initialize_notification(level='Warning !', content='Test')

        self.backend_client = AlignakData()
        self.backend_client.log_to_backend(config)

        timer.timeout.connect(self.check_data)

    def check_data(self):
        """
        Collect data from Backend-Client.

        """
        self.hosts_states, self.services_states = self.get_state()

        # Define notification message
        msg = ''
        if self.services_states['ok'] < 0 or self.hosts_states['up'] < 0:
            msg += 'AlignakApp has something broken... \nPlease Check your logs !'
        else:
            for state in self.hosts_states:
                print(state + ' : ' + str(self.hosts_states[state]))
                msg += 'Hosts ' + state + ' : ' + str(self.hosts_states[state]) + '\n'
            for state in self.services_states:
                print(state + ' : ' + str(self.services_states[state]))
                msg += 'Services ' + state + ' : ' + str(self.services_states[state]) + '\n'

        # Change application icon
        if self.services_states['critical'] > 0 or self.hosts_states['down'] > 0:
            img = self.tray_icon.get_icon_path() + self.config.get('Config', 'alert')
            # title = 'Alert !!!'
        elif self.services_states['unknown'] > 0 or \
                self.services_states['warning'] or \
                self.hosts_states['unreach'] > 0:
            img = self.tray_icon.get_icon_path() + self.config.get('Config', 'warning')
            # title = 'Warning !'
        else:
            # title = 'All is OK :)'
            img = self.tray_icon.get_icon_path() + self.config.get('Config', 'ok')

        # Trigger changes and send notification
        self.tray_icon.setIcon(QIcon(img))
        self.popup.send_notification()
        self.tray_icon.update_menus_actions(self.hosts_states, self.services_states)

    def get_state(self):
        """
        Check the hosts states.

        :return: number of hosts and services UP, UNKNOWN and DOWN in two dict.
        :rtype: dict
        """

        if not self.backend_client.backend.authenticated:
            logger.warning('Connection to backend is lost, application will try to reconnect !')
            self.backend_client.log_to_backend(self.config)

        logger.info('Get state of Host and Services...')
        # Dicts for states
        hosts_states = {
            'up': 0,
            'down': 0,
            'unreachable': 0
        }
        services_states = {
            'ok': 0,
            'critical': 0,
            'unknown': 0,
            'warning': 0
        }

        # Collect Hosts state
        hosts_data = self.backend_client.get_host_state()

        if not hosts_data:
            hosts_states['up'] = -1
        else:
            for _, v in hosts_data.items():
                if 'UP' in v:
                    hosts_states['up'] += 1
                if 'DOWN' in v:
                    hosts_states['down'] += 1
                if 'UNREACHABLE' in v:
                    hosts_states['unreachable'] += 1
            hosts_log = str(hosts_states['up']) + ' host(s) Up, ' \
                + str(hosts_states['down']) + ' host(s) Down, ' \
                + str(hosts_states['unreachable']) + ' host(s) unreachable, '
            logger.info(hosts_log)

        # Collect Services state
        services_data = self.backend_client.get_service_state()
        if not services_data:
            services_states['ok'] = -1
        else:
            for _, v in services_data.items():
                if 'OK' in v:
                    services_states['ok'] += 1
                if 'CRITICAL' in v:
                    services_states['critical'] += 1
                if 'UNKNOWN' in v:
                    services_states['unknown'] += 1
                if 'WARNING' in v:
                    services_states['warning'] += 1
            services_log = str(services_states['ok']) + ' service(s) Ok, ' \
                + str(services_states['warning']) + ' service(s) Warning, ' \
                + str(services_states['critical']) + ' service(s) Critical, ' \
                + str(services_states['unknown']) + ' service(s) Unknown.'
            logger.info(services_log)

        return hosts_states, services_states
