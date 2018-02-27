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
    App
    ~~~
    App manages the creation of QObjects for the whole application:

    * Creation of QObject for App Main (QMainWindow)
    * Creation of QProgressbar until the Data Manager is ready
"""

import os
import sys
import time

from logging import DEBUG, INFO
from PyQt5.Qt import QApplication, QObject, QIcon, Qt, QProgressBar, QWidget, QLabel, QVBoxLayout
from PyQt5.Qt import QTimer

from alignak_app import __application__, __version__

from alignak_app.utils.config import settings
from alignak_app.utils.logs import create_logger
from alignak_app.locales.locales import init_localization

from alignak_app.backend.backend import app_backend
from alignak_app.backend.datamanager import data_manager

from alignak_app.qthreads.threadmanager import thread_manager, BackendQThread
from alignak_app.qobjects.common.widgets import center_widget
from alignak_app.qobjects.login.login import LoginQDialog
from alignak_app.qobjects.dock.events import init_event_widget
from alignak_app.qobjects.systray.tray_icon import TrayIcon

settings.init_config()
settings.init_css()
init_localization()
logger = create_logger()


class AppProgressQWidget(QWidget):
    """
        Class who create a small widget for App start progression
    """

    def __init__(self, parent=None):
        super(AppProgressQWidget, self).__init__(parent)
        self.setWindowIcon(QIcon(settings.get_image('icon')))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(250, 80)
        self.setStyleSheet(settings.css_style)
        self.progress_bar = AppProgressBar()

    def initialize(self):
        """
        Initialize the QWidget

        """

        title_lbl = QLabel('%s - %s' % (__application__, __version__))
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setObjectName('start')
        layout = QVBoxLayout(self)

        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)
        layout.addWidget(self.progress_bar)


class AppProgressBar(QProgressBar):
    """
        AppProgressBar in busy mode with text displayed at the center.
    """

    def __init__(self):
        super(AppProgressBar, self).__init__()
        self.setRange(0, 0)
        self.setAlignment(Qt.AlignCenter)
        self._text = None

    def set_text(self, text):
        """
        Set text of QProgressBar

        :param text: text of progress bar
        :type text: str
        """

        self._text = text

    def text(self):
        """
        Overload: text(self) -> str

        :return: text of progress bar
        :rtype: str
        """

        return self._text


class AlignakApp(QObject):  # pragma: no cover
    """
        Class who build Alignak-app QObjects, initialize configurations, systray icon
        and Thread Manager.
    """

    def __init__(self):
        super(AlignakApp, self).__init__()
        self.tray_icon = None
        self.threadmanager_timer = QTimer()

    def start(self):
        """
        Start Alignak-app

        """

        logger.name = 'alignak_app'
        if settings.get_config('Log', 'debug', boolean=True):
            logger.setLevel(DEBUG)
            logger.info('- [Log Level]: DEBUG')
        else:
            logger.setLevel(INFO)
            logger.info('- [Log Level]: INFO')

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        username = None
        password = None
        if settings.get_config('Alignak', 'username'):
            username = settings.get_config('Alignak', 'username')
            password = settings.get_config('Alignak', 'password')

        while not app_backend.login(username, password):
            login = LoginQDialog()
            login.create_widget()

            if login.exec_() == login.Accepted:
                username = str(login.username_line.text())
                password = str(login.password_line.text())

        thread_to_launch = thread_manager.get_threads_to_launch()
        logger.info("Filling the database [%s]", thread_to_launch)
        thread_to_launch.remove('history')
        thread_to_launch.remove('notifications')

        launched_threads = []
        for thread in thread_to_launch:
            backend_thread = BackendQThread(thread)
            backend_thread.start()

            launched_threads.append(backend_thread)

        # Create Progress Bar
        app_progress = AppProgressQWidget()
        app_progress.initialize()
        center_widget(app_progress)
        logger.info("Preparing DataManager...")
        while data_manager.is_ready() != 'READY':
            app_progress.show()

            for _ in range(0, 100):
                t = time.time()
                while time.time() < t + 0.01:
                    status = data_manager.is_ready()
                    app_progress.progress_bar.set_text('%s' % status)
                    app.processEvents()

        app_progress.close()

        logger.info('- [ALIGNAKAPP_LOG_DIR]: %s', os.environ['ALIGNAKAPP_LOG_DIR'])
        logger.info('- [ALIGNAKAPP_USER_CFG]: %s', os.environ['ALIGNAKAPP_USER_CFG'])
        logger.info('- [ALIGNAKAPP_APP_CFG]: %s', os.environ['ALIGNAKAPP_APP_CFG'])

        init_event_widget()

        requests_interval = int(settings.get_config('Alignak-app', 'requests_interval')) * 1000
        self.threadmanager_timer.setInterval(requests_interval)
        self.threadmanager_timer.start()
        self.threadmanager_timer.timeout.connect(self.launch_threads)

        self.tray_icon = TrayIcon(QIcon(settings.get_image('icon')))
        self.tray_icon.build_menu()
        self.tray_icon.show()

        while self.quit_launched_threads(launched_threads):
            pass

        sys.exit(app.exec_())

    def quit_launched_threads(self, launched_threads):
        """
        Exit the threads that were started when the application started

        :param launch_threads: list of threads that have been launched
        :type launched_threads: list
        :return: empty list if all the threads have been left or current list
        :rtype: list
        """

        for old_thread in launched_threads:
            if old_thread.isFinished():
                old_thread.quit()
                launched_threads.remove(old_thread)

        return launched_threads

    @staticmethod
    def launch_threads():
        """
        Launch periodically threads

        """

        if app_backend.connected:
            if not thread_manager.threads_to_launch:
                thread_manager.threads_to_launch = thread_manager.get_threads_to_launch()

            # In case there is no thread running
            if thread_manager.threads_to_launch and not thread_manager.current_thread:
                cur_thread = thread_manager.threads_to_launch.pop(0)
                backend_thread = BackendQThread(cur_thread)
                backend_thread.start()

                thread_manager.current_thread = backend_thread

            # Cleaning threads who are finished
            if thread_manager.current_thread:
                if thread_manager.current_thread.isFinished():
                    logger.debug('Remove finished thread: %s',
                                 thread_manager.current_thread.thread_name)
                    thread_manager.current_thread.quit()
                    thread_manager.current_thread.wait()

                    thread_manager.current_thread = None
        else:
            logger.info('App is not connected %s', str(app_backend.connected))
            thread_manager.stop_threads()


if __name__ == '__main__':
    apptest = AlignakApp()

    apptest.start()
