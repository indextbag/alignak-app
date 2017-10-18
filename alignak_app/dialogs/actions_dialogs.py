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
    Actions display QDialog's for actions : Acknowledge and Downtime
"""

import datetime
from logging import getLogger

from PyQt5.Qt import QDialog, QWidget, QTime, QVBoxLayout, Qt  # pylint: disable=no-name-in-module
from PyQt5.Qt import QGridLayout, QTimeEdit, QDateTimeEdit  # pylint: disable=no-name-in-module
from PyQt5.Qt import QPixmap, QCheckBox  # pylint: disable=no-name-in-module
from PyQt5.Qt import QPushButton, QLabel, QTextEdit, QIcon  # pylint: disable=no-name-in-module

from alignak_app.core.utils import get_image_path, get_css
from alignak_app.widgets.common.utils_widgets import get_logo_widget, center_widget

logger = getLogger(__name__)


class AckQDialog(QDialog):
    """
        Class who create Acknowledge QDialog for hosts/services
    """

    def __init__(self, parent=None):
        super(AckQDialog, self).__init__(parent)
        self.setWindowTitle(_('Request an Acknowledge'))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(get_css())
        self.setWindowIcon(QIcon(get_image_path('icon')))
        self.setMinimumSize(360, 460)
        self.setObjectName('dialog')
        # Fields
        self.sticky = True
        self.notify = False
        self.ack_comment_edit = None
        self.offset = None

    def initialize(self, item_type, item_name, comment):  # pylint: disable=too-many-locals
        """
        Initialize Acknowledge QDialog

        :param item_type: type of item to acknowledge : host | service
        :type item_type: str
        :param item_name: name of the item to acknowledge
        :type item_name: str
        :param comment: the default comment of action
        :type comment: str
        """

        # Main layout
        center_widget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(get_logo_widget(self))

        ack_widget = QWidget()
        ack_widget.setObjectName('dialog')
        ack_layout = QGridLayout(ack_widget)

        ack_title = QLabel(_('Request an acknowledge'))
        ack_layout.addWidget(ack_title, 0, 0, 1, 2)

        host_label = QLabel('%s: %s' % (item_type.capitalize(), item_name))
        ack_layout.addWidget(host_label, 1, 0, 1, 1)

        sticky_label = QLabel(_('Acknowledge is sticky:'))
        sticky_label.setObjectName('actions')
        ack_layout.addWidget(sticky_label, 2, 0, 1, 1)

        sticky_checkbox = QCheckBox()
        sticky_checkbox.setObjectName('actions')
        sticky_checkbox.setChecked(self.sticky)
        sticky_checkbox.setFixedSize(18, 18)
        ack_layout.addWidget(sticky_checkbox, 2, 1, 1, 1)

        sticky_info = QLabel(
            _(
                'If checked, '
                'the acknowledge will remain until the element returns to an "OK" state.'
            )
        )
        sticky_info.setWordWrap(True)
        ack_layout.addWidget(sticky_info, 3, 0, 1, 2)

        notify_label = QLabel(_('Acknowledge notifies:'))
        notify_label.setObjectName('actions')
        ack_layout.addWidget(notify_label, 4, 0, 1, 1)

        notify_checkbox = QCheckBox()
        notify_checkbox.setObjectName('actions')
        notify_checkbox.setChecked(self.notify)
        notify_checkbox.setFixedSize(18, 18)
        ack_layout.addWidget(notify_checkbox, 4, 1, 1, 1)

        notify_info = QLabel(
            _('If checked, a notification will be sent out to the concerned contacts.')
        )
        notify_info.setWordWrap(True)
        ack_layout.addWidget(notify_info, 5, 0, 1, 2)

        ack_comment = QLabel(_('Acknowledge comment:'))
        ack_comment.setObjectName('actions')
        ack_layout.addWidget(ack_comment, 6, 0, 1, 1)

        self.ack_comment_edit = QTextEdit()
        self.ack_comment_edit.setText(comment)
        self.ack_comment_edit.setMaximumHeight(60)
        ack_layout.addWidget(self.ack_comment_edit, 7, 0, 1, 2)

        request_btn = QPushButton(_('REQUEST ACKNOWLEDGE'), self)
        request_btn.clicked.connect(self.accept)
        request_btn.setObjectName('valid')
        request_btn.setMinimumHeight(30)
        request_btn.setDefault(True)
        ack_layout.addWidget(request_btn, 8, 0, 1, 2)

        main_layout.addWidget(ack_widget)

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


class DownQDialog(QDialog):
    """
        Class who create Downtime QDialog for hosts/services
    """

    def __init__(self, parent=None):
        super(DownQDialog, self).__init__(parent)
        self.setWindowTitle(_('Request a Downtime'))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(get_css())
        self.setWindowIcon(QIcon(get_image_path('icon')))
        self.setMinimumSize(360, 460)
        self.setObjectName('dialog')
        # Fields
        self.fixed = True
        self.duration = QTimeEdit()
        self.start_time = QDateTimeEdit()
        self.end_time = QDateTimeEdit()
        self.comment_edit = QTextEdit()
        self.offset = None

    def initialize(self, item_type, item_name, comment):  # pylint: disable=too-many-locals
        """
        Initialize Downtime QDialog

        :param item_type: type of item to acknowledge : host | service
        :type item_type: str
        :param item_name: name of the item to acknowledge
        :type item_name: str
        :param comment: the default comment of action
        :type comment: str
        """

        # Main layout
        center_widget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(get_logo_widget(self))

        downtime_widget = QWidget()
        downtime_widget.setObjectName('dialog')
        downtime_layout = QGridLayout(downtime_widget)

        ack_title = QLabel(_('Request a downtime'))
        downtime_layout.addWidget(ack_title, 0, 0, 1, 3)

        host_label = QLabel('%s: %s' % (item_type.capitalize(), item_name))
        downtime_layout.addWidget(host_label, 1, 0, 1, 1)

        options_label = QLabel(_('Downtime options:'))
        options_label.setObjectName('actions')
        downtime_layout.addWidget(options_label, 2, 0, 1, 1)

        fixed_checkbox = QCheckBox()
        fixed_checkbox.setObjectName('actions')
        fixed_checkbox.setChecked(self.fixed)
        fixed_checkbox.setFixedSize(18, 18)
        downtime_layout.addWidget(fixed_checkbox, 2, 1, 1, 1)

        fixed_label = QLabel(_('Fixed'))
        fixed_label.setObjectName('actions')
        downtime_layout.addWidget(fixed_label, 2, 2, 1, 1)

        fixed_info = QLabel(
            _(
                'If checked, downtime will start and end at the times specified'
                ' by the “start time” and “end time” fields.'
            )
        )
        fixed_info.setWordWrap(True)
        downtime_layout.addWidget(fixed_info, 3, 0, 1, 3)

        duration_label = QLabel(_('Duration'))
        duration_label.setObjectName('actions')
        downtime_layout.addWidget(duration_label, 4, 0, 1, 1)

        duration_clock = QLabel()
        duration_clock.setPixmap(QPixmap(get_image_path('clock')))
        downtime_layout.addWidget(duration_clock, 4, 1, 1, 1)
        duration_clock.setFixedSize(16, 16)
        duration_clock.setScaledContents(True)

        self.duration.setTime(QTime(4, 00))
        self.duration.setDisplayFormat("HH'h'mm")
        downtime_layout.addWidget(self.duration, 4, 2, 1, 1)

        duration_info = QLabel(
            _('Sets the duration if it is a non-fixed downtime.')
        )
        downtime_layout.addWidget(duration_info, 5, 0, 1, 3)

        date_range_label = QLabel(_('Downtime date range'))
        date_range_label.setObjectName('actions')
        downtime_layout.addWidget(date_range_label, 6, 0, 1, 1)

        calendar_label = QLabel()
        calendar_label.setPixmap(QPixmap(get_image_path('calendar')))
        calendar_label.setFixedSize(16, 16)
        calendar_label.setScaledContents(True)
        downtime_layout.addWidget(calendar_label, 6, 1, 1, 1)

        start_time_label = QLabel(_('Start time:'))
        downtime_layout.addWidget(start_time_label, 7, 0, 1, 1)

        self.start_time.setCalendarPopup(True)
        self.start_time.setDateTime(datetime.datetime.now())
        self.start_time.setDisplayFormat("dd/MM/yyyy HH'h'mm")
        downtime_layout.addWidget(self.start_time, 7, 1, 1, 2)

        end_time_label = QLabel(_('End time:'))
        downtime_layout.addWidget(end_time_label, 8, 0, 1, 1)

        self.end_time.setCalendarPopup(True)
        self.end_time.setDateTime(datetime.datetime.now() + datetime.timedelta(hours=2))
        self.end_time.setDisplayFormat("dd/MM/yyyy HH'h'mm")
        downtime_layout.addWidget(self.end_time, 8, 1, 1, 2)

        self.comment_edit.setText(comment)
        self.comment_edit.setMaximumHeight(60)
        downtime_layout.addWidget(self.comment_edit, 9, 0, 1, 3)

        request_btn = QPushButton(_('REQUEST DOWNTIME'), self)
        request_btn.clicked.connect(self.handle_accept)
        request_btn.setObjectName('valid')
        request_btn.setMinimumHeight(30)
        request_btn.setDefault(True)
        downtime_layout.addWidget(request_btn, 10, 0, 1, 3)

        main_layout.addWidget(downtime_widget)

    def duration_to_seconds(self):
        """
        Return "duration" QTimeEdit value in seconds

        :return: "duration" in seconds
        :rtype: int
        """

        return QTime(0, 0).secsTo(self.duration.time())

    def handle_accept(self):
        """
        Check if end_time timestamp is not lower than start_time

        """

        if self.start_time.dateTime().toTime_t() > self.end_time.dateTime().toTime_t():
            logger.warning('Try to add Downtime with "End Time" lower than "Start Time"')
        else:
            self.accept()

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
