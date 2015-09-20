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

import os
from snowTools.common.config import Config

def fileShouldBeIgnored(filePath):
    fileDir, fileName = os.path.split(os.path.normpath(os.path.abspath(filePath)))
    if fileName in Config.getIgnoreFiles().union(set([Config.getDBFilename(), Config.getLockFilename()])):
        return True
    else:
        return directoryShouldBeIgnored(fileDir)

def directoryShouldBeIgnored(dirPath):
    dirPath = os.path.normpath(os.path.abspath(dirPath))
    if dirPath in Config.getIgnoreDirs():
        return True
    else:
        for dirName in Config.getIgnoreDirs():
            if dirPath.find(dirName) != -1:
                return True
    return False
