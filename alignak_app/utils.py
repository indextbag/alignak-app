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
    Application logs
"""

from logging import Formatter
from logging import DEBUG
from logging.handlers import TimedRotatingFileHandler
from string import Template

import os
import sys


def create_logger(logger):  # pragma: no cover
    """
    Create the logger for Alignak-App

    :param logger: the main logger.
    :type logger: :class:`~`
    """

    path = get_alignak_home() + '/alignak_app'

    filename = 'alignakapp.log'

    if not os.path.isdir(path):
        # noinspection PyBroadException
        try:  # pragma: no cover - not testable
            os.makedirs(path)
        except Exception:
            path = '.'

    if not os.access(path, os.W_OK):
        path = '.'

    formatter = Formatter('[%(asctime)s] - %(name)-12s - %(levelname)s - %(message)s')

    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(path, filename),
        when="D",
        interval=1,
        backupCount=6
    )

    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.setLevel(DEBUG)


def get_alignak_home():  # pragma: no cover
    """
    Return user home.
    """

    # Get HOME and USER
    if 'linux' in sys.platform or 'sunos5' in sys.platform:
        alignak_home = os.environ['HOME']
        alignak_home += '/.local'
    elif 'win32' in sys.platform:
        alignak_home = os.environ['USERPROFILE']
        alignak_home += '\\AppData\\Roaming\\Python\\'
    else:
        sys.exit('Application can\'t find the user HOME.')

    # Prevent from root user
    if 'root' in alignak_home or not alignak_home:
        sys.exit('Application can\'t find the user HOME or maybe you are connected as ROOT.')

    return alignak_home


def get_template(name, values, config):
    """
        Return content of the choosen template with its values.


    :param name: name of the template.
    :type name: str
    :param values: dict of values to substitute.
    :param config:
    :return: content of a template
    :rtype: str
    """

    tpl_content = ''

    tpl_path = get_alignak_home() \
        + config.get('Config', 'path') \
        + config.get('Config', 'tpl') \
        + '/'

    try:
        tpl_file = open(tpl_path + name)
    except FileNotFoundError as e:
        sys.exit('Failed open template : ' + str(e))

    if tpl_file:
        tpl = Template(tpl_file.read())
        tpl_content = tpl.safe_substitute(values)

    return tpl_content
