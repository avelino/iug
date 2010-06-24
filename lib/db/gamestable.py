# -*- coding: utf-8 -*-

__all__ = ['GamesTable']

from generictable import GenericTable

class GamesTable(GenericTable):
    """ Table to hold games category information. """
    Version = 3
    Key = "id"
    KeyAuto = True
    Name = "iug_gamesTable"
    CreateSQL = """
        CREATE TABLE %s (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category INTEGER NOT NULL,
            game VARCHAR(50) NOT NULL,
            description TEXT,
            image_url VARCHAR(255),
            image_file VARCHAR(100),
            requires varchar(255),
            download_url VARCHAR(255),
            download_type VARCHAR(30),
            file_size   VARCHAR (30),
            website varchar(250),
            deb_filename VARCHAR(255),
            install_command  VARCHAR(255),
            version VARCHAR(30),
            rate INT
            )
    """ % Name
    Fields = ['id', 'game','category', 'description', 'image_url', 'image_file', \
              'requires','website', 'download_url', 'download_type', 'file_size', \
              'deb_filename', 'install_command', 'version', 'rate']