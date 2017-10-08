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
    ItemDaemon manage creation of daemon item
"""


from logging import getLogger

from alignak_app.items.item_model import ItemModel


logger = getLogger(__name__)


class Daemon(ItemModel):
    """
        Class who create a daemon item
    """

    def __init__(self):
        super(Daemon, self).__init__()
        self.item_type = 'alignakdaemon'

    @staticmethod
    def get_request_model():
        """
        Return the request model for alignakdaemon requests

        :return: request model for alignakdaemon endpoint
        :rtype: dict
        """

        daemons_projection = [
            'alive', 'type', 'name', 'reachable', 'spare', 'address', 'port', 'passive',
            'last_check'
        ]

        request_model = {
            'endpoint': 'alignakdaemon',
            'params': None,
            'projection': daemons_projection
        }

        return request_model

    @staticmethod
    def get_daemons_names():
        """
        Returns all the names of daemons

        :return: all the names of daemons
        :rtype: list
        """

        return [
            'poller',
            'receiver',
            'reactionner',
            'arbiter',
            'scheduler',
            'broker'
        ]
