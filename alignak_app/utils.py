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

import os
import sys

from logging import getLogger
from logging import Formatter
from logging import DEBUG
from logging.handlers import TimedRotatingFileHandler

from string import Template
import configparser

logger = getLogger(__name__)


# Application Logger
def create_logger(main_logger):  # pragma: no cover
    """
    Create the logger for Alignak-App

    :param main_logger: the main logger.
    :type main_logger: :class:`~`
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

    main_logger.addHandler(file_handler)
    main_logger.setLevel(DEBUG)


# Application Home
def get_alignak_home():
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

# Application Configuration

# Global variable, access by funtions
app_config = None


def set_app_config():
    """
    Create app_config

    """

    config_file = get_alignak_home() + '/alignak_app/settings.cfg'

    global app_config  # pylint: disable=global-statement
    app_config = configparser.ConfigParser()

    logger.info('Read configuration file...')
    if os.path.isfile(config_file):
        app_config.read(config_file)
        logger.info('Configuration file is OK.')
    else:
        logger.error('Configuration file is missing in [' + config_file + '] !')
        sys.exit('Configuration file is missing in [' + config_file + '] !')


def get_app_config():
    """
    Return global application configuration

    """

    return app_config


# Application Templates
def get_template(name, values):
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
        + app_config.get('Config', 'path') \
        + app_config.get('Config', 'tpl') \
        + '/'

    try:
        tpl_file = open(tpl_path + name)
    except IOError as e:
        sys.exit('Failed open template : ' + str(e))

    if tpl_file:
        tpl = Template(tpl_file.read())
        tpl_content = tpl.safe_substitute(values)

    return tpl_content


def get_img_path():
    """
    Get the path for all icons

    :return: path of icon
    :rtype: str
    """
    img_path = get_alignak_home() \
        + app_config.get('Config', 'path') \
        + app_config.get('Config', 'img') \
        + '/'

    return img_path