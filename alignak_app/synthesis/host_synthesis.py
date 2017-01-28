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
    TODO
"""

import json
import datetime
import sys

from logging import getLogger

from alignak_app.core.utils import get_image_path, init_config
from alignak_app.core.backend import AppBackend
from alignak_app.core.action_manager import ActionManager, ACK, DOWNTIME, PROCESS
from alignak_app.widgets.app_widget import AppQWidget
from alignak_app.widgets.banner import send_banner
from alignak_app.synthesis.service import Service

try:
    __import__('PyQt5')
    from PyQt5.QtWidgets import QApplication  # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QWidget, QPushButton, QLabel  # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QGridLayout, QHBoxLayout  # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QStackedWidget  # pylint: disable=no-name-in-module
    from PyQt5.Qt import QIcon, QPixmap, QListWidget  # pylint: disable=no-name-in-module
    from PyQt5.Qt import QTimer, QListWidgetItem, Qt  # pylint: disable=no-name-in-module
except ImportError:  # pragma: no cover
    from PyQt4.Qt import QApplication  # pylint: disable=import-error
    from PyQt4.Qt import QWidget, QPushButton, QLabel  # pylint: disable=import-error
    from PyQt4.Qt import QGridLayout, QHBoxLayout  # pylint: disable=import-error
    from PyQt4.Qt import QStackedWidget  # pylint: disable=import-error
    from PyQt4.Qt import QIcon, QPixmap, QListWidget  # pylint: disable=import-error
    from PyQt4.Qt import QTimer, QListWidgetItem, Qt  # pylint: disable=import-error


logger = getLogger(__name__)


class HostSynthesis(QWidget):
    """
        Class who create the Synthesis QWidget.
    """

    def __init__(self, app_backend, parent=None):
        super(HostSynthesis, self).__init__(parent)
        self.app_backend = app_backend
        self.action_manager = ActionManager(app_backend)
        self.host = {}
        self.stack = None

    def initialize(self, backend_data):
        """
        TODO
        :return:
        """

        main_layout = QHBoxLayout(self)
        self.host = backend_data['host']

        main_layout.addWidget(self.get_host_widget(backend_data))
        main_layout.addWidget(self.get_services_widget(backend_data))

        action_timer = QTimer(self)
        action_timer.start(10000)
        action_timer.timeout.connect(self.check_action_manager)

    def get_services_widget(self, backend_data):
        """

        :param backend_data:
        :return:
        """

        services_widget = QWidget()
        services_layout = QGridLayout(services_widget)

        # Init Vars
        pos = 0
        self.stack = QStackedWidget()
        services_list = QListWidget()

        services_layout.addWidget(services_list)
        services_layout.addWidget(self.stack)

        for service in backend_data['services']:
            # Service QWidget
            service_widget = Service()
            service_widget.initialize(service)

            # Connect ACK button
            service_widget.acknowledge_btn.clicked.connect(self.add_acknowledge)
            service_widget.acknowledge_btn.setObjectName(
                'service:%s:%s' % (service['_id'], service['display_name'])
            )
            if 'OK' in service['ls_state'] or service['ls_acknowledged']:
                service_widget.acknowledge_btn.setEnabled(False)

            # Connect DOWN button
            service_widget.downtime_btn.clicked.connect(self.add_downtime)
            service_widget.downtime_btn.setObjectName(
                'service:%s:%s' % (service['_id'], service['display_name'])
            )
            if 'OK' in service['ls_state'] or service['ls_downtimed']:
                service_widget.downtime_btn.setEnabled(False)

            # Add widget to QStackedWidget
            self.stack.addWidget(service_widget)
            # Add item to QListWidget
            list_item = QListWidgetItem()
            list_item.setText(service['display_name'])
            list_item.setIcon(
                QIcon(get_image_path('services_%s' % service['ls_state']))
            )
            services_list.insertItem(pos, list_item)

            pos += 1

        services_list.currentRowChanged.connect(self.display)

        return services_widget

    def get_host_widget(self, backend_data):
        """
        TODO
        :return:
        """

        host_widget = QWidget()
        host_layout = QGridLayout(host_widget)

        # Overall State
        host_overall_state = QLabel()
        host_overall_state.setPixmap(self.get_real_state_icon(backend_data['services']))
        host_layout.addWidget(host_overall_state, 0, 0, 1, 2)

        # Hostname
        host_name = QLabel(backend_data['host']['alias'])
        host_layout.addWidget(host_name, 1, 0, 1, 2)

        # ACK
        acknowledge_btn = QPushButton()
        acknowledge_btn.setObjectName(
            'host:%s:%s' % (backend_data['host']['_id'], backend_data['host']['name'])
        )
        acknowledge_btn.setIcon(QIcon(get_image_path('acknowledged')))
        acknowledge_btn.setFixedSize(25, 25)
        acknowledge_btn.setToolTip('Acknowledge this host')
        acknowledge_btn.clicked.connect(self.add_acknowledge)
        if 'UP' in backend_data['host']['ls_state'] or backend_data['host']['ls_acknowledged']:
            acknowledge_btn.setEnabled(False)
        host_layout.addWidget(acknowledge_btn, 2, 0, 1, 1)

        # DOWN
        downtime_btn = QPushButton()
        downtime_btn.setObjectName(
            'host:%s:%s' % (backend_data['host']['_id'], backend_data['host']['name'])
        )
        downtime_btn.setIcon(QIcon(get_image_path('downtime')))
        downtime_btn.setFixedSize(25, 25)
        downtime_btn.setToolTip('Schedule a downtime for this host')
        downtime_btn.clicked.connect(self.add_downtime)
        if 'UP' in backend_data['host']['ls_state'] or backend_data['host']['ls_downtimed']:
            downtime_btn.setEnabled(False)
        host_layout.addWidget(downtime_btn, 2, 1, 1, 1)

        host_real_state = QLabel()
        host_real_state.setPixmap(self.get_host_icon(backend_data['host']['ls_state']))
        host_layout.addWidget(host_real_state, 3, 0, 1, 2)

        return host_widget

    def display(self, i):
        """
        TODO
        :param i:
        :return:
        """
        self.stack.setCurrentIndex(i)

    def add_acknowledge(self):  # pragma: no cover, no testability
        """
        Handle action for "acknowledge_btn"

        """

        # Get who emit SIGNAL
        print(self.sender().objectName())
        item_type = self.sender().objectName().split(':')[0]

        if self.host:
            if 'service' in item_type:
                service_id = self.sender().objectName().split(':')[1]
            else:
                service_id = None
            host_id = self.host['_id']

            user = self.app_backend.get_user()

            comment = '%s %s acknowledged by %s, from Alignak-app' % (
                item_type.capitalize(),
                self.sender().objectName().split(':')[2],
                user['name']
            )

            data = {
                'action': 'add',
                'host': host_id,
                'service': service_id,
                'user': user['_id'],
                'comment': comment
            }

            post = self.app_backend.post(ACK, data)
            item_process = {
                'action': PROCESS,
                'name': self.sender().objectName().split(':')[2],
                'post': post
            }
            self.action_manager.add_item(item_process)

            item_action = {
                'action': ACK,
                'host_id': host_id,
                'service_id': service_id
            }
            self.action_manager.add_item(item_action)

            self.sender().setEnabled(False)

    def add_downtime(self):  # pragma: no cover, no testability
        """
        Handle action for "downtime_btn"

        """

        # Get who emit SIGNAL
        item_type = self.sender().objectName().split(':')[0]

        if self.host:
            if 'service' in item_type:
                service_id = self.sender().objectName().split(':')[1]
            else:
                service_id = None
            host_id = self.host['_id']

            user = self.app_backend.get_user()

            comment = 'Schedule downtime by %s, from Alignak-app' % user['name']

            start_time = datetime.datetime.now()
            end_time = start_time + datetime.timedelta(days=1)

            data = {
                'action': 'add',
                'host': host_id,
                'service': service_id,
                'user': user['_id'],
                'comment': comment,
                'start_time': start_time.timestamp(),
                'end_time': end_time.timestamp(),
                'fixed': True
            }

            post = self.app_backend.post(DOWNTIME, data)
            item_process = {
                'action': PROCESS,
                'name': self.sender().objectName().split(':')[2],
                'post': post
            }
            self.action_manager.add_item(item_process)

            item_action = {
                'action': DOWNTIME,
                'host_id': self.current_host['_id'],
                'service_id': service_id
            }
            self.action_manager.add_item(item_action)

            self.sender().setEnabled(False)

    def check_action_manager(self):
        """
        Check ActionManager and send banner if items to send

        """

        items_to_send = self.action_manager.check_items()
        actions = [ACK, DOWNTIME]

        if items_to_send:
            # Send ACKs and DOWNTIMEs
            for action in actions:
                title = action.replace('action', '').capitalize()
                # For Hosts
                if items_to_send[action]['hosts']:
                    for item in items_to_send[action]['hosts']:
                        host = self.app_backend.get_host(item['host_id'])
                        send_banner('OK', '%s for %s is done !' % (title, host['name']))
                # For Services
                if items_to_send[action]['services']:
                    for item in items_to_send[action]['services']:
                        service = self.app_backend.get_service(item['host_id'], item['service_id'])
                        send_banner('OK', '%s for %s is done !' % (title, service['name']))
            # Send PROCESS
            if items_to_send[PROCESS]:
                for item in items_to_send[PROCESS]:
                    requested_action = item['post']['_links']['self']['title'].replace(
                        'Action', '')
                    action_title = requested_action.capitalize()
                    send_banner('OK', '%s for %s is processed...' % (action_title, item['name']))

    @staticmethod
    def get_service_icon(state):
        """
        Return QPixmap with the icon corresponding to the status.

        :param state: state of the host.
        :type state: str
        :return: QPushButton with QIcon
        :rtype: QPushButton
        """

        state_model = {
            'OK': 'services_ok',
            'WARNING': 'services_warning',
            'CRITICAL': 'services_critical',
            'UNKNOWN': 'services_unknown',
            'UNREACHABLE': 'services_unreachable',
            'DEFAULT': 'services_none'
        }

        try:
            icon_name = state_model[state]
        except KeyError:
            icon_name = state_model['DEFAULT']
        icon = QPixmap(get_image_path(icon_name))

        return icon

    @staticmethod
    def get_host_icon(state):
        """
        Return QPixmap with the icon corresponding to the status.

        :param state: state of the host.
        :type state: str
        :return: QPixmap with image
        :rtype: QPixmap
        """

        if 'UP' in state:
            icon_name = 'hosts_up'
        elif 'UNREACHABLE' in state:
            icon_name = 'hosts_unreach'
        elif 'DOWN' in state:
            icon_name = 'hosts_down'
        else:
            icon_name = 'hosts_none'

        icon = QPixmap(get_image_path(icon_name))

        return icon

    @staticmethod
    def get_real_state_icon(services):
        """
        Calculate real state and return QPixmap

        :param services: dict of services. None if search is not found
        :type services: dict
        """

        if services:
            icon_names = ['hosts_up', 'hosts_none', 'hosts_unreach', 'hosts_down']
            state_lvl = []
            for service in services:
                if 'UNREACHABLE' in service['ls_state'] or 'CRITICAL' in service['ls_state']:
                    state_lvl.append(3)
                elif 'WARNING' in service['ls_state'] or 'UNKNOWN' in service['ls_state']:
                    state_lvl.append(2)
                elif service['ls_downtimed']:
                    state_lvl.append(1)
                else:
                    state_lvl.append(0)

            result = max(state_lvl)

            icon = QPixmap(get_image_path(icon_names[result]))
        else:
            icon = QPixmap(get_image_path('hosts_none'))

        return icon