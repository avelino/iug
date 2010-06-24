# coding: utf-8
#
# Copyright (C) 2008 Carlos Donizete <coringao@jabber.com>
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

import gtk
import gobject

from lib.utils import GTKWrappers
from lib.constants import *
    
class CacheDialog():
    def __init__(self, parent):
        self.gui = GTKWrappers()
        self.gui.get_glade(MAIN_GLADE, 'dialog_outdated')
        #Main widget
        self.window_main = self.gui.get_widget( 'dialog_outdated')
        self.window_main.set_icon_name("system-software-update")
        self.title_label = self.gui.get_widget( 'label20')
        self.window_main.realize()
        self.window_main.set_default_size(800, 0)
        self.window_main.set_transient_for(parent)
        parent.set_sensitive(False)
       
    def set_title(self, title):
        self.title_label.set_markup(title)        
    def run(self):
        return self.window_main.run()
    def hide(self):
        self.window_main.hide()
    def destroy(self):
        self.window_main.destroy()
        
