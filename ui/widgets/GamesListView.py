# coding: utf-8
#
# ListView - An enhanced listview to make work with TreeView easier
#
# Copyright (C) 2008 Laudeci Oliveira.
#
# Authors:
#  Laudeci Oliveira <laudeci@gmail.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
#
import os
import gc 
import gtk
import pango
import gobject
from math import log
from lib.utils import load_pixbuf_image
from lib.constants import *
class GamesListStore(gtk.ListStore):
    
    (PIC_COL, NAME_COL, STARS_COL, GAME_COL, IMG_SET_COL) = range(5)
    
    def __init__(self):
        gtk.ListStore.__init__(self, gtk.gdk.Pixbuf, gobject.TYPE_STRING,gobject.TYPE_INT, gobject.TYPE_PYOBJECT, gobject.TYPE_BOOLEAN)
        self.append_method = gtk.ListStore.append
        self.pixbuf_default = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True ,8, 48, 48)
    
    def add_games(self, games):
        """
            @param games a list of IUG.Games object.
        """
        for game in games:
            item = [self.pixbuf_default, game.game, game.rate, game, False]
            self.append_method(self, item)
    
    def add_game(self, game):
        """
            @param games a reference to IUG.Games object.
        """
        pixbuf, isdefault = load_pixbuf_image(game.image_filename)
        pixscaled = pixbuf.scale_simple(48,48,gtk.gdk.INTERP_HYPER)
        item = [pixscaled, game.game, game.rate, game, False]
        self.append_method(self, item)
    
    def set_sort_order(self, order):
        """
            @param order Either C{gtk.SORT_DESCENDING} or C{gtk.SORT_ASSCENDING}
        """
        if order == gtk.SORT_DESCENDING:
            # Alternatively gtk.TreeStore.prepend for bottom panel layout
            self.append_method = gtk.ListStore.prepend
        else:
            self.append_method = gtk.ListStore.append
    
class GamesListView(gtk.TreeView):
    """
        Base class upon which other ListView classes will build upon. This class should never be used by
        itself, as some of its methods are inplace soely as place holders (virtual methods)
    """
    
    __gsignals__ = { 
        "game-selected": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
    }
    
    def __init__(self, model=GamesListStore()):
        """
            Prepares object for processing, connects message and event handlers if already specified, also
            connects a backup set object as a propery
        """
        # Call the super class
        gtk.TreeView.__init__ (self, model)
        self.model = model
        self.initializeProperties()
        
        self.connect("cursor-changed", self.__on_cursor_changed)
        self.createColumns()
        
    def initializeProperties(self):
        """
            Initializes essntial class properies
        """
        self.icons = gtk.icon_theme_get_default()
        self.stars = self.__get_stars()
       
    def __get_stars(self):
        """Return a prerendered list of rating stars pixbufs"""
        stars = []
        try:
            pixbuf_star = self.icons.load_icon("gnome-app-install-star", 16, 0)
        except gobject.GError:
            pixbuf_star = self.icons.load_icon(gtk.STOCK_MISSING_IMAGE, 16, 0)
        for i in range(5):
            starlets = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True,
                                     8, 96, 16) # depth, width, height
            starlets.fill(0x0)
            for l in range(i+1):
                pixbuf_star.copy_area(0,0,        # from
                                      16,16,      # size
                                      starlets,   # to-pixbuf
                                      20 * l, 0)  # dest
            stars.append(starlets)
        return stars
    
    def createColumns(self):
        """
            Creates columns used in this treeview.
        """
        # Game column
        cell_icon = gtk.CellRendererPixbuf()
        cell_icon.set_property("xpad", 10)
        cell_text = gtk.CellRendererText()
        cell_text.set_property ("ellipsize", pango.ELLIPSIZE_END)
        cell_text.set_property("yalign", 0)
        self._game_column = gtk.TreeViewColumn(MSG_000010)
        self._game_column.pack_start(cell_icon, expand=False)
        self._game_column.add_attribute(cell_icon, "pixbuf", self.model.PIC_COL)
        self._game_column.pack_start(cell_text)
        self._game_column.add_attribute(cell_text, "markup", self.model.NAME_COL)
        #self._game_column.set_cell_data_func(cell_icon, self.__game_view_func)
        self._game_column.set_cell_data_func(cell_text, self.__game_view_func)
        self._game_column.set_expand(True)
        self._game_column.set_sort_column_id(self.model.GAME_COL)
        self._game_column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)

        # popcon renderer
        renderer_popcon = gtk.CellRendererPixbuf()
        renderer_popcon.set_property("xpad", 4)
        self._popcon_column = gtk.TreeViewColumn(MSG_000020, renderer_popcon)
        self._popcon_column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self._popcon_column.set_sort_column_id(self.model.STARS_COL)
        self._popcon_column.set_cell_data_func(renderer_popcon, self.__popcon_view_func)
        self._popcon_column.set_fixed_width(108)

        self.append_column(self._game_column)
        self.append_column(self._popcon_column)
    
    def add(self, game ):
        self.model.add_game(game)
        
    def clear(self):
        self.model.clear()
    
    def get_selected_game(self):
        path = self.get_cursor()[0]
        iter = self.get_model().get_iter(path)
        return self.model.get_value(iter, self.model.GAME_COL)
        
    def __on_cursor_changed(self, treeview):
        path = treeview.get_cursor()[0]
        iter = treeview.get_model().get_iter(path)
        self.emit('game-selected',self.model.get_value(iter, self.model.GAME_COL))
    
    def __popcon_view_func(self, cell_layout, renderer, model, iter):
        """
        Create a pixmap showing a row of stars representing the popularity
        of the corresponding application
        """
        
        value = model.get_value(iter, self.model.STARS_COL)

        rank = 0
        if value > 0:
            rank = int(5 * log(value) / log(6))
        renderer.set_property("pixbuf", self.stars[rank])
    
    def __game_view_func(self, cell_layout, renderer, model, iter):
        if isinstance(renderer, gtk.CellRendererPixbuf):
            #if not model.get_value(iter, model.IMG_SET_COL):
            game = model.get_value(iter, model.GAME_COL)
            pixbuf, isdefault = load_pixbuf_image(game.image_filename)
            model.set_value(iter,model.IMG_SET_COL,True)
            pixscaled = pixbuf.scale_simple(48,48,gtk.gdk.INTERP_HYPER)
            model.set_value(iter,model.PIC_COL,pixscaled)
            gc.collect() # Tell Python to clean up the memory
                
        elif isinstance(renderer, gtk.CellRendererText):
            game = model.get_value(iter, self.model.GAME_COL)
            markup = MSG_000021 % (game.game, game.description, game.file_size, game.version)
            renderer.set_property("markup", markup)
        

