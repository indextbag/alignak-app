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
    Host
    ++++
    Host manage creation of host item for backend ``host`` endpoint
"""

import json
from logging import getLogger

from alignak_app.items.item import Item

logger = getLogger(__name__)


class Host(Item):
    """
        Class who create a host item
    """

    def __init__(self):
        super(Host, self).__init__()
        self.item_type = 'host'

    @staticmethod
    def get_request_model():
        """
        Return the request model for host requests

        :return: request model for host endpoint
        :rtype: dict
        """

        hosts_projection = [
            'name', 'alias', 'ls_state', '_id', 'ls_acknowledged', 'ls_downtimed', 'ls_last_check',
            'ls_output', 'address', 'business_impact', 'notes', '_realm', 'passive_checks_enabled',
            'active_checks_enabled', '_overall_state_id'
        ]

        request = {
            'endpoint': 'host',
            'params': {'where': json.dumps({'_is_template': False})},
            'projection': hosts_projection
        }

        return request

    @staticmethod
    def get_available_icons():
        """
        Return list of available icons for a Host item

        :return: list of available icons for Host
        :rtype: list
        """

        return ['hosts_up', 'hosts_unreachable', 'hosts_down', 'acknowledge',
                'downtime', 'hosts_not_monitored']

    def get_display_name(self):
        """
        Return alias or name if available

        :return: name or alias
        :rtype: str
        """

        if 'alias' in self.data:
            return self.data['alias'].title()

        return self.name.title()

    def is_problem(self):
        """
        Return True if host is a problem, else return False

        :return: if host in problem or not
        :rtype: bool
        """

        if self.data['ls_state'] in ['DOWN', 'UNREACHABLE'] and not self.data['ls_acknowledged'] \
                and not self.data['ls_downtimed']:
            return True

        return False
