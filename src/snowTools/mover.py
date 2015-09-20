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
import os
import shutil
import sys
from snowTools.common.tools.logger import SLogger

class Mover(object):

    @classmethod
    def run(cls, src, dst):

        src = os.path.abspath(os.path.normpath(src))
        dst = os.path.abspath(os.path.normcase(dst))
        if src == dst:
            return

        if not os.path.exists(src):
            sys.stderr.write("File %s does not exist\n" % src)
            sys.exit(1)

        if os.path.exists(dst):
            sys.stderr.write("File %s already exists\n" % dst)
            sys.exit(1)

        sourceDir, sourceFilename = os.path.split(src)
        if not SnowFileDB.existsAtDir(sourceDir):
            sys.stderr.write("DB file not found at %s, aborting\n" % os.path.join(sourceDir, Config.getDBFilename()))
            sys.exit(1)

        destDir, destFilename = os.path.split(dst)

        if sourceDir != destDir:
            sourceDB = SnowFileDB(sourceDir)
            destDB = SnowFileDB(destDir)

            fileInfo = sourceDB.getFileInfo(sourceFilename)
            if not fileInfo:
                sys.stderr.write("File %s not present at DB file %s\n" % (sourceFilename, sourceDB.getDBFilePath()))
                sys.exit(1)
            sourceDB.deleteFile(sourceFilename)
            fileInfo.setFileName(destFilename)
            destDB.addFileInfo(fileInfo)
            shutil.move(src, dst)
            sourceDB.commitAndClose()
            destDB.commitAndClose()

        else:
            db = SnowFileDB(sourceDir)
            sucesss = db.renameFile(sourceFilename, destFilename)
            if not sucesss:
                sys.stderr.write("File %s not present at DB file %s\n" % (sourceFilename, db.getDBFilePath()))
                sys.exit(1)

            shutil.move(src, dst)
            db.commitAndClose()

        SLogger.debug("File successfully moved from %s to %s\n" % (src, dst))
