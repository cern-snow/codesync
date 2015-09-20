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

import logging
from optparse import OptionParser
import sys

import snowTools
from snowTools.cleaner import Cleaner
from snowTools.common.config import Config
from snowTools.common.tools.logger import SLogger
from snowTools.daemon import Daemon
from snowTools.downloader import DownloaderOne, DownloaderManySimple, \
    DownloaderManyComplex
from snowTools.mover import Mover
from snowTools.updater import Updater


class CommonParser(OptionParser):

    def __init__(self, commandName):
        self.__commandName = commandName

        self.__nArgs = 1
        usage = ""
        if commandName == "get":
            usage = "Usage: %prog [options] target [path]\n\ntarget: url of a ServiceNow record\npath (optional) where to write the file"
        elif commandName == "getmany":
            usage = "Usage: %prog [options] target \n\ntarget: url of a ServiceNow filter (obtained via right-click on a filter)."
        elif commandName == "getmany2":
            usage = "Usage: %prog [options] target1 target2 ...\n\ntargets: files that specify which records to download and how."
        elif commandName == "update":
            usage = "Usage: %prog [options] file\n\nfile: file to update from ServiceNow"
        elif commandName == "watch":
            usage = "Usage: %prog [options] target_dir\n\ntarget_dir: the directory to watch"
        elif commandName == "clean":
            usage = "Usage: %prog [options] target_dir\n\ntarget_dir: the directory to where to clean the lock files"
        elif commandName == "move":
            self.__nArgs = 2
            usage = "Usage: %prog [options] source destination\n\nsource: initial location of the file\ndestination: final location of the file"
        


        OptionParser.__init__(self, usage, version="%prog " + snowTools.version)

        if commandName == "watch" or commandName == "clean":
            if commandName == 'watch':
                helpText = "Recursive: watch directories recursively."
            else:
                helpText = "Recursive: clean directories recursively."
            self.add_option("-r", "--recursive", action="store_true", dest="recursive",
                        help=helpText)
        self.add_option("-v", action="store_true", dest="verbose",
                        help="Verbose: print all log statements.")
        self.add_option("-c", "--config-file", dest="configFilePath", metavar="FILE",
                        default=None,
                        help="Location of a config file. If omitted, it will look for snowcong.py in the current directory or parent directories")
        if commandName == "get" or commandName == "getmany":
            self.add_option("-n", "--name-field", dest="nameField", metavar="string",
                            default=None,
                            help="Name of the field that hold what will be used as file name. Only use if you get an error because the name of the field is not known by the program.")
            self.add_option("-t", "--content-field", dest="contentField", metavar="string",
                            default=None,
                            help="Name of the field that holds the code. Only use if you get an error because the name of the field is not known by the program.")
        self.add_option("-u", "--username", dest="username", metavar="string",
                        default=None,
                        help="Your ServiceNow username, e.g. david.martin. You can also write this in the config file.")
        self.add_option("-p", "--password", dest="password", metavar="string",
                        default=None,
                        help="Your ServiceNow password. You can also write this in the config file.")
        if commandName == "watch":
            self.add_option("--ignore-lock-files", action="store_true", dest="deleteLockFiles",
                        help="Ignore lock files and watch anyway.")

        self.__options = None
        self.__args = None


    def process(self):
        self.__options, self.__args = self.parse_args()

        self.__verifyNArgs()
        Config.loadOptionsFromFile(self.__options.configFilePath)
        self.__setCommandLineOptions()
        Config.setDefaultsIfOptionNotPresent()
        self.__setLoggerLevel()
        if Config.getConfigFilePath():
            SLogger.debug("Loaded config file from %s" % Config.getConfigFilePath())
        self.__launchCommand()

    def __verifyNArgs(self):
        if len(self.__args) < self.__nArgs:
            self.print_help()
            sys.exit(1)

    def __setCommandLineOptions(self):
        commandLineOptions = ['instance', 'username', 'password', 'nameField', 'contentField', 'deleteLockFiles', 'recursive']
        commandLineOptionValues = {}
        for commandLineOptionName in commandLineOptions:
            if hasattr(self.__options, commandLineOptionName):
                optionValue = getattr(self.__options, commandLineOptionName)
                if optionValue:
                    commandLineOptionValues[commandLineOptionName] = optionValue
        Config.setOptions(commandLineOptionValues)

    def __setLoggerLevel(self):
        if self.__options.verbose:
            SLogger.setLevel(logging.DEBUG)
        else:
            level = Config.getLoggerLevel()
            if level == "warning":
                SLogger.setLevel(logging.WARNING)
            elif level == "debug":
                SLogger.setLevel(logging.DEBUG)

    def __launchCommand(self):
        if self.__commandName == "get":
            DownloaderOne.run(self.__args[0], *self.__args[1:])
        elif self.__commandName == "getmany":
            DownloaderManySimple.run(self.__args[0]) 
        elif self.__commandName == "getmany2":
            DownloaderManyComplex.run(self.__args)
        elif self.__commandName == "update":
            Updater.run(self.__args[0])
        elif self.__commandName == "watch":
            Daemon.run(self.__args[0])
        elif self.__commandName == "clean":
            Cleaner.run(self.__args[0])
        elif self.__commandName == "move":
            Mover.run(self.__args[0], self.__args[1])
