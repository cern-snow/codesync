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
from snowTools.common.config import Config
from snowTools.common.tools.dt import snowServerToLocalDate
from threading import Thread
import os
import snowTools
import sqlite3
from snowTools.common.tools.logger import SLogger

class DBWorker(Thread):

    OP_GET_FILE_INFO = 0
    OP_SET_UPDATE_DATE = 1

    def __init__(self):
        Thread.__init__(self)
        self.__dbPool = DBPool()
        self.__inputQueue = Queue()

    def getFileInfo(self, eventProcessor, filePath):
        self.__inputQueue.put((eventProcessor, filePath, DBWorker.OP_GET_FILE_INFO, None))

    def setUpdatedOn(self, eventProcessor, filePath, newUpdateDate):
        self.__inputQueue.put((eventProcessor, filePath, DBWorker.OP_SET_UPDATE_DATE, newUpdateDate))

    def run(self):
        try:
            while True:
                inputItem = self.__inputQueue.get()
                if not inputItem:
                    break

                eventProcessor, filePath, operation, argument = inputItem
                dirName, fileName = os.path.split(filePath)
                db = self.__dbPool.getDB(dirName)

                if operation == DBWorker.OP_GET_FILE_INFO:
                    #we return the file info
                    fileInfo = db.getFileInfo(fileName)
                    eventProcessor.sendFileInfo(fileInfo)
                elif operation == DBWorker.OP_SET_UPDATE_DATE:
                    #we update the file info
                    success = db.setUpdatedOn(fileName, argument)
                    db.commit()
                    eventProcessor.sendConfirmation(success)

        except KeyboardInterrupt:
            pass

        finally:
            pass

    def stop(self):
        self.__inputQueue.put(None)


class DBPool(object):

    def __init__(self):
        self.__dbs = {}

    def getDB(self, dirName):
        if not dirName in self.__dbs:
            self.__dbs[dirName] = SnowFileDB(dirName)
        return self.__dbs[dirName]

class SnowFileDB(object):

    def __init__(self, path):
        self.__dbFilePath = os.path.join(path, Config.getDBFilename())
        SLogger.debug("Opening DB File: %s" % self.__dbFilePath)
        self.__conn = sqlite3.connect(self.__dbFilePath)
        self.__cursor = self.__conn.cursor()

    @classmethod
    def existsAtDir(cls, path):
        return os.path.exists(os.path.join(path, Config.getDBFilename()))

    def getDBFilePath(self):
        return self.__dbFilePath

    def getFileInfo(self, fileName):
        if not self.__isTableCreated():
            self.__createTable()
        rows = self.__cursor.execute('SELECT * FROM files WHERE file_name=?', [fileName])
        row = rows.fetchone()
        if row:
            return FileInfo(*row)
        return None

    def addFileInfo(self, fileInfo):
        if not self.__isTableCreated():
            self.__createTable()
        self.__cursor.execute("INSERT OR REPLACE INTO files VALUES(?,?,?,?,?,?,?)", (fileInfo.getFileName(), fileInfo.getInstance(), fileInfo.getTableName(), fileInfo.getSysId(), fileInfo.getNameFieldName(), fileInfo.getContentFieldName(), fileInfo.getUpdatedOn()))

    def deleteFile(self, fileName):
        if not self.__isTableCreated():
            self.__createTable()
        self.__cursor.execute("DELETE FROM files WHERE file_name = ?", [fileName])
        return self.__cursor.rowcount > 0

    def renameFile(self, oldName, newName):
        if not self.__isTableCreated():
            self.__createTable()
        self.__cursor.execute("DELETE FROM files WHERE file_name = ?", [newName])
        self.__cursor.execute("UPDATE files SET file_name = ? WHERE file_name = ?", (newName, oldName))
        return self.__cursor.rowcount > 0

    def setUpdatedOn(self, fileName, newUpdateDateString):
        if not self.__isTableCreated():
            self.__createTable()
        stringToWrite = snowServerToLocalDate(newUpdateDateString)
        self.__cursor.execute("UPDATE files SET updated_on = ? WHERE file_name = ?", (stringToWrite, fileName))
        return self.__cursor.rowcount > 0

    def commit(self):
        self.__conn.commit()

    def close(self):
        self.__cursor.close()

    def commitAndClose(self):
        self.commit()
        self.close()

    def __isTableCreated(self):
        rows = self.__cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
        return bool(rows.fetchone())

    def __createTable(self):
        self.__cursor.execute('CREATE TABLE files (file_name TEXT PRIMARY KEY, instance TEXT, table_name TEXT, sys_id TEXT, name_field TEXT, content_field TEXT, updated_on TEXT)')
        self.__cursor.execute('CREATE TABLE version (version TEXT)')
        self.__cursor.execute('INSERT INTO version VALUES(?)', [snowTools.version])
        self.commit()


class FileInfo(object):

    def __init__(self, fileName, instance, tableName, sysId, nameFieldName, contentFieldName, updated_on):
        self.__fileName = fileName
        self.__instance = instance
        self.__tableName = tableName
        self.__sysId = sysId
        self.__nameFieldName = nameFieldName
        self.__contentFieldName = contentFieldName
        self.__updatedOn = snowServerToLocalDate(updated_on)

    def getFileName(self):
        return self.__fileName

    def setFileName(self, fileName):
        self.__fileName = fileName

    def getInstance(self):
        return self.__instance

    def getTableName(self):
        return self.__tableName

    def getSysId(self):
        return self.__sysId

    def getNameFieldName(self):
        return self.__nameFieldName

    def getContentFieldName(self):
        return self.__contentFieldName

    def getUpdatedOn(self):
        return self.__updatedOn

    def setUpdatedOn(self, updateDate):
        self.__updatedOn = updateDate
