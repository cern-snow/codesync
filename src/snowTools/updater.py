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
from snowTools.common.db import SnowFileDB
from snowTools.common.soapClient import SnowClient
from snowTools.common.tools.logger import SLogger
from snowTools.common.tools.string import normalizeNewlines
import codecs
import os
import sys

class Updater(object):

    @classmethod
    def run(cls, target):
        if not os.path.exists(target):
            sys.stderr.write("Unable to find file %s" % target)
            sys.exit(1)

        dirName, fileName = os.path.split(target)
        dirName = os.path.abspath(os.path.normpath(dirName))

        db = SnowFileDB(dirName)
        fileInfo = db.getFileInfo(fileName)

        if not fileInfo:
            sys.stderr.write("File %s not found in %s" % (target, os.path.join(dirName, Config.getDBFilename())))
            sys.exit(1)

        client = SnowClient(fileInfo.getTableName(), fileInfo.getInstance())
        record = client.get(fileInfo.getSysId())
        recordName = record.sys_id
        content = normalizeNewlines(getattr(record, fileInfo.getContentFieldName()))

        if os.path.isfile(os.path.join(dirName, Config.getLockFilename())):
            #swatch is watching, we do not want him to re-upload, we write a file for swatch.py to know
            ignoreWatchFilePath = target + Config.getIgnoreWatchFilenameSuffix()
            SLogger.debug("Creating file %s to avoid swatch to re-upload" % ignoreWatchFilePath)
            ignoreWatchFile = open(ignoreWatchFilePath, "w")
            ignoreWatchFile.close()

        f = codecs.open(target, "w", "utf-8")
        f.write(content)

        db.setUpdatedOn(fileName, record.sys_updated_on)
        db.commitAndClose()
        SLogger.debug("Updated record %s to file %s. set updated_on to %s" % (recordName, fileName, record.sys_updated_on))
