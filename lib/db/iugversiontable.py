# -*- coding: utf-8 -*-

__all__ = ['IUGVersionTable']

from generictable import GenericTable

class IUGVersionTable(GenericTable):
    """ Table to hold version information for all tables. """
    Version = 1
    Key = "id"
    KeyAuto = False
    Name = "iug_IUGVersionTable"
    CreateSQL = """
        CREATE TABLE %s (
        id INTEGER PRIMARY KEY NOT NULL,
        version  float NOT NULL,
        version_date DATETIME NOT NULL)
    """ % Name
    Fields = ['id', 'version', 'version_date']