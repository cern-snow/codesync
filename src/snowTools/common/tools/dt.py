# -*- coding: utf-8 -*-
#
# This file is part of CERN CodeSync for ServiceNow.
# Copyright (C) 2010 - 2015 European Organization for Nuclear Research (CERN).
#
# CERN CodeSync for ServiceNow is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# CERN CodeSync for ServiceNow is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CERN CodeSync for ServiceNow; if not, see <http://www.gnu.org/licenses/>.
#
# Author: David Martin Clavo

from snowTools.common.config import Config
import datetime

def checkCanUpdate(localDateString, remoteDateString):
    localDate = datetime.datetime.strptime(localDateString, Config.getLocalDateFormat())
    remoteDate = datetime.datetime.strptime(remoteDateString, Config.getServerDateFormat())
    return remoteDate <= localDate

def snowServerToLocalDate(dateString):
    if dateString:
        dt = datetime.datetime.strptime(dateString, Config.getServerDateFormat())
        return dt.strftime(Config.getLocalDateFormat())
    else:
        return dateString
