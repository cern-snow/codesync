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

class TableInfo(object):

    __tableInfo = {
        "content_block_programmatic" : ("name", "programmatic_content", "xml"), #dynamic blocks
        "sys_ui_macro" : ("name", "xml", "xml"), #ui macros
        "sys_script_include" : ("name", "script", "js"), #script includes
        "sys_ui_page" : ("name", "html", "xml"), #UI Pages (html field)
        "sys_ui_script" : ("name", "script", "js"), #UI scripts
        "content_css" : ("name", "style", "css"), #CSS stylesheets
        "sys_script" : ("name", "script", "js"), #business rules
        "sys_script_client" : ("name", "script", "js"), #client scripts
        "sys_ui_policy" : ("short_description", "script_true", "js"), #UI Policies (script_true field)
        "sys_ui_action" : ("name", "script", "js"), #UI Actions
        "sys_security_acl" : ("name", "script", "js"), #Access Control
        "catalog_script_client" : ("name", "script", "js"), #Catalog client scripts
        "catalog_ui_policy" : ("short_description", "script_true", "js"), #Catalog UI Policies (script_true field)
        "wf_activity" : ("name", "script", "js"), #Workflow activity
        "cmn_schedule_page" :("name", "client_script", "js"), #schedule pages,
        "kb_submission" : ("number", "text", "html"), #KB Submissions
        "content_block_static" : ("name", "static_content", "html"), #static content
        "sysevent_in_email_action" : ("name", "script", "js"), #inbound email actions
        "sys_installation_exit" : ("name", "script", "js"), #Installation exits
        "sysauto_script" : ("name", "script", "js"), #scheduled jobs
        "sys_processor" : ("name", "script", "js"), #processors
        "content_type" : ("type", "summary", "xml"), #CMS content types
        "sysevent_email_action" : ("name", "message", "txt"), #Email notifications
        "sysevent_email_template" : ("name", "message", "txt"), #Email templates
        "sys_impex_map" : ("name", "script", "js"), #Import export maps
        "content_block_lists" : ("name", "script", "js"), #CMS List of content (advanced query)
        "content_page_rule" : ("name", "advanced_condition", "js"), #Login Rules
        "sys_ui_message" : ("key", "message", "txt"), #Messages
        "sc_cat_item_producer" : ("name", "script", "js"), #Record Producers
        "sys_relationship" : ("name", "query_with", "js"), #Relationships
        "sysevent_script_action" : ("name", "script", "js"), #Script Actions
        "sys_transform_map" :  ("name", "script", "js"), #Transform Maps
        "sys_transform_script" :  ("sys_id", "script", "js"), #Transform Scripts
        "sys_web_service" :  ("name", "script", "js"), #Scripted Web Service
        "sys_script_ajax" : ("name", "script", "js"), #AJAX Script
        "sys_script_fix" : ("name", "script", "js"), #Fix Script
    }

    @classmethod
    def hasTableInfo(cls, tableName):
        return tableName in cls.__tableInfo

    @classmethod
    def getNameField(cls, tableName):
        if cls.hasTableInfo(tableName):
            return cls.__tableInfo[tableName][0]
        else:
            raise KeyError(tableName)

    @classmethod
    def getContentField(cls, tableName):
        if cls.hasTableInfo(tableName):
            return cls.__tableInfo[tableName][1]
        else:
            raise KeyError(tableName)

    @classmethod
    def getFileExtension(cls, tableName):
        if cls.hasTableInfo(tableName):
            return cls.__tableInfo[tableName][2]
        else:
            raise KeyError(tableName)
