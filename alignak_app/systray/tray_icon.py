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
    Tray_icon manage the creation of Application menus.
"""

import sys
import webbrowser
from logging import getLogger

from alignak_app.core.utils import get_app_config, get_image_path, init_config
from alignak_app.core.notifier import AppNotifier
from alignak_app.synthesis.synthesis import Synthesis
from alignak_app.systray.qactions_factory import QActionFactory
from alignak_app.widgets.about import AppAbout
from alignak_app.widgets.status import AlignakStatus
from alignak_app.widgets.banner import send_banner

try:
    __import__('PyQt5')
    from PyQt5.QtWidgets import QSystemTrayIcon  # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QMenu  # pylint: disable=no-name-in-module
    from PyQt5.QtGui import QIcon  # pylint: disable=no-name-in-module
    from PyQt5.Qt import QObject, pyqtSignal  # pylint: disable=no-name-in-module
except ImportError:  # pragma: no cover
    try:
        __import__('PyQt4')
        from PyQt4.Qt import QSystemTrayIcon  # pylint: disable=import-error
        from PyQt4.Qt import QMenu  # pylint: disable=import-error
        from PyQt4.QtGui import QIcon  # pylint: disable=import-error
        from PyQt4.Qt import QObject, pyqtSignal  # pylint: disable=import-error
    except ImportError:
        sys.exit('\nYou must have PyQt installed to run this app.\nPlease read the doc.')


logger = getLogger(__name__)


class TrayIcon(QSystemTrayIcon):
    """
        Class who create QMenu and QAction.
    """

    update_tray = pyqtSignal(AppNotifier)

    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.menu = QMenu(parent)
        self.hosts_menu = QMenu(self.menu)
        self.hosts_menu.setIcon(QIcon(get_image_path('host')))
        self.services_menu = QMenu(self.menu)
        self.services_menu.setIcon(QIcon(get_image_path('service')))
        self.qaction_factory = QActionFactory()
        self.alignak_status = None
        self.app_about = None
        self.synthesis = None

    def build_menu(self, app_backend, dashboard):
        """
        Initialize and create each action of menu.

        :param app_backend: AppBackend object
        :type app_backend: alignak_app.core.backend.AppBackend
        :param dashboard: Dashboard QWidget
        :type dashboard: alignak_app.dashboard.app_dashboard.Dashboard
        """

        # Create actions
        self.create_synthesis_action(app_backend)
        self.create_dashboard_action(dashboard)
        self.create_status_action(app_backend)
        self.menu.addSeparator()

        self.create_hosts_actions()
        self.create_services_actions()
        self.menu.addSeparator()

        self.create_reload_configuration()
        self.create_about_action()
        self.menu.addSeparator()

        self.create_quit_action()

        self.setContextMenu(self.menu)

        self.update_tray.connect(self.apply_changes)

    def apply_changes(self, sender):
        """
        TODO
        :return:
        """

        try:
            assert isinstance(sender, AppNotifier)
        except TypeError as e:
            logger.error('Bad object received: %s', e)

    def create_dashboard_action(self, dashboard):
        """
        Create dashboard action

        :param dashboard: Dashboard QWidget
        :type dashboard: alignak_app.dashboard.app_dashboard.Dashboard
        """

        logger.info('Create Dashboard action')

        self.qaction_factory.create(
            'dashboard',
            'Dashboard',
            self
        )

        self.qaction_factory.get('dashboard').triggered.connect(dashboard.app_widget.show)

        self.menu.addAction(self.qaction_factory.get('dashboard'))

    def create_hosts_actions(self):
        """
        Create hosts actions.

        """

        logger.info('Create Host Actions')

        self.hosts_menu.setTitle('Hosts (N/A)')

        self.qaction_factory.create(
            'hosts_up',
            'Hosts UP, Wait...',
            self.hosts_menu
        )
        self.qaction_factory.get('hosts_up').triggered.connect(self.open_url)

        self.qaction_factory.create(
            'hosts_unreach',
            'Hosts UNREACHABLE, Wait...',
            self.hosts_menu
        )
        self.qaction_factory.get('hosts_unreach').triggered.connect(self.open_url)

        self.qaction_factory.create(
            'hosts_down',
            'Hosts DOWN, Wait...',
            self.hosts_menu
        )
        self.qaction_factory.get('hosts_down').triggered.connect(self.open_url)

        self.hosts_menu.addSeparator()

        self.qaction_factory.create(
            'acknowledged',
            'Hosts ACKNOWLEDGE, Wait...',
            self.hosts_menu
        )

        self.qaction_factory.create(
            'downtime',
            'Hosts DOWNTIME, Wait...',
            self.hosts_menu
        )

        # Add hosts actions to menu
        self.hosts_menu.addAction(self.qaction_factory.get('hosts_up'))
        self.hosts_menu.addAction(self.qaction_factory.get('hosts_unreach'))
        self.hosts_menu.addAction(self.qaction_factory.get('hosts_down'))
        self.hosts_menu.addAction(self.qaction_factory.get('hosts_acknowledged'))
        self.hosts_menu.addAction(self.qaction_factory.get('hosts_downtime'))

        self.menu.addMenu(self.hosts_menu)

    def create_services_actions(self):
        """
        Create services actions.

        """

        logger.info('Create Service Actions')

        self.services_menu.setTitle('Services (N/A)')

        self.qaction_factory.create(
            'services_ok',
            'Services OK, Wait...',
            self
        )
        self.qaction_factory.get('services_ok').triggered.connect(self.open_url)

        self.qaction_factory.create(
            'services_warning',
            'Services WARNING, Wait...',
            self.services_menu
        )
        self.qaction_factory.get('services_warning').triggered.connect(self.open_url)

        self.qaction_factory.create(
            'services_critical',
            'Services CRITICAL, Wait...',
            self.services_menu
        )
        self.qaction_factory.get('services_critical').triggered.connect(self.open_url)

        self.qaction_factory.create(
            'services_unknown',
            'Services UNKNOWN, Wait...',
            self.services_menu
        )
        self.qaction_factory.get('services_unknown').triggered.connect(self.open_url)

        self.qaction_factory.create(
            'services_unreachable',
            'Services UNREACHABLE, Wait...',
            self.services_menu
        )

        self.services_menu.addSeparator()

        self.qaction_factory.create(
            'acknowledged',
            'Services ACKNOWLEDGE, Wait...',
            self.services_menu
        )

        self.qaction_factory.create(
            'downtime',
            'Services DOWNTIME, Wait...',
            self.services_menu
        )

        # Add services actions to menu
        self.services_menu.addAction(self.qaction_factory.get('services_ok'))
        self.services_menu.addAction(self.qaction_factory.get('services_warning'))
        self.services_menu.addAction(self.qaction_factory.get('services_critical'))
        self.services_menu.addAction(self.qaction_factory.get('services_unknown'))
        self.services_menu.addAction(self.qaction_factory.get('services_unreachable'))
        self.services_menu.addAction(self.qaction_factory.get('services_acknowledged'))
        self.services_menu.addAction(self.qaction_factory.get('services_downtime'))

        self.menu.addMenu(self.services_menu)

    def create_synthesis_action(self, app_backend):
        """
        Create Synthesis QWidget and "synthesis view" action

        :param app_backend: Backend data
        :type app_backend: AppBackend
        """

        self.qaction_factory.create(
            'database',
            'Host Synthesis View',
            self
        )

        self.synthesis = Synthesis()
        self.synthesis.initialize(app_backend)

        self.qaction_factory.get('database').triggered.connect(
            self.synthesis.app_widget.show_widget
        )

        self.menu.addAction(self.qaction_factory.get('database'))

        logger.info('Create Synthesis Action')

    def create_status_action(self, app_backend):
        """
        Create AlignakStatus QWidget and "status" action

        :param app_backend: AppBackend data
        :type app_backend: AppBackend
        """

        self.qaction_factory.create(
            'icon',
            'Alignak Status',
            self
        )

        self.alignak_status = AlignakStatus()
        self.alignak_status.create_status(app_backend)
        self.qaction_factory.get('icon').triggered.connect(self.alignak_status.show_states)

        self.menu.addAction(self.qaction_factory.get('icon'))

        logger.info('Create Status Action')

    def create_reload_configuration(self):
        """
        Create "reload" action

        """

        self.qaction_factory.create(
            'refresh',
            'Reload Configuration',
            self
        )

        self.qaction_factory.get('refresh').triggered.connect(self.reload_configuration)

        self.menu.addAction(self.qaction_factory.get('refresh'))

        logger.info('Create Reload Action')

    def create_about_action(self):
        """
        Create AppAbout QWidget and "about" action.

        """

        self.app_about = AppAbout()
        self.app_about.create_window()

        self.qaction_factory.create(
            'about',
            'About',
            self
        )

        self.qaction_factory.get('about').triggered.connect(self.app_about.show_about)

        self.menu.addAction(self.qaction_factory.get('about'))

        logger.info('Create About Action')

    def create_quit_action(self):
        """
        Create quit action.

        """

        logger.info('Create Quit Action')

        self.qaction_factory.create(
            'exit',
            'Quit',
            self
        )

        self.qaction_factory.get('exit').triggered.connect(self.quit_app)

        self.menu.addAction(self.qaction_factory.get('exit'))

    def update_menu_actions(self, hosts, services):
        """
        Update items Menu

        :param hosts: number of hosts UP, DOWN or UNREACHABLE
        :type hosts: dict
        :param services: number of services OK, CRITICAL, WARNING or UNKNOWN
        :type services: dict
        """

        logger.info('Update menus...')

        host_nb = hosts['up'] + \
            hosts['down'] + \
            hosts['unreachable'] + \
            hosts['downtime'] + \
            hosts['acknowledge']
        services_nb = services['ok'] + \
            services['warning'] + \
            services['critical'] + \
            services['unknown'] + \
            services['unreachable'] + \
            services['downtime'] + \
            services['acknowledge']

        if hosts['down'] != 0:
            self.hosts_menu.setIcon(QIcon(get_image_path('hosts_down')))
        elif hosts['down'] == 0 and hosts['unreachable'] > hosts['up']:
            self.hosts_menu.setIcon(QIcon(get_image_path('hosts_unreach')))
        else:
            self.hosts_menu.setIcon(QIcon(get_image_path('hosts_up')))

        self.hosts_menu.setTitle('Hosts (' + str(host_nb) + ')')

        if services['critical'] != 0:
            self.services_menu.setIcon(QIcon(get_image_path('services_critical')))
        else:
            if services['unknown'] != 0 or services['warning'] != 0:
                self.services_menu.setIcon(QIcon(get_image_path('services_warning')))
            else:
                self.services_menu.setIcon(QIcon(get_image_path('services_ok')))

        self.services_menu.setTitle('Services (' + str(services_nb) + ')')

        self.qaction_factory.get('hosts_up').setText(
            'Hosts UP (' + str(hosts['up']) + ')')
        self.qaction_factory.get('hosts_down').setText(
            'Hosts DOWN (' + str(hosts['down']) + ')')
        self.qaction_factory.get('hosts_unreach').setText(
            'Hosts UNREACHABLE (' + str(hosts['unreachable']) + ')')
        self.qaction_factory.get('hosts_acknowledged').setText(
            'Hosts ACKNOWLEDGE (' + str(hosts['acknowledge']) + ')')
        self.qaction_factory.get('hosts_downtime').setText(
            'Hosts DOWNTIME (' + str(hosts['downtime']) + ')')

        self.qaction_factory.get('services_ok').setText(
            'Services OK (' + str(services['ok']) + ')')
        self.qaction_factory.get('services_critical').setText(
            'Services CRITICAL (' + str(services['critical']) + ')')
        self.qaction_factory.get('services_warning').setText(
            'Services WARNING (' + str(services['warning']) + ')')
        self.qaction_factory.get('services_unknown').setText(
            'Services UNKNOWN (' + str(services['unknown']) + ')')
        self.qaction_factory.get('services_unreachable').setText(
            'Services UNREACHABLE (' + str(services['unreachable']) + ')')
        self.qaction_factory.get('services_acknowledged').setText(
            'Services ACKNOWLEDGE (' + str(services['acknowledge']) + ')')
        self.qaction_factory.get('services_downtime').setText(
            'Services DOWNTIME (' + str(services['downtime']) + ')')

    @staticmethod
    def quit_app():  # pragma: no cover
        """
        Quit application.

        """

        sys.exit(0)

    def open_url(self):  # pragma: no cover
        """
        Add a link to Alignak-WebUI on every menu

        """

        target = self.sender()

        webui_url = get_app_config('Alignak', 'webui')

        # Define each filter for items
        if "UP" in target.text():
            endurl = '/hosts/table?search=ls_state:UP'
        elif "DOWN" in target.text():
            endurl = '/hosts/table?search=ls_state:DOWN'
        elif "UNREACHABLE" in target.text():
            endurl = '/hosts/table?search=ls_state:UNREACHABLE'
        elif 'OK' in target.text():
            endurl = '/services/table?search=ls_state:OK'
        elif 'CRITICAL' in target.text():
            endurl = '/services/table?search=ls_state:CRITICAL'
        elif 'WARNING' in target.text():
            endurl = '/services/table?search=ls_state:WARNING'
        elif 'UNKNOWN' in target.text():
            endurl = '/services/table?search=ls_state:UNKNOWN'
        else:
            endurl = '/dashboard'

        logger.debug('Open url : ' + webui_url + endurl)
        webbrowser.open(webui_url + endurl)

    @staticmethod
    def reload_configuration():
        """
        Reload configuration

        """

        init_config()
        send_banner('INFO', 'Configuration reloaded')
