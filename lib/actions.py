# -*- coding: utf-8 -*-

__all__ = ['Actions']

import sys

import dal
import time
import datetime
from lib.utils import force_string
from db.categoriestable import CategoriesTable
from db.gamestable import GamesTable
from db.iugversiontable import IUGVersionTable

from xml import sax as Sax2
from xml.dom import EMPTY_NAMESPACE

class Actions(object):

    def __init__(self, databaselayer=None):
        if not databaselayer:
            databaselayer = dal.DAL()

        self.dal = databaselayer

    def get_games(self, kwargs = None):
        """ Returns one or more records that meet the criteria passed """
        return self.dal.get(GamesTable, kwargs)
    
    def add_game(self, kwargs):
        """ Adds a bill to the database """
        return self.dal.add(GamesTable, kwargs)

    def edit_game(self, kwargs):
        """ Edit a record in the database """
        return self.dal.edit(GamesTable, kwargs)

    def delete_game(self, key):
        """ Delete a record in the database """
        return self.dal.delete(GamesTable, key)

    def get_categories(self, key):
        """ Returns one or more records that meet the criteria passed """
        return self.dal.get(CategoriesTable, key)

    def add_category(self, kwargs):
        """ Adds a category to the database """
        return self.dal.add(CategoriesTable, kwargs)

    def edit_category(self, kwargs):
        """ Edit a record in the database """
        return self.dal.edit(CategoriesTable, kwargs)

    def delete_category(self, key):
        """ Delete a record in the database """
        return self.dal.delete(CategoriesTable, key)
    
    def get_iugversion(self, kwargs = ''):
        """ Returns one or more records that meet the criteria passed """
        return self.dal.get(IUGVersionTable, kwargs)
    
    def add_iugversion(self, kwargs):
        """ Adds a category to the database """
        return self.dal.add(IUGVersionTable, kwargs)
    
    def edit_iugversion(self, kwargs):
        """ Edit a record in the database """
        return self.dal.edit(IUGVersionTable, kwargs)

