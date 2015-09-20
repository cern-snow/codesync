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

from Queue import Queue
import codecs
import os
from threading import Thread, Lock
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from snowTools.common.commands import Commands
from snowTools.common.config import Config
from snowTools.common.db import DBWorker
from snowTools.common.soapClient import clientPool
from snowTools.common.tools.dt import checkCanUpdate, snowServerToLocalDate
from snowTools.common.tools.filesystem import fileShouldBeIgnored, \
    directoryShouldBeIgnored
from snowTools.common.tools.logger import SLogger


class Daemon(object):

    @classmethod
    def run(cls, targetDir):
        cls.__dbWorker = DBWorker()
        cls.__dbWorker.start()

        cls.__handler = EventHandler(cls.__dbWorker)

        cls.__lockFiles = []
        cls.__observer = Observer()

        if Config.isRecursive():
            for root, _, _ in os.walk(targetDir):
                cls.__scheduleDir(root, targetDir)
        else:
            cls.__scheduleDir(targetDir, targetDir)

        cls.__observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            SLogger.debug("Stopping...")
        finally:
            cls.__shutdown()


    @classmethod
    def __scheduleDir(cls, dirPath, rootDirPath):
        if not directoryShouldBeIgnored(dirPath):
            SLogger.debug("Watching dir %s" % os.path.abspath(dirPath))
            lockFilePath = os.path.abspath(os.path.join(dirPath, Config.getLockFilename()))
            if os.path.exists(lockFilePath):
                SLogger.warning("%s already exists. Another swatch might be watching this directory or might not have shut down correctly. Consider using the scleanlockfiles command." % (lockFilePath))
                if dirPath == rootDirPath:
                    Commands.warning("Directory already watched", "Another swatch might be watching or might not have shut down correctly.")
            else:
                lockFile = open(lockFilePath, "w")
                lockFile.close()
                cls.__lockFiles.append(lockFilePath)
            
            cls.__observer.schedule(cls.__handler, path=dirPath)

    @classmethod
    def __shutdown(cls):
        cls.__observer.stop()
        cls.__dbWorker.stop()

        SLogger.debug("Deleting lock files...")
        for lockFilePath in cls.__lockFiles:
            try:
                os.remove(lockFilePath)
            except OSError:
                SLogger.warning("Lock file %s could not be deleted" % lockFilePath)

        cls.__observer.join()
        cls.__dbWorker.join()

        SLogger.debug("Stopped")


class EventHandler(FileSystemEventHandler):
    """Handles all the events captured."""

    def __init__(self, dbWorker):
        FileSystemEventHandler.__init__(self)
        self.__changedFiles = set()
        self.__dbWorker = dbWorker

    def addChangedFile(self, filePath):
        self.__changedFiles.add(filePath)

    def getChangedFiles(self):
        return self.__changedFiles

    def clearChangedFiles(self, changedFiles):
        self.__changedFiles = self.__changedFiles.difference(changedFiles)

    def on_modified(self, event):
        path = event.src_path
        if not event.is_directory and not fileShouldBeIgnored(path):
            self.addChangedFile(path)
            eventProcessor = EventProcessor(self, self.__dbWorker)
            eventProcessor.start()


class EventProcessor(Thread):

    lock = Lock()

    def __init__(self, eventHandler, dbWorker):
        Thread.__init__(self)
        self.__eventHandler = eventHandler
        self.__dbWorker = dbWorker
        self.__inputQueue = Queue()

    def run(self):
        time.sleep(0.2)
        with EventProcessor.lock:
            changedFiles = list(self.__eventHandler.getChangedFiles())
            self.__eventHandler.clearChangedFiles(changedFiles)
            for filePath in changedFiles:
                self.processFile(filePath)


    def sendFileInfo(self, fileInfo):
        self.__inputQueue.put(fileInfo)

    def sendConfirmation(self, confirmation):
        self.__inputQueue.put(confirmation)

    def processFile(self, filePath):
        ignoreWatchFilePath = filePath + Config.getIgnoreWatchFilenameSuffix()
        if os.path.isfile(ignoreWatchFilePath):
            #this file was updated by supdate.py, do not process
            os.remove(ignoreWatchFilePath)
            return

        #Loic Horisberger - 17.10.2014:
        #This is a fix for MacVIM where current files are swap files.        
        #If the file ends with ".swp", remove the extention to get the
        #original filename. Remove the "." at the beginning that makes
        #the file hidden as well.
        if filePath.endswith(".swp"):
            filePath = filePath.replace(".swp","")
            filePath = filePath[::-1].replace("/."[::-1],"/"[::-1],1)[::-1]

        self.__dbWorker.getFileInfo(self, filePath)
        fileInfo = self.__inputQueue.get()

        if fileInfo:
            SLogger.debug("Local modification detected for: %s" % filePath)

            client = clientPool.getClient(fileInfo.getTableName(), fileInfo.getInstance())
            localUpdateDateString = fileInfo.getUpdatedOn()

            canUpdate = True
            if localUpdateDateString:
                SLogger.debug("Checking remote version...")
                remoteRecord = client.get(fileInfo.getSysId())
                remoteUpdatedOnString = remoteRecord.sys_updated_on
                canUpdate = checkCanUpdate(localUpdateDateString, remoteUpdatedOnString)
                if canUpdate:
                    SLogger.debug("Done")
                else:
                    SLogger.warning("Remote file changed by %s on %s. Previous local version is %s. Cannot update" %
                        (remoteRecord.sys_updated_by, snowServerToLocalDate(remoteUpdatedOnString), localUpdateDateString))
                    Commands.cannotUpload(remoteRecord.sys_updated_by, remoteUpdatedOnString, localUpdateDateString)


            if canUpdate:
                SLogger.debug("Updating in SNOW...")
                content = codecs.open(filePath, "r", "utf-8").read()

                success = client.updateContent(fileInfo.getSysId(), fileInfo.getContentFieldName(), content)
                if success:
                    SLogger.debug("Updating local update date...")
                    newRemoteRecord = client.get(fileInfo.getSysId())
                    newRemoteUpdatedOnString = newRemoteRecord.sys_updated_on
                    self.__dbWorker.setUpdatedOn(self, filePath, newRemoteUpdatedOnString)
                    confirmation = self.__inputQueue.get()
                    if confirmation:
                        SLogger.debug("Success updating %s" % fileInfo.getFileName())
                        Commands.success(fileInfo)
                    else:
                        SLogger.warning("Update of local date failed for file %s" % fileInfo)
                        Commands.warning("Upload failed", "Update of local date failed for file %s" % fileInfo)

                else:
                    SLogger.warning("Update of local date failed for file %s" % fileInfo)
                    Commands.warning("Upload failed", "Update of local date failed for file %s" % fileInfo)
