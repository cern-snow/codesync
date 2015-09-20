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
import sys

class SLogger():

    __logger = None

    @classmethod
    def __initLogger(cls):
        if not cls.__logger:
            logger = logging.getLogger("codesync")
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.WARNING)
            cls.__logger = logger

    @classmethod
    def setLevel(cls, level):
        cls.__initLogger()
        cls.__logger.setLevel(level)

    @classmethod
    def debug(cls, msg):
        cls.__initLogger()
        cls.__logger.debug(msg)

    @classmethod
    def warning(cls, msg):
        cls.__initLogger()
        cls.__logger.warning(msg)
