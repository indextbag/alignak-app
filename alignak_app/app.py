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
    App manage Alignak-App
"""

import sys
from logging import DEBUG, INFO

from alignak_app.core.logs import create_logger
from alignak_app.core.notifier import AppNotifier
from alignak_app.core.utils import get_image_path, get_main_folder, get_app_workdir
from alignak_app.core.utils import init_config, get_app_config
from alignak_app.core.locales import init_localization
from alignak_app.systray.tray_icon import TrayIcon
from alignak_app.widgets.login import AppLogin
from alignak_app.widgets.banner import bannerManager, send_banner
from alignak_app.core.backend import app_backend
from alignak_app.dashboard.app_dashboard import Dashboard

from PyQt5.QtWidgets import QDialog, QMessageBox  # pylint: disable=no-name-in-module
from PyQt5.Qt import QIcon, QTimer  # pylint: disable=no-name-in-module
from PyQt5.Qt import QObject, pyqtSignal  # pylint: disable=no-name-in-module

# Initialize app config, logger and localization
init_config()
logger = create_logger()
init_localization()


class AlignakApp(QObject):
    """
        Class who build Alignak-app and initialize configuration, notifier and systray icon.
    """

    reconnecting = pyqtSignal(str, name='reconnecting')

    def __init__(self, parent=None):
        super(AlignakApp, self).__init__(parent)
        self.tray_icon = None
        self.notifier = None
        self.notifier_timer = QTimer()
        self.reconnect_mode = False
        self.dashboard = None

    def start(self):
        """
        The main function of Alignak-App

        """

        # Start BannerManager
        bannerManager.start()

        # Define level of logger
        logger.name = 'alignak_app.app'
        if get_app_config('Log', 'debug', boolean=True):
            logger.setLevel(DEBUG)
            logger.info('Logger Level is: DEBUG')
        else:
            logger.setLevel(INFO)
            logger.info('Logger Level is: INFO')

        logger.info('App WorkDir = %s', get_app_workdir())
        logger.info('App MainDir = %s', get_main_folder())

        # If not app_backend url, stop application
        if get_app_config('Alignak', 'backend'):
            # If not username and password, create login form, else connect with config data.
            if not get_app_config('Alignak', 'username') and \
                    not get_app_config('Alignak', 'password'):  # pragma: no cover - Not testable
                login = AppLogin()
                login.create_widget()

                if login.exec_() == QDialog.Accepted:
                    self.run()
                else:
                    logger.info('Alignak-App closes...')
                    sys.exit(0)
            elif get_app_config('Alignak', 'username') and \
                    not get_app_config('Alignak', 'password'):
                self.run()
            elif get_app_config('Alignak', 'username') and \
                    get_app_config('Alignak', 'password'):
                self.run()
            else:
                self.display_error_msg()

        else:
            self.display_error_msg()

    def reconnect_to_backend(self, error):  # pragma: no cover
        """
        Set AlignakApp in reconnect mode and try to login to Backend

        :param error: string error to display in banner
        :type error: str
        """

        self.reconnect_mode = True
        logger.warning('Application reconnecting MODE: %s', self.reconnecting)
        send_banner('ERROR', _('Alignak Backend seems unreachable ! %s') % error, duration=5000)
        timer = QTimer(self)

        def connect_to_backend():
            """Try to log in to Backend"""
            try:
                connect = app_backend.login()
                assert connect
                # If connect, reconnecting is disable
                timer.stop()
                logger.info('Connection restored : %s', connect)
                send_banner(
                    'OK',
                    _('Connection with the Backend has been restored ! You are logged in again'),
                    duration=5000
                )
                self.reconnect_mode = False
            except AssertionError:
                send_banner(
                    'ERROR',
                    _('Backend is still unreachable... Alignak-app is trying to connect'),
                    duration=5000
                )
                logger.error('Backend is still unreachable...')

        if timer.isActive():
            pass
        else:
            timer.start(10000)
            timer.timeout.connect(connect_to_backend)

    def run(self):  # pragma: no cover
        """
        Start all Alignak-app processes and create AppBackend if connection by config file.

        """

        app_backend.login()

        # Check if connected
        if app_backend.connected:
            # Send Welcome Banner
            send_banner(
                'OK',
                _('Welcome %s, you are connected to Alignak Backend') %
                app_backend.user['username'],
                duration=10000
            )

            if 'token' not in app_backend.user:
                app_backend.user['token'] = app_backend.backend.token

            # Dashboard
            self.dashboard = Dashboard()
            self.dashboard.initialize()

            # TrayIcon
            self.tray_icon = TrayIcon(QIcon(get_image_path('icon')))
            self.tray_icon.build_menu(self.dashboard)
            self.tray_icon.show()

            # Give ALignakApp for AppBackend reconnecting mode
            app_backend.app = self

            # Start Notifier which will interrogate the backend periodically
            self.notifier = AppNotifier()
            self.notifier.initialize(app_backend, self.tray_icon, self.dashboard)

            self.notifier_timer.start(self.notifier.interval)
            self.notifier_timer.timeout.connect(self.notifier.check_data)

            # Connect reconnectingmode for AppBackend
            self.reconnecting.connect(self.reconnect_to_backend)
        else:
            # In case of data provided in config file fails
            send_banner(
                'WARN',
                _('The application fails to connect with the information provided'
                  ' in the configuration file. Please enter your login details!'),
                duration=10000
            )
            login = AppLogin()
            login.create_widget()

            if login.exec_() == QDialog.Accepted:
                self.run()
            else:
                logger.info('Alignak-App closes...')
                sys.exit(0)

    @staticmethod
    def display_error_msg():  # pragma: no cover
        """
        Display a QMessageBox error in case app fail to start

        """

        logger.error('Something seems wrong in your configuration.'
                     'Please configure Alignak-app before starting it. '
                     'And make sure the backend is available')

        QMessageBox.critical(
            None,
            _('Configuration / Connection ERROR'),
            _(
                'Something seems wrong in your configuration. '
                'Please configure Alignak-app before starting it. '
                'And make sure the backend is available'
            )
        )
        sys.exit()
