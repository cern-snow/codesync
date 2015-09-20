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
from snowTools.common.db import SnowFileDB, FileInfo
from snowTools.common.soapClient import SnowClient
from snowTools.common.tableInfo import TableInfo
from snowTools.common.tools.logger import SLogger
from snowTools.common.tools.string import normalizeNewlines
import codecs
import os
import sys
import urlparse

class DownloaderBase(object):
    
    @classmethod
    def _getTableInfo(cls, tableName):
        try:
            nameField = Config.getNameField()
            if not nameField:
                nameField = TableInfo.getNameField(tableName)

            contentField = Config.getContentField()
            if not contentField:
                contentField = TableInfo.getContentField(tableName)

        except KeyError:
            sys.stderr.write("No name_field or content_field parameter and no default information about table %s, aborting\n" % tableName)
            sys.exit(1)

        try:
            fileExtension = TableInfo.getFileExtension(tableName)
        except KeyError:
            fileExtension = ".txt"

        return (nameField, contentField, fileExtension)





class DownloaderOne(DownloaderBase):

    @classmethod
    def run(cls, targetURL, *extraArgs):
        instance, tableName, sysId = cls.__parseURL(targetURL)
        nameField, contentField, fileExtension = cls._getTableInfo(tableName)

        localDir = os.getcwd()
        db = SnowFileDB(localDir)
        client = SnowClient(tableName, instance)
        record = client.get(sysId)


        if len(extraArgs) > 0:
            fileName = extraArgs[0]
        else:
            fileName = "%s.%s" % (getattr(record, nameField).replace(" ", "-").replace("/", "-").replace("(", "[").replace(")", "]"), fileExtension)
        filePath = os.path.join(localDir, fileName)
        if os.path.exists(filePath):
            SLogger.warning("Local file %s already exists, will not overwrite" % filePath)
            return

#         if os.path.isfile(os.path.join(localDir, Config.getLockFilename())):
#             #swatch is watching, we do not want him to re-upload, we write a file for swatch.py to know
#             ignoreWatchFilePath = filePath + Config.getIgnoreWatchFilenameSuffix()
#             SLogger.debug("Creating file %s to avoid swatch to re-upload" % ignoreWatchFilePath)
#             ignoreWatchFile = open(ignoreWatchFilePath, "w")
#             ignoreWatchFile.close()

        f = codecs.open(filePath, "w", "utf-8")
        content = normalizeNewlines(getattr(record, contentField))
        f.write(content)
        f.close()
        db.addFileInfo(FileInfo(fileName, instance, tableName, record.sys_id, nameField, contentField, record.sys_updated_on))
        db.commitAndClose()
        SLogger.debug("Done. Written to %s" % fileName)

    @classmethod
    def __parseURL(cls, urlString):

        url = urlparse.urlparse(urlString)
        if (url[0] != 'https' and url[0] != 'https'):
            sys.stderr.write("URL must begin with http or https\n")
            sys.exit(1)
        if not url[1].endswith(".service-now.com"):
            sys.stderr.write("Please provide a service-now.com URL\n")
            sys.exit(1)
        queryParams = urlparse.parse_qs(url[4])


        sysId = None
        if url[2] == "/nav_to.do":
            if not 'uri' in queryParams:
                sys.stderr.write("nav_to.do URL without 'uri' parameter, aborting\n")
                sys.exit(1)
            uri = urlparse.urlparse(queryParams['uri'][0])
            tableName = uri[2][:-3]
            uriQueryParams = urlparse.parse_qs(uri[4])
            sysId = uriQueryParams.get('sys_id', None)[0]

        else:
            tableName = url[2][1:-3]
            sysId = queryParams.get('sys_id', None)[0]

        if not sysId:
            sys.stderr.write("Did not detect a sys_id URI parameter, aborting\n")
            sys.exit(1)

        instance = "%s://%s/" % (url[0], url[1])

        return (instance, tableName, sysId)




class DownloaderManySimple(DownloaderBase):

    @classmethod
    def run(cls, targetURL):
        instance, tableName, query = cls.__parseURL(targetURL)
        nameField, contentField, fileExtension = cls._getTableInfo(tableName)

        localDir = os.getcwd()
        db = SnowFileDB(localDir)
        client = SnowClient(tableName, instance)
        
        records = client.getRecords(query)

        for record in records:
            recordName = getattr(record, nameField)
            SLogger.debug("Downloading %s ... " % recordName)
            fileName = "%s.%s" % (getattr(record, nameField).replace(" ", "-").replace("/", "-").replace("(", "[").replace(")", "]"), fileExtension)
            filePath = os.path.abspath(os.path.join(localDir, fileName))
            if os.path.exists(filePath):
                good = False
                suffix = 2
                while not good:
                    filePathNew = filePath + "_" + str(suffix)
                    if not os.path.exists(filePathNew):
                        good = True
                        filePath = filePathNew
                    else:
                        suffix = suffix + 1
                        SLogger.warning("Local file %s already exists, will not overwrite" % filePath)
                        continue

            try:
                content = normalizeNewlines(getattr(record, contentField))
                f = codecs.open(filePath, "w", "utf-8")
                f.write(content)
                f.close()
                db.addFileInfo(FileInfo(fileName, instance, tableName, record.sys_id, nameField, contentField, record.sys_updated_on))
                SLogger.debug("Done. Written to %s" % fileName)
            except Exception:
                SLogger.debug("Problem with this record, will not write")


        db.commitAndClose()
    
    @classmethod
    def __parseURL(cls, urlString):

        url = urlparse.urlparse(urlString)
        if (url[0] != 'https' and url[0] != 'https'):
            sys.stderr.write("URL must begin with http or https\n")
            sys.exit(1)
        if not url[1].endswith(".service-now.com"):
            sys.stderr.write("Please provide a service-now.com URL\n")
            sys.exit(1)
        queryParams = urlparse.parse_qs(url[4])


        query = None
        if url[2] == "/nav_to.do":
            if not 'uri' in queryParams:
                sys.stderr.write("nav_to.do URL without 'uri' parameter, aborting\n")
                sys.exit(1)
            uri = urlparse.urlparse(queryParams['uri'][0])
            tableName = uri[2][:-8]
            uriQueryParams = urlparse.parse_qs(uri[4])
            query = uriQueryParams.get('sysparm_query', None)[0]

        else:
            tableName = url[2][1:-8]
            query = queryParams.get('sysparm_query', None)[0]

        if not query:
            sys.stderr.write("Did not detect a sysparm_query URI parameter, aborting\n")
            sys.exit(1)

        instance = "%s://%s/" % (url[0], url[1])

        return (instance, tableName, query)





class DownloaderManyComplex(object):

    @classmethod
    def run(cls, targetFiles):

        for targetFile in targetFiles:
            if not os.path.isfile(targetFile):
                SLogger.warning("File %s does not exist, ignoring" % os.path.abspath(targetFile))
                continue

            SLogger.debug("Reading target file %s" % os.path.abspath(targetFile))

            loadedParams = {}
            execfile(targetFile, globals(), loadedParams)


            instance = loadedParams.get('instance', None)
            if not instance:
                SLogger.warning("No instance declared in target file %s, aborting" % targetFile)
                sys.exit(1)

            if not instance.endswith("/"):
                instance = instance + "/"

            for i, target in enumerate(loadedParams['targets']):

                #we extract the table name
                table = target.get('table', None)
                if not table:
                    SLogger.warning("No table in target number %d of file %s, ignoring" % (i, targetFile))
                    continue

                #we extract the name field, content field, and how to rename files
                tableInfo = cls.__getTableInfo(table, target)
                if not tableInfo:
                    continue
                nameField, contentField, transformName = tableInfo

                #we extract the filtering functions
                query = target.get('query', '')
                recordFilter = target.get('recordFilter', lambda x: True)

                #we extract the local target directory
                localDir = target.get('localDir', None)
                if not localDir:
                    SLogger.debug("No localDir in target number %d of file %s, using current directory" % (i, targetFile))
                    localDir = os.getcwd()
                if not os.path.isdir(localDir):
                    SLogger.warning("Local directory %s does not exist, ignoring target %d" % (localDir, i))
                    continue

                #if everything is well, we start downloading and writing
                db = SnowFileDB(localDir)
                client = SnowClient(table, instance)

                records = client.getRecords(query)

                for record in records:
                    if recordFilter(record):
                        recordName = getattr(record, nameField)
                        SLogger.debug("Downloading %s ... " % recordName)
                        fileName = transformName(recordName)
                        filePath = os.path.abspath(os.path.join(localDir, fileName))
                        if os.path.exists(filePath):
                            good = False
                            suffix = 2
                            while not good:
                                filePathNew = filePath + "_" + str(suffix)
                                if not os.path.exists(filePathNew):
                                    good = True
                                    filePath = filePathNew
                                else:
                                    suffix = suffix + 1

                        try:
                            content = normalizeNewlines(getattr(record, contentField))
                            f = codecs.open(filePath, "w", "utf-8")
                            f.write(content)
                            f.close()
                            db.addFileInfo(FileInfo(fileName, instance, table, record.sys_id, nameField, contentField, record.sys_updated_on))
                            SLogger.debug("Done. Written to %s" % fileName)
                        except Exception:
                            SLogger.debug("Problem with this record, will not write")


                db.commitAndClose()

    @classmethod
    def __getTableInfo(cls, tableName, target):

        try:
            nameField = target.get('nameField', None)
            if not nameField:
                nameField = TableInfo.getNameField(tableName)
            contentField = target.get('contentField', None)
            if not contentField:
                contentField = TableInfo.getContentField(tableName)

        except KeyError:
            sys.stderr.write("No name_field or content_field parameter in target information, and no default information about table %s, ignoring\n" % tableName)
            return None

        transformName = target.get('transformName', None)
        if not transformName:
            try:
                fileExtension = TableInfo.getFileExtension(tableName)
            except KeyError:
                fileExtension = "txt"
            transformName = lambda name : "%s.%s" % (name.replace(" ", "-").replace("/", "-").replace("(", "[").replace(")", "]"), fileExtension)

        return (nameField, contentField, transformName)
