# -*- coding: utf-8 -*-
#
#  Laudeci Oliveira <laudeci@gmail.com>
#
#  Copyright 2009 Ubuntu Games DevTeam.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published
#  by the Free Software Foundation; version 2 only.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
from constants import *

class Game(object):
    """
        This class holds games info. 
    """

    def __init__(self, game_name = ''):
        self.__id = 0
        self.__game = game_name
        self.__category = ''
        self.__description = ''
        self.__image_url = ''
        self.__image_file = ''
        self.__requires = ''
        self.__website = ''
        self.__download_url = ''
        self.__download_type = ''
        self.__file_size = ''
        self.__deb_filename = ''
        self.__install_command = ''
        self.__version = ''
        self.__points = 0
        self.__localpicture = False
    
    def __get_game_id(self): return self.__id
    def __set_game_id(self, value): self.__id = value
    game_id = property(fget = __get_game_id, fset = __set_game_id, doc = 'Get/Set Game id.')
    
    def __get_game_name(self): return self.__game
    def __set_game_name(self, value): self.__game = value
    game = property(fget = __get_game_name, fset = __set_game_name, doc = 'Get/Set Game name.')
    
    def __get_category(self): return self.__category
    def __set_category(self, value): self.__category = value
    category = property(fget = __get_category, fset = __set_category, doc = 'Get/Set Game category name.')
    
    def __get_game_description(self): return self.__description
    def __set_game_description(self, value): self.__description = value
    description = property(fget = __get_game_description, fset = __set_game_description, doc = 'Get/Set Game description.')
    
    def __get_game_image_url(self): return self.__image_url
    def __set_game_image_url(self, value):
        self.__image_url = value
        self.__image_file = value.split('/')[-1]
    image_url = property(fget = __get_game_image_url, fset = __set_game_image_url, doc = 'Get/Set Game Image URL used as screenshot.')
    
    def __get_game_image_file(self): return self.__image_file
    def __set_game_image_file(self, value): self.__image_file = value
    image_filename = property(fget = __get_game_image_file, fset = __set_game_image_file, doc = 'Get/Set Game Image filename.')
    
    def __get_game_requires(self): return self.__requires
    def __set_game_requires(self, value): self.__requires = value
    requires = property(fget = __get_game_requires, fset = __set_game_requires, doc = 'Get/Set system especification to play the game.')
    
    def __get_game_website(self): return self.__website
    def __set_game_website(self, value): self.__website = value
    website = property(fget = __get_game_website, fset = __set_game_website, doc = 'Get/Set Game website developer.')
    
    def __get_download_url(self): return self.__download_url
    def __set_download_url(self, value): self.__download_url = value
    download_url = property(fget = __get_download_url, fset = __set_download_url, doc = 'Get/Set Game url for download.')
    
    def __get_download_type(self): return self.__download_type
    def __set_download_type(self, value): self.__download_type = value
    download_type = property(fget = __get_download_type, fset = __set_download_type, doc = 'Get/Set type of comando to download the game.')
    
    def __get_file_size(self): return self.__file_size
    def __set_file_size(self, value): self.__file_size = value
    file_size = property(fget = __get_file_size, fset = __set_file_size, doc = 'Get/Set game file size.')
    
    def __get_deb_filename(self): return self.__deb_filename
    def __set_deb_filename(self, value): self.__deb_filename = value
    deb_filename = property(fget = __get_deb_filename, fset = __set_deb_filename, doc = 'Get/Set the deb filename for install the game.')
    
    def __get_install_command(self): return self.__install_command
    def __set_install_command(self, value): self.__install_command = value
    install_command = property(fget = __get_install_command, fset = __set_install_command, doc = 'Get/Set a list that contains commands to install the game')
    
    def __get_version(self): return self.__version
    def __set_version(self, value): self.__version = value
    version = property(fget = __get_version, fset = __set_version, doc = 'Get/Set the version of the game.')
    
    def __get_rate(self): return self.__rate
    def __set_rate(self, value): self.__rate = value
    rate = property(fget = __get_rate, fset = __set_rate, doc = 'Get/Set points that shows the game rating from 0 to 5.')
    
    def __get_localpicture(self): return self.__localpicture
    def __set_localpicture(self, value): self.__localpicture = value
    localpicture = property(fget = __get_localpicture, fset = __set_localpicture, doc = '')
    
    def __get_fields_description(self):
        return dict(
            {
            'category': MSG_000001,
            'game': MSG_000013,
            'description': MSG_000014,
            'requires': MSG_000015,
            'file_size': MSG_000016,
            'website': MSG_000017,
            'version': MSG_000018,
            'download_type': 'Instalation Type'}
            )
    description_dictionary = property(fget=__get_fields_description,
                          doc='Gets a dictionary representation of games descriptions.')
    
    def __get_dictionary(self):
        return dict({
            'Id': self.__id,
            'category': self.__category,
            'game': self.__game,
            'description': self.__description,
            'image_url': self.__image_url,
            'image_file': self.__image_file,
            'requires': self.__requires,
            'download_url':self.__download_url,
            'download_type':self.__download_type,
            'file_size':self.__file_size,
            'website': self.__website,
            'deb_filename':self.__deb_filename,
            'install_command':self.__install_command,
            'version':self.__version,
            'rate':self.__rate,
            'localpicture': self.__localpicture}) 
    Dictionary = property(fget=__get_dictionary,
                          doc='Gets a dictionary representation of game.')
    
    
