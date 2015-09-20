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

from snowTools.common.tools.logger import SLogger
import os
import sys
from getpass import getpass

class Config(object):

    __userInfo = {}

    __optionValues = {}
    __defaults = {'dbFilename' : '.snow',
                  'lockFilename': '.snow.lock',
                  'ignoreWatchFilenameSuffix' : '.snow.ignore',
                  'snowServerTz' : 'Europe/Zurich',
                  'serverDateFormat' : "%Y-%m-%d %H:%M:%S",
                  'localDateFormat' : "%Y-%m-%d %H:%M:%S",
                  'loggerLevel' : 'warning',
                  'ignoreFiles': '',
                  'ignoreDirs': '',
                  'deleteLockFiles' : False,
                  'recursive' : False,
                  'nameField' : None,
                  'contentField' : None,
                  'timeout': 20
                  }

    @classmethod
    def setOptions(cls, options):
        for key, value in options.iteritems():
            cls.__optionValues[key] = value

    @classmethod
    def loadOptionsFromFile(cls, configFilePath):
        found = True
        if not configFilePath:
            currentDir = os.getcwd()
            found = False
            while not found:
                configFilePath = os.path.join(currentDir, "snowconf.py")
                if os.path.isfile(configFilePath):
                    found = True
                else:
                    if cls.__isRootDir(currentDir):
                        break
                    currentDir = os.path.dirname(currentDir)

        elif not os.path.isfile(configFilePath):
            SLogger.warning("Config file not found at %s" % configFilePath)
            sys.exit(1)

        if found:
            cls.__configFilePath = os.path.normpath(os.path.abspath(configFilePath))
            loadedOptions = {}
            execfile(cls.__configFilePath, globals(), loadedOptions)
            cls.__setLoadedOptions(loadedOptions)
        else:
            cls.__configFilePath = None

    @classmethod
    def __isRootDir(cls, dirname):
        dirname = os.path.abspath(os.path.normpath(dirname))
        return dirname == os.path.dirname(dirname)

    @classmethod
    def __setLoadedOptions(cls, loadedOptions):
        for key, value in loadedOptions.iteritems():
            if key == "userInfo":
                for instance, username, password in value:
                    cls.__userInfo[instance] = [username, password]
            else:
                cls.__optionValues[key] = value

    @classmethod
    def setDefaultsIfOptionNotPresent(cls):
        for key, value in cls.__defaults.iteritems():
            if not key in cls.__optionValues:
                cls.__optionValues[key] = value

    @classmethod
    def getMissingOptions(cls, compulsoryOptions):
        missingOptions = []
        for optionName in compulsoryOptions:
            if not optionName in cls.__optionValues:
                missingOptions.append(optionName)
        return missingOptions

    @classmethod
    def getConfigFilePath(cls):
        return cls.__configFilePath

    @classmethod
    def getDBFilename(cls):
        return cls.__optionValues["dbFilename"]

    @classmethod
    def getUsername(cls, instance):
        if not instance in cls.__userInfo:
            cls.__userInfo[instance] = ["", ""]
        if cls.__userInfo[instance][0] == "":
            cls.__userInfo[instance][0] = raw_input("Username for %s : " % instance)
        return cls.__userInfo[instance][0]

    @classmethod
    def getPassword(cls, instance):
        if not instance in cls.__userInfo:
            cls.__userInfo[instance] = ["", ""]
        if cls.__userInfo[instance][1] == "":
            cls.__userInfo[instance][1] = getpass("Password for %s (will not be displayed): " % instance)
        return cls.__userInfo[instance][1]
    
    @classmethod
    def clearPassword(cls, instance):
        if instance in cls.__userInfo:
            cls.__userInfo[instance][1] = ""

    @classmethod
    def getServerDateFormat(cls):
        return cls.__optionValues["serverDateFormat"]

    @classmethod
    def getLocalDateFormat(cls):
        return cls.__optionValues["localDateFormat"]

    @classmethod
    def getLoggerLevel(cls):
        return cls.__optionValues["loggerLevel"]

    @classmethod
    def getNameField(cls):
        return cls.__optionValues["nameField"]

    @classmethod
    def getContentField(cls):
        return cls.__optionValues["contentField"]

    @classmethod
    def getIgnoreFiles(cls):
        cls.__stringToSet("ignoreFiles", [cls.getDBFilename(), cls.getLockFilename()])
        return cls.__optionValues["ignoreFiles"]

    @classmethod
    def getIgnoreDirs(cls):
        cls.__stringToSet("ignoreDirs")
        return cls.__optionValues["ignoreDirs"]
    
    @classmethod
    def isDeleteLockFiles(cls):
        return cls.__optionValues['deleteLockFiles']

    @classmethod
    def __stringToSet(cls, optionName, extraItems=None):
        if not extraItems:
            extraItems = []
        if not type(cls.__optionValues[optionName]) == set:
            if cls.__optionValues[optionName] == "":
                cls.__optionValues[optionName] = set()
            else:
                cls.__optionValues[optionName] = set([s.strip() for s in cls.__optionValues[optionName].split(",")]).union(set(extraItems))


    @classmethod
    def getLockFilename(cls):
        return cls.__optionValues["lockFilename"]

    @classmethod
    def getIgnoreWatchFilenameSuffix(cls):
        return cls.__optionValues["ignoreWatchFilenameSuffix"]

    @classmethod
    def isRecursive(cls):
        return cls.__optionValues["recursive"]

    @classmethod
    def getCannotUploadCommand(cls):
        if not "cannotUploadCommand" in cls.__optionValues:
            return None
        return cls.__optionValues["cannotUploadCommand"]

    @classmethod
    def getSuccessCommand(cls):
        if not "successCommand" in cls.__optionValues:
            return None
        return cls.__optionValues["successCommand"]

    @classmethod
    def getWarningCommand(cls):
        if not "warningCommand" in cls.__optionValues:
            return None
        return cls.__optionValues["warningCommand"]

    @classmethod
    def getTimeout(cls):
        return cls.__optionValues["timeout"]
