# coding: utf-8
#
# ListView - An enhanced listview to make work with TreeView easier
#
# Copyright (C) 2009 Carlos Donizete <coringao@ubuntu.com>
#
# Authors:
#  Laudeci Oliveira <laudeci@ubuntu.com>
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
import gtk
import pango
import gobject
from lib.utils import wrap_text

class DescriptionListStore(gtk.ListStore):
    
    (NAME_COL, VALUE_COL) = range(2)
    
    def __init__(self):
        gtk.ListStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_STRING )
        self.append_method = gtk.ListStore.append
    
    def add_game(self, game):
        """
            @param games a reference to IUG.Games object.
        """
        dic = game.Dictionary
        dicDesc = game.description_dictionary
        self.append_method(self, [dicDesc['game'], dic['game']])
        self.append_method(self, [dicDesc['description'], dic['description']])
        self.append_method(self, [dicDesc['requires'], dic['requires']])
        self.append_method(self, [dicDesc['version'], dic['version']])
        self.append_method(self, [dicDesc['file_size'], dic['file_size']])
        self.append_method(self, [dicDesc['website'], dic['website']])
        self.append_method(self, [dicDesc['download_type'], dic['download_type']])

    def set_sort_order(self, order):
        """
            @param order Either C{gtk.SORT_DESCENDING} or C{gtk.SORT_ASSCENDING}
        """
        if order == gtk.SORT_DESCENDING:
            # Alternatively gtk.TreeStore.prepend for bottom panel layout
            self.append_method = gtk.ListStore.prepend
        else:
            self.append_method = gtk.ListStore.append
    
class DescriptionTreeView(gtk.TreeView):
    """
        Base class upon which other ListView classes will build upon. This class should never be used by
        itself, as some of its methods are inplace soely as place holders (virtual methods)
    """
    
    def __init__(self, model=DescriptionListStore()):
        """
            Prepares object for processing, connects message and event handlers if already specified, also
            connects a backup set object as a propery
        """
        # Call the super class
        gtk.TreeView.__init__ (self, model)
        self.model = model
        #self.model.wrap_width = -1
        self.initializeProperties()
        self.createColumns()
        self.connect("motion-notify-event", self.onTreeviewMotionNotify)
        
    def initializeProperties(self):
        """
            Initializes essential class properies
        """
        self.set_headers_visible(False)
        self.set_rules_hint(True)
        
        pass
    
    def createColumns(self):
        """
            Creates columns used in this treeview.
        """
        # Name column
        cell_name = gtk.CellRendererText()
        cell_name.set_property('scale', 1.0)
        cell_name.set_property("yalign", 0.0)
        self._name_column = gtk.TreeViewColumn("Property",cell_name)
        self._name_column.add_attribute(cell_name, 'markup', self.model.NAME_COL)
        self._name_column.set_cell_data_func(cell_name, self.__name_view_func)
        
        #value column
        cell_text = gtk.CellRendererText()
        cell_text.set_property("wrap-mode", gtk.WRAP_WORD)
        cell_text.set_property("yalign", 0.0)

        self._value_column = gtk.TreeViewColumn("Value", cell_text)
        self._value_column.add_attribute(cell_text, "text", self.model.VALUE_COL)
        self._value_column.set_cell_data_func(cell_text, self.__value_view_func)
        #self._game_column.set_expand(True)
        self._name_column.set_sort_column_id(self.model.VALUE_COL)

        self.append_column(self._name_column)
        self.append_column(self._value_column)
    
    def onTreeviewMotionNotify(self, treeview, event):
        win = self.get_bin_window()
        try:
            current_path, current_column = self.get_path_at_pos(int(event.x), int(event.y))[:2]
        except:
            win.set_cursor(None)
            return
        
        if current_column == self._value_column:
            iter= self.model.get_iter(current_path)
            
            if iter:
                value = self.model.get_value(iter,1)
                if value.find('http://') > -1:
                    if win:
                        win.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
                else:
                    if win:
                        win.set_cursor(None)
            else:
                if win:
                    win.set_cursor(None)
        else:
            if win:
                win.set_cursor(None) 

    def add(self, game ):
        self.model.add_game(game)
        
    def clear(self):
        self.model.clear()
        
    def __name_view_func(self, cell_layout, renderer, model, iter):
        if isinstance(renderer, gtk.CellRendererText):
            text = model.get_value(iter, self.model.NAME_COL)
            markup = "<b>%s:</b>" % text
            renderer.set_property("markup", markup)
    
    def __value_view_func(self, column, renderer, model, iter):
        if isinstance(renderer, gtk.CellRendererText):
            text = model.get_value(iter, self.model.VALUE_COL)
            if (text.find('http://') == -1):
                renderer.set_property('wrap-width',column.get_width() -30)
                renderer.set_property("markup", text)
                renderer.set_property('foreground-gdk',gtk.gdk.color_parse("black"))
                renderer.set_property('underline',False)
            else:
                renderer.set_property('foreground-gdk',gtk.gdk.color_parse("blue"))
                renderer.set_property('underline',True)

    


