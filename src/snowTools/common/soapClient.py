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

from config import Config
from snowTools.common.tools.logger import SLogger
from snowTools.common.tools.string import prepareContentForUpload
from suds.client import Client
from urllib2 import URLError
import sys
from suds.transport import TransportError

class ClientPool(object):

    def __init__(self):
        self.__clients = {}

    def getClient(self, table, instance):
        if not (instance, table) in self.__clients:
            self.__clients[(instance, table)] = SnowClient(table, instance)
        return self.__clients[(instance, table)]
    
    def removeClient(self, table, instance):
        if (instance, table) in self.__clients:
            del self.__clients[(instance, table)]

clientPool = ClientPool()

class SnowClient(Client):

    __getRecordsMessage = \
"""<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:ns0="http://www.service-now.com/%s" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
   <SOAP-ENV:Header/>
   <ns1:Body>
      <ns0:getRecords>
         <ns0:__first_row>0</ns0:__first_row>
         <ns0:__last_row>10000</ns0:__last_row>
         <ns0:__encoded_query>%s</ns0:__encoded_query>
      </ns0:getRecords>
   </ns1:Body>
</SOAP-ENV:Envelope>"""

    def __init__(self, table, instance):
        self.__table = table
        self.__instance = instance
        username = Config.getUsername(instance)
        password = Config.getPassword(instance)
        SLogger.debug("Connecting to %s to download from table %s" % (instance, table))
        try:
            Client.__init__(self,
                            instance + table + "_list.do?WSDL",
                            username=username,
                            password=password,
                            timeout=Config.getTimeout())
        except URLError, e:
            SnowClient.__processURLError(e)
        except TransportError, e:
            SnowClient.__processTransportError(e)

    def getRecords(self, query):
        try:
            query = str(query)
            SLogger.debug("Using encoded query: %s" % (query))
            return self.service.getRecords(__inject={'msg': SnowClient.__getRecordsMessage % (self.__table, query)})
        except URLError, e:
            SnowClient.__processURLError(e)
        except TransportError, e:
            SnowClient.__processTransportError(e)

    def get(self, sysId):
        try:
            return self.service.get(sysId)
        except URLError, e:
            SnowClient.__processURLError(e)
        except TransportError, e:
            SnowClient.__processTransportError(e)
        except AttributeError, e:
            self.__processAttributeError(e)

    def insert(self, insertArgs):
        try:
            result = self.service.insert(**insertArgs)
            return result
        except URLError, e:
            SnowClient.__processURLError(e)
        except TransportError, e:
            SnowClient.__processTransportError(e)

    def update(self, updateArgs):
        if not 'sys_id' in updateArgs:
            raise KeyError('sys_id not present in updateArgs')
        try:
            result = self.service.update(**updateArgs)
            return result == updateArgs['sys_id']
        except URLError, e:
            SnowClient.__processURLError(e)
        except TransportError, e:
            SnowClient.__processTransportError(e)

    def updateContent(self, sysId, contentFieldName, content):
        updateArgs = {"sys_id" : sysId}
        updateArgs[contentFieldName] = prepareContentForUpload(content)
        return self.update(updateArgs)

    @classmethod
    def __processURLError(cls, e):
        if hasattr(e, "reason") and hasattr(e.reason, "args") and e.reason.args[0] == "The read operation timed out":
            SLogger.warning("Connection timed out. Verify your username.")
            sys.exit(1)
        else:
            raise e

    @classmethod
    def __processTransportError(cls, e):
        if hasattr(e, "httpcode") and e.httpcode == 401:
            SLogger.warning("Authentication error 401. Verify your password")
            sys.exit(1)
        else:
            raise e
        
    def __processAttributeError(self, e):
        SLogger.warning("Could not retrieve information from ServiceNow. Possibly your password is wrong.")
        Config.clearPassword(self.__instance)
        clientPool.removeClient(self.__table, self.__instance)
        sys.exit(1)
