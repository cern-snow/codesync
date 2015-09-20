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

import shlex
import subprocess

from snowTools.common.config import Config
from snowTools.common.tools.dt import snowServerToLocalDate


class Commands(object):

    @classmethod
    def success(cls, fileInfo):
        successCommandTemplate = Config.getSuccessCommand()
        if successCommandTemplate:
            command = successCommandTemplate % {"filename": fileInfo.getFileName().replace("[", "\[")}
            subprocess.call(shlex.split(str(command)))

    @classmethod
    def warning(cls, title, msg):
        warningCommandTemplate = Config.getWarningCommand()
        if warningCommandTemplate:
            command = warningCommandTemplate % {"msg": msg, "title": title}
            subprocess.call(shlex.split(str(command)))

    @classmethod
    def cannotUpload(cls, updatedBy, remoteUpdatedOnString, localUpdateDateString):
        cannotUploadCommandTemplate = Config.getCannotUploadCommand()
        if cannotUploadCommandTemplate:
            command = cannotUploadCommandTemplate % {"person": updatedBy,
                                                     "remoteDate" : snowServerToLocalDate(remoteUpdatedOnString),
                                                     "localDate": localUpdateDateString}
            subprocess.call(shlex.split(str(command)))
