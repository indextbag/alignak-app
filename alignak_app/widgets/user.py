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
    User manage QWidget who display User Profile.
"""

from logging import getLogger

from alignak_app.core.utils import get_image_path, get_css
from alignak_app.widgets.app_widget import AppQWidget
from alignak_app.widgets.banner import send_banner

from PyQt5.QtWidgets import QWidget, QPushButton, QCheckBox  # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout  # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QLabel  # pylint: disable=no-name-in-module
from PyQt5.Qt import QIcon  # pylint: disable=no-name-in-module

logger = getLogger(__name__)


class UserProfile(QWidget):
    """
        Class who create QWidget for User Profile.
    """

    def __init__(self, app_backend, parent=None):
        super(UserProfile, self).__init__(parent)
        self.setStyleSheet(get_css())
        # Fields
        self.user = None
        self.app_backend = app_backend
        self.app_widget = None

    def initialize(self):
        """
        Initialize User QWidget

        """

        # Get the user data first
        self.get_user_data()

        # Then initialize AppQWidget
        self.app_widget = AppQWidget()
        self.app_widget.initialize('User view: %s' % self.user['alias'])
        self.app_widget.add_widget(self)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.get_main_user_widget())
        layout.addWidget(self.get_info_user_widget())

        layout.addWidget(self.get_notifications_widget())

    def get_user_data(self):
        """
        Get and set the user data

        """

        projection = [
            '_realm',
            'is_admin',
            'alias',
            'name',
            'notes',
            'email',
            'can_submit_commands',
            'token',
            'host_notifications_enabled',
            'service_notifications_enabled',
            'host_notification_period',
            'service_notification_period',
            'host_notification_options',
            'service_notification_options',
        ]

        self.user = self.app_backend.get_user(projection)

    def get_main_user_widget(self):
        """
        Create and return QWidget with main informations

        :return: main QWidget
        :rtype: QWidget
        """

        main_user_widget = QWidget()
        main_layout = QGridLayout()
        main_user_widget.setLayout(main_layout)

        main_title = QLabel('Main informations:')
        main_layout.addWidget(main_title, 0, 0, 1, 2)

        realm_title = QLabel('Realm:')
        main_layout.addWidget(realm_title, 1, 0, 1, 1)
        realm_data = QLabel(self.user['_realm'])
        main_layout.addWidget(realm_data)

        role_title = QLabel('Role:')
        main_layout.addWidget(role_title, 2, 0, 1, 1)
        role_data = QLabel(str(self.user['is_admin']))
        main_layout.addWidget(role_data, 2, 1, 1, 1)

        mail_title = QLabel('Email:')
        main_layout.addWidget(mail_title, 3, 0, 1, 1)
        mail_data = QLabel(self.user['email'])
        main_layout.addWidget(mail_data, 3, 1, 1, 1)

        return main_user_widget

    def get_info_user_widget(self):
        """
        Create and return inf of user in a QWidget

        :return: information QWidet
        :rtype: QWidget
        """

        info_widget = QWidget()
        info_layout = QGridLayout()
        info_widget.setLayout(info_layout)

        info_layout.addWidget(self.get_rights_widget(), 0, 0, 1, 1)
        info_layout.addWidget(self.get_notes_widget(), 0, 1, 1, 1)

        return info_widget

    def get_rights_widget(self):
        """
        Create and return Rights QWidget

        :return: rights QWidget
        :rtype: QWidget
        """

        rights_widget = QWidget()
        rights_layout = QGridLayout()
        rights_widget.setLayout(rights_layout)

        rights_title = QLabel('Rights:')
        rights_layout.addWidget(rights_title, 0, 0, 1, 2)

        admin_title = QLabel('Administrator:')
        rights_layout.addWidget(admin_title, 1, 0, 1, 1)
        admin_data = QLabel(str(self.user['is_admin']))
        rights_layout.addWidget(admin_data, 1, 1, 1, 1)

        command_title = QLabel('Commands:')
        rights_layout.addWidget(command_title, 2, 0, 1, 1)
        command_data = QLabel(str(self.user['can_submit_commands']))
        rights_layout.addWidget(command_data, 2, 1, 1, 1)

        password_title = QLabel('Password:')
        rights_layout.addWidget(password_title, 3, 0, 1, 1)
        password_btn = QPushButton()
        password_btn.setIcon(QIcon(get_image_path('user')))
        password_btn.setFixedSize(32, 32)
        rights_layout.addWidget(password_btn, 3, 1, 1, 1)

        return rights_widget

    def get_notes_widget(self):
        """
        Create and return Notes QWidget

        :return: notes QWidget
        :rtype: QWidget
        """

        notes_widget = QWidget()
        notes_layout = QGridLayout()
        notes_widget.setLayout(notes_layout)

        notes_title = QLabel('Notes:')
        notes_layout.addWidget(notes_title, 0, 0, 1, 2)

        alias_title = QLabel('Alias')
        notes_layout.addWidget(alias_title, 1, 0, 1, 1)
        alias_data = QLabel(self.user['alias'])
        notes_layout.addWidget(alias_data, 1, 1, 1, 1)

        note_title = QLabel('Notes')
        notes_layout.addWidget(note_title, 2, 0, 1, 1)
        note_data = QLabel(self.user['notes'])
        notes_layout.addWidget(note_data, 2, 1, 1, 1)

        token_title = QLabel('Token')
        notes_layout.addWidget(token_title, 3, 0, 1, 1)
        token_data = QLabel(self.user['token'])
        notes_layout.addWidget(token_data, 3, 1, 1, 1)

        return notes_widget

    def get_notifications_widget(self):
        """
        Create and return notification QWidget for hosts and services

        :return: notifications QWidget
        :rtype: QWidget
        """

        notification_widget = QWidget()
        notification_layout = QGridLayout()
        notification_widget.setLayout(notification_layout)

        notification_layout.addWidget(self.get_hosts_notif_widget(), 0, 0, 1, 1)
        notification_layout.addWidget(self.get_services_notif_widget(), 0, 1, 1, 1)

        return notification_widget

    def get_hosts_notif_widget(self):
        """
        Create and return notification QWidget for hosts

        :return: hosts notification QWidget
        :rtype: QWidget
        """

        host_notif_widget = QWidget()
        host_notif_layout = QGridLayout()
        host_notif_widget.setLayout(host_notif_layout)

        notif_title = QLabel("Hosts notifications configurations")
        host_notif_layout.addWidget(notif_title, 0, 0, 1, 2)

        state_title = QLabel("State:")
        host_notif_layout.addWidget(state_title, 1, 0, 1, 1)
        notif_state = QCheckBox()
        notif_state.setChecked(self.user['host_notifications_enabled'])
        notif_state.stateChanged.connect(self.enable_notifications)
        notif_state.setObjectName('hostactions')
        notif_state.setFixedSize(18, 18)
        host_notif_layout.addWidget(notif_state, 1, 1, 1, 1)

        period_title = QLabel("Notification period:")
        host_notif_layout.addWidget(period_title, 2, 0, 1, 1)
        period_data = QLabel(self.user['host_notification_period'])
        host_notif_layout.addWidget(period_data, 2, 1, 1, 1)

        enable_title = QLabel("Notification enabled:")
        host_notif_layout.addWidget(enable_title, 3, 0, 1, 1)
        enable_data = QLabel(str(self.user['host_notifications_enabled']))
        host_notif_layout.addWidget(enable_data, 3, 1, 1, 1)

        option_title = QLabel("Options:")
        host_notif_layout.addWidget(option_title, 4, 0, 1, 1)
        options_data = QLabel(str(self.user['host_notification_options']))
        host_notif_layout.addWidget(options_data, 4, 1, 1, 1)

        return host_notif_widget

    def get_services_notif_widget(self):
        """
        Create and return notification QWidget for services

        :return: services notification QWidget
        :rtype: QWidget
        """

        service_notif_widget = QWidget()
        service_notif_layout = QGridLayout()
        service_notif_widget.setLayout(service_notif_layout)

        notif_title = QLabel("Services notifications configurations")
        service_notif_layout.addWidget(notif_title, 0, 0, 1, 2)

        state_title = QLabel("State:")
        service_notif_layout.addWidget(state_title, 1, 0, 1, 1)
        notif_state = QCheckBox()
        notif_state.setObjectName('serviceactions')
        notif_state.setChecked(self.user['service_notifications_enabled'])
        notif_state.stateChanged.connect(self.enable_notifications)
        notif_state.checkState()
        notif_state.setFixedSize(18, 18)
        service_notif_layout.addWidget(notif_state, 1, 1, 1, 1)

        period_title = QLabel("Notification period:")
        service_notif_layout.addWidget(period_title, 2, 0, 1, 1)
        period_data = QLabel(self.user['service_notification_period'])
        service_notif_layout.addWidget(period_data, 2, 1, 1, 1)

        enable_title = QLabel("Notification enabled:")
        service_notif_layout.addWidget(enable_title, 3, 0, 1, 1)
        enable_data = QLabel(str(self.user['service_notifications_enabled']))
        service_notif_layout.addWidget(enable_data, 3, 1, 1, 1)

        option_title = QLabel("Options:")
        service_notif_layout.addWidget(option_title, 4, 0, 1, 1)
        options_data = QLabel(str(self.user['service_notification_options']))
        service_notif_layout.addWidget(options_data, 4, 1, 1, 1)

        return service_notif_widget

    def enable_notifications(self):
        """
        Enable notification for the wanted type: hosts or services

        """

        check_btn = self.sender()

        notification_type = ''
        if 'hostactions' in check_btn.objectName():
            notification_type = 'host_notifications_enabled'
        elif 'serviceactions' in check_btn.objectName():
            notification_type = 'service_notifications_enabled'
        else:
            logger.error('Wrong caller %s' % self.sender().objectName())

        if notification_type:
            # check_btn.checkState() is equal to 0 or 2
            notification_enabled = True if check_btn.checkState() else False
            data = {notification_type: notification_enabled}
            headers = {'If-Match': self.user['_etag']}
            endpoint = '/'.join(['user', self.user['_id']])

            patched = self.app_backend.patch(endpoint, data, headers)

            if patched:
                enabled = 'enabled' if notification_enabled else 'disabled'
                message = "Notifications for %ss are %s" % (
                    check_btn.objectName().replace('actions', ''),
                    enabled
                )
                send_banner('OK', message, duration=10000)
            else:
                send_banner('ERROR', "Backend PATCH failed, please check your logs !")


class User(object):
    """
        User manage the UserProfile QWidget creation
    """

    def __init__(self, app_backend):
        self.app_backend = app_backend
        self.user_widget = None

    def create_user_profile(self):
        """
        Create the USerProfile QWidget. Store old informations if needed.

        """

        old_pos = None
        if self.user_widget:
            old_pos = self.user_widget.app_widget.pos()
            self.user_widget.deleteLater()
            self.user_widget = None

        self.user_widget = UserProfile(self.app_backend)
        self.user_widget.initialize()

        if old_pos:
            self.user_widget.app_widget.move(old_pos)

    def show_user_widget(self):
        """
        Destroy and create the UserProfile, then show it

        """

        self.create_user_profile()
        self.user_widget.app_widget.show()