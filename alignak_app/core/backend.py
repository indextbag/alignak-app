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
    App Backend manage connexion and access to app_backend.
"""

import json
from logging import getLogger

from alignak_backend_client.client import Backend, BackendException

from alignak_app.core.utils import get_app_config

logger = getLogger(__name__)


class AppBackend(object):
    """
        Class who collect informations with Backend-Client and returns data for
        Alignak-App.
    """

    def __init__(self):
        self.backend = None
        self.user = {}
        self.connected = False
        self.app = None

    def login(self, username=None, password=None):
        """
        Connect to app_backend with credentials in settings.cfg.

        :param username: name or token of user
        :type username: str
        :param password: password of user. If token given, this parameter is useless
        :type password: str
        :return: True if connected or False if not
        :rtype: bool
        """

        # Credentials
        if not username and not password:
            if self.user:
                username = self.user['token']
            else:
                username = get_app_config('Alignak', 'username')
                password = get_app_config('Alignak', 'password')

        # Create Backend object
        backend_url = get_app_config('Alignak', 'backend')
        processes = int(get_app_config('Alignak', 'processes'))

        self.backend = Backend(backend_url, processes=processes)

        logger.debug('Backend URL : %s', backend_url)
        logger.info('Try to connect to app_backend...')

        if username and password:
            # Username & password : not recommended, without "widgets.login.py" form.
            try:
                self.connected = self.backend.login(username, password)
                if self.connected:
                    self.user['username'] = username
                    self.user['token'] = self.backend.token
                logger.info('Connection by password: %s', str(self.connected))
            except BackendException as e:  # pragma: no cover
                logger.error('Connection to Backend has failed: %s', str(e))
        elif username and not password:
            # Username as token : recommended
            self.backend.authenticated = True
            if self.user:
                self.backend.token = self.user['token']
            else:
                self.backend.token = username
                self.user['token'] = username

            # Make backend connected to test token
            self.connected = True
            user = self.get_user(projection=['name'])

            self.connected = bool(user)
            if not self.connected:
                return False

            self.user['username'] = user['name']
            logger.info('Connection by token: %s', str(self.connected))
        else:
            # Else exit
            logger.error(
                'Connection to Backend has failed.\nCheck [Backend] section in configuration file.'
            )
            return False

        return self.connected

    def get(self, endpoint, params=None, projection=None, all_items=False):
        """
        GET on alignak Backend REST API.

        :param endpoint: endpoint (API URL)
        :type endpoint: str
        :param params: dict of parameters for the app_backend API
        :type params: dict|None
        :param projection: list of field to get, if None, get all
        :type projection: list|None
        :param all_items: make GET on all items
        :type all_items: bool
        :return desired request of app_backend
        :rtype: dict
        """

        request = None

        if params is None:
            params = {'max_results': 50}
        if projection is not None:
            generate_proj = {}
            for field in projection:
                generate_proj[field] = 1
            params['projection'] = json.dumps(generate_proj)

        if self.connected:
            # Request
            try:
                if not all_items:
                    request = self.backend.get(
                        endpoint,
                        params
                    )
                else:
                    request = self.backend.get_all(
                        endpoint,
                        params
                    )
                logger.debug('GET: %s', endpoint)
                logger.debug('..with params: %s', str(params))
                logger.debug('...Response > %s', str(request['_status']))
            except BackendException as e:
                logger.error('GET failed: %s', str(e))
                logger.error('...Request: %s', str(request))
                try:
                    request = self.backend.get(
                        endpoint,
                        params
                    )
                    logger.debug('GET (Retry): %s', endpoint)
                    logger.debug('..with params: %s', str(params))
                    logger.debug('...Response > %s', str(request['_status']))
                except BackendException as e:
                    logger.error('GET failed: %s', str(e))
                    logger.error('...Request: %s', str(request))
                    logger.warning('Application checks the connection with the Backend...')
                    self.connected = False
                    if self.app:
                        if not self.app.reconnect_mode:
                            self.app.reconnecting.emit(str(e))
                    return request

        return request

    def post(self, endpoint, data, headers=None):  # pragma: no cover - Post already test by client
        """
        POST on alignak Backend REST API

        :param endpoint: endpoint (API URL)
        :type endpoint: str
        :param data: properties of item to create | add
        :type data: dict
        :param headers: headers (example: Content-Type)
        :type headers: dict|None
        :return: response (creation information)
        :rtype: dict
        """

        request = None

        if self.connected:
            try:
                request = self.backend.post(endpoint, data, headers=headers)
                logger.debug('POST on %s', endpoint)
                logger.debug('..with data: %s', str(data))
                logger.debug('...Response > %s', str(request['_status']))
            except BackendException as e:
                logger.error('POST failed: %s', str(e))
                logger.warning('Application checks the connection with the Backend...')
                self.connected = False
                if not self.app.reconnect_mode:
                    self.app.reconnecting.emit(self, str(e))
                return request

        return request

    def patch(self, endpoint, data, headers):
        """
        PATCH on alignak Backend REST API

        :param endpoint:
        :param data:
        :param headers:
        :return:
        """

        request = None

        if self.connected:
            try:
                request = self.backend.patch(endpoint, data, headers=headers, inception=True)
                logger.debug('PATCH on %s', endpoint)
                logger.debug('..with data: %s', str(data))
                logger.debug('...with headers: %s', str(headers))
                logger.debug('....Response > %s', str(request['_status']))
            except BackendException as e:  # pragma: no cover
                logger.error('PATCH failed: %s', str(e))
                logger.warning('Application checks the connection with the Backend...')
                self.connected = False
                if not self.app.reconnect_mode:
                    self.app.reconnecting.emit(str(e))
                return False

        if request['_status'] == 'OK':
            return True

    def get_host(self, key, value, projection=None):
        """
        Return the host corresponding to "key"/"value" pair

        :param key: key corresponding to value
        :type key: str
        :param value: value of key
        :type value: str
        :param projection: list of field to get, if None, get all
        :type projection: list|None
        :return: None if not found or item dict
        :rtype: dict|None
        """

        params = {'where': json.dumps({'_is_template': False, key: value})}

        hosts = self.get('host', params, projection=projection)

        if hosts and hosts['_items']:
            wanted_host = hosts['_items'][0]
        else:
            wanted_host = None

        return wanted_host

    def get_service(self, host_id, service_id, projection=None):
        """
        Returns the desired service of the specified host

        :param host_id: "_id" of host
        :type host_id: str
        :param service_id: "_id" of wanted service
        :type service_id: str
        :param projection: list of field to get, if None, get all
        :type projection: list|None
        :return: wanted service
        :rtype: dict
        """

        params = {
            'where': json.dumps({
                '_is_template': False,
                'host': host_id
            })
        }

        services = self.get('service', params=params, projection=projection)

        wanted_service = None
        if services:
            if services['_items']:
                wanted_service = services['_items'][0]
            for service in services['_items']:
                if service['_id'] == service_id:
                    wanted_service = service

        return wanted_service

    def get_host_with_services(self, host_name):
        """
        Returns the desired host and all its services

        :param host_name: desired host
        :type host_name: str
        :return dict with host data and its associated services
        :rtype: dict
        """

        host_data = None

        host_projection = ['name', 'alias', 'ls_state', '_id', 'ls_acknowledged', 'ls_downtimed',
                           'ls_last_check', 'ls_output', 'address', 'business_impact', 'parents',
                           'ls_last_state_changed']
        host = self.get_host('name', host_name, projection=host_projection)

        if host:
            params = {
                'where': json.dumps({
                    '_is_template': False,
                    'host': host['_id']
                })
            }
            service_projection = ['name', 'alias', 'display_name', 'ls_state', 'ls_acknowledged',
                                  'ls_downtimed', 'ls_last_check', 'ls_output', 'business_impact',
                                  'customs', '_overall_state_id', 'aggregation',
                                  'ls_last_state_changed']
            services = self.get('service', params=params, projection=service_projection)

            services_host = None
            if services:
                services_host = services['_items']

            host_data = {
                'host': host,
                'services': services_host
            }

        return host_data

    def get_user(self, projection=None):
        """
        Get current user. The token must already be acquired

        :param projection: list of field to get, if None, get all
        :type projection: list|None
        :return user items
        :rtype dict|None
        """

        params = {
            'where': json.dumps({
                'token': self.user['token']
            })
        }

        if projection is not None:
            generate_proj = {}
            for field in projection:
                generate_proj[field] = 1
            params['projection'] = json.dumps(generate_proj)

        user = self.get('user', params, projection=projection)

        if user:
            return user['_items'][0]

        return None

    def synthesis_count(self):
        """
        Get on "synthesis" endpoint and return the states of hosts and services

        :return: states of hosts and services.
        :rtype: dict
        """

        states = {
            'hosts': {
                'up': 0,
                'down': 0,
                'unreachable': 0,
                'acknowledge': 0,
                'downtime': 0
            },
            'services': {
                'ok': 0,
                'critical': 0,
                'unknown': 0,
                'warning': 0,
                'unreachable': 0,
                'acknowledge': 0,
                'downtime': 0
            }
        }
        live_synthesis = self.get('livesynthesis')

        if live_synthesis:
            for realm in live_synthesis['_items']:
                states['hosts']['up'] += realm['hosts_up_soft']
                states['hosts']['up'] += realm['hosts_up_hard']

                states['hosts']['unreachable'] += realm['hosts_unreachable_soft']
                states['hosts']['unreachable'] += realm['hosts_unreachable_hard']

                states['hosts']['down'] += realm['hosts_down_soft']
                states['hosts']['down'] += realm['hosts_down_hard']

                states['hosts']['acknowledge'] += realm['hosts_acknowledged']
                states['hosts']['downtime'] += realm['hosts_in_downtime']

                states['services']['ok'] += realm['services_ok_soft']
                states['services']['ok'] += realm['services_ok_hard']

                states['services']['warning'] += realm['services_warning_soft']
                states['services']['warning'] += realm['services_warning_hard']

                states['services']['critical'] += realm['services_critical_soft']
                states['services']['critical'] += realm['services_critical_hard']

                states['services']['unknown'] += realm['services_unknown_soft']
                states['services']['unknown'] += realm['services_unknown_hard']

                states['services']['unreachable'] += realm['services_unreachable_soft']
                states['services']['unreachable'] += realm['services_unreachable_hard']

                states['services']['acknowledge'] += realm['services_acknowledged']
                states['services']['downtime'] += realm['services_in_downtime']

        logger.info('Store current states...')

        return states

    def user_can_submit_commands(self):
        """
        Return if user can submit command or not

        :return: if user can submit command
        :rtype: bool
        """

        params = {
            'where': json.dumps({'name': self.user['username']}),
            'projection': json.dumps({'can_submit_commands': 1})
        }

        user = self.get('user', params)

        if user:
            return user['_items'][0]['can_submit_commands']

        return False

    def get_host_history(self, host_id):
        """
        Return history of an host

        :param host_id: id of host
        :type host_id: str
        :return: dict of history
        :rtype: dict
        """

        params = {
            'where': json.dumps({'host': host_id}),
            'sort': '-_id',
            'projection': json.dumps({'service_name': 1, 'message': 1, 'type': 1})
        }

        history = self.get('history', params)

        if history:
            return history['_items']

        return {}


app_backend = AppBackend()
