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
    Login manage login form
"""

from logging import getLogger

from alignak_app import __short_version__
from alignak_app.core.backend import AppBackend, Backend
from alignak_app.core.utils import get_app_config, set_app_config, init_config
from alignak_app.core.utils import get_css, get_image_path
from alignak_app.widgets.banner import send_banner


try:
    __import__('PyQt5')
    from PyQt5.QtWidgets import QWidget, QDialog  # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QPushButton, QGridLayout  # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout  # pylint: disable=no-name-in-module
    from PyQt5.Qt import QLineEdit, Qt, QIcon, QLabel, QPixmap  # pylint: disable=no-name-in-module
except ImportError:  # pragma: no cover
    from PyQt4.Qt import QDialog, QWidget  # pylint: disable=import-error
    from PyQt4.Qt import QPushButton, QWidget, QGridLayout  # pylint: disable=import-error
    from PyQt4.Qt import QHBoxLayout, QVBoxLayout  # pylint: disable=import-error
    from PyQt4.Qt import QLineEdit, Qt, QIcon, QLabel, QPixmap  # pylint: disable=import-error


logger = getLogger(__name__)


class AppLogin(QDialog):
    """
        Class who create login QDialog.
    """

    def __init__(self, parent=None):
        super(AppLogin, self).__init__(parent)
        self.setWindowTitle('Login to Alignak')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(get_css())
        self.setWindowIcon(QIcon(get_image_path('icon')))
        # Fields
        self.app_backend = AppBackend()
        self.backend_url = None
        self.username_line = None
        self.password_line = None
        self.offset = None

    def showEvent(self, _):
        """ QDialog.showEvent(QShowEvent) """

        self.username_line.setFocus()

    def create_widget(self):
        """
        Create widget login

        """

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.get_logo_widget())

        title = '<b>Welcome to Alignak-app v%s</b>' % __short_version__
        main_layout.addWidget(self.get_title_widget(title))

        # Login QWidget
        login_widget = QWidget(self)
        login_layout = QGridLayout(login_widget)

        # Configuration button
        refresh_conf_btn = QPushButton()
        refresh_conf_btn.clicked.connect(init_config)
        refresh_conf_btn.setFixedSize(32, 32)
        refresh_conf_btn.setIcon(QIcon(get_image_path('refresh')))
        refresh_conf_btn.setToolTip('Reload configuration')
        login_layout.addWidget(refresh_conf_btn, 2, 1, 1, 1)

        # Server button
        server_btn = QPushButton()
        server_btn.clicked.connect(self.handle_server)
        server_btn.setFixedSize(32, 32)
        server_btn.setIcon(QIcon(get_image_path('host')))
        server_btn.setToolTip('Modify Alignak Server')
        login_layout.addWidget(server_btn, 2, 2, 1, 1)

        # Welcome text
        login_label = QLabel('Log-in to use the application')
        login_layout.addWidget(login_label, 2, 0, 1, 1)

        # Username field
        self.username_line = QLineEdit(self)
        self.username_line.setPlaceholderText('Username')
        login_layout.addWidget(self.username_line, 3, 0, 1, 3)

        # Password field
        self.password_line = QLineEdit(self)
        self.password_line.setPlaceholderText('Password')
        self.password_line.setEchoMode(QLineEdit.Password)
        login_layout.addWidget(self.password_line, 4, 0, 1, 3)

        # Login button
        login_button = QPushButton('LOGIN', self)
        login_button.clicked.connect(self.handle_login)
        login_button.setObjectName('valid')
        login_button.setMinimumHeight(30)
        login_button.setDefault(True)
        login_layout.addWidget(login_button, 5, 0, 1, 3)

        main_layout.addWidget(login_widget)
        self.setLayout(main_layout)

    def get_logo_widget(self):
        """
        Return the logo QWidget

        :return: logo QWidget
        :rtype: QWidget
        """

        logo_widget = QWidget()
        logo_widget.setFixedHeight(45)
        logo_layout = QHBoxLayout()
        logo_widget.setLayout(logo_layout)

        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(get_image_path('alignak')))
        logo_label.setFixedSize(121, 35)
        logo_label.setScaledContents(True)

        logo_layout.addWidget(logo_label, 0)

        minimize_btn = QPushButton()
        minimize_btn.setIcon(QIcon(get_image_path('minimize')))
        minimize_btn.setFixedSize(24, 24)
        minimize_btn.clicked.connect(self.showMinimized)
        logo_layout.addStretch(self.width())
        logo_layout.addWidget(minimize_btn, 1)

        maximize_btn = QPushButton()
        maximize_btn.setIcon(QIcon(get_image_path('maximize')))
        maximize_btn.setFixedSize(24, 24)
        maximize_btn.clicked.connect(self.showMaximized)
        logo_layout.addWidget(maximize_btn, 2)

        close_btn = QPushButton()
        close_btn.setIcon(QIcon(get_image_path('exit')))
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.close)
        logo_layout.addWidget(close_btn, 3)

        return logo_widget

    @staticmethod
    def get_title_widget(title):
        """
        Return the title QWidget

        :return: title QWidget
        :rtype: QWidget
        """

        title_widget = QWidget()
        title_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
        title_layout = QVBoxLayout()
        title_widget.setLayout(title_layout)
        title_widget.setFixedHeight(50)
        title_widget.setObjectName('title')

        title_label = QLabel('<h2>%s</h2>' % title)
        title_label.setObjectName('title')

        title_layout.addWidget(title_label)
        title_layout.setAlignment(title_label, Qt.AlignCenter)

        return title_widget

    def handle_login(self):
        """
        Handle for login button

        """

        username = self.username_line.text()
        password = self.password_line.text()

        self.app_backend.backend = Backend(get_app_config('Backend', 'alignak_backend'))

        resp = self.app_backend.login(str(username), str(password))

        if resp:
            send_banner('OK', 'Connected to Alignak Backend')
            self.app_backend.user['username'] = str(username)
            self.app_backend.user['token'] = str(self.app_backend.backend.token)
            self.accept()
        else:
            send_banner('WARN', 'Backend connection refused...')
            logger.warning('Connection informations are not accepted !')

    def handle_server(self):
        """
        Handle for server button

        """

        server_dialog = QDialog(self)
        server_dialog.setWindowTitle('Server Configuration')
        server_dialog.setMinimumSize(250, 100)

        layout = QGridLayout()
        server_dialog.setLayout(layout)

        # Description
        desc_label = QLabel(
            '<h3>Alignak Backend</h3><p>Here you can define alignak server url.</p>'
            '<b>Be sure to enter a valid address</b>'
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label, 0, 0, 1, 3)

        # Server URL
        url_desc = QLabel('Server')
        layout.addWidget(url_desc, 1, 0, 1, 1)

        server_url = QLineEdit()
        server_url.setPlaceholderText('alignak backend url')
        server_url.setText(get_app_config('Backend', 'alignak_url'))
        layout.addWidget(server_url, 1, 1, 1, 2)

        # Server Port
        port_desc = QLabel('Port')
        layout.addWidget(port_desc, 2, 0, 1, 1)

        server_port = QLineEdit()
        server_port.setPlaceholderText('alignak backend port')
        cur_port = get_app_config('Backend', 'alignak_backend').split(':')[2]
        server_port.setText(cur_port)
        layout.addWidget(server_port, 2, 1, 1, 2)

        # Valid Button
        valid_btn = QPushButton('Valid')
        valid_btn.clicked.connect(server_dialog.accept)
        layout.addWidget(valid_btn, 3, 0, 1, 3)

        if server_dialog.exec_() == QDialog.Accepted:
            backend_url = '%(alignak_url)s:' + str(server_port.text()).rstrip()
            set_app_config('Backend', 'alignak_backend', backend_url)
            set_app_config('Backend', 'alignak_url', str(server_url.text()).rstrip())

    def mousePressEvent(self, event):
        """ QWidget.mousePressEvent(QMouseEvent) """

        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        """ QWidget.mousePressEvent(QMouseEvent) """

        try:
            x = event.globalX()
            y = event.globalY()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.move(x - x_w, y - y_w)
        except AttributeError as e:
            logger.warning('Move Event %s: %s', self.objectName(), str(e))
