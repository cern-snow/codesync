# CodeSync for ServiceNow

CodeSync is a tool to synchronize local code files with ServiceNow configuration elements.

##Features

It is able to quickly download one or more ServiceNow "code elements" as files in your local file system so that you can edit them with your favorite IDE / text editor. After that, it detects local changes to those files and uploads them back automatically into ServiceNow. Conflicts are avoided; when a conflict happens, a warning is shown and you can re-download the latest online version.

More than 30 types of "code elements" such as Business Rules, Script Includes, Client Scripts and UI Macros are currently supported and it is easy to define new ones.

##Documentation

Documentation on how to install and use will be soon added to the [Wiki](https://github.com/cern-snow/codesync/wiki).

##License

CodeSync is free software, licensed under terms of the GNU General Public License (GPL) v3. It is currently used by members of the ServiceNow dev/admin team at CERN as well as other ServiceNow professionals in the world.


##History

CodeSync is written in Python. Interaction with ServiceNow is done via the SOAP interface, thanks to the suds library. The filesystem is watched thanks to the lightweight watchdog library. A mapping between ServiceNow "code elements" and local files is kept in each folder thanks to a small sqlite database.


It was initially developed in 2010 by David Martin Clavo in order to speed up the implementation of the [CERN Service Portal](https://cern.ch/service-portal/) on top of the ServiceNow platform. Several small improvements were added between 2010 and 2015.
