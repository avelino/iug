#!/usr/bin/env python
# coding: utf-8
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
__version__ = "1.0"
__author__ = 'Laudeci "Pretto" Oliveira'

# internal imports
from warnings import warn
import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gtk.gdk
import gobject
import pango

import os
import gc
import sys
import re
import subprocess
import tempfile
import warnings
import locale

# iug imports
import ui
import ui.widgets
import ui.aboutdialog
from ui.widgets.SearchEntry import SearchEntry
from ui.widgets.GamesListView import GamesListView
from ui.widgets.DescriptionListView import DescriptionTreeView
from ui.download import DownloadWizard
from ui.download import DownloadError
from ui.progressdialog import ProgressDialog
from ui.cachedialog import CacheDialog
from lib.actions import Actions
from lib.download import DownloadItem
from lib.versionchecker import IUGVersionChecker
from lib.Game import Game
import lib.utils
from lib.utils import load_pixbuf_image
from lib.utils import ZoomWindow
from lib.utils import GTKWrappers
from lib.utils import get_current_date
from lib.utils import XML2obj
from lib.utils import decode
from lib.utils import get_file_name
from lib.utils import gunzip
from lib.constants import *

warnings.filterwarnings("ignore", "ICON:.*", UserWarning)


gtk.gdk.threads_init()

class IUG():
    
    def __init__(self):
        self.gui = GTKWrappers()
        self.actions = Actions()
        
        # setup a default icon
        self.icons = gtk.icon_theme_get_default()
        self.current_category_id = 0
        
        self.gui.get_glade(MAIN_GLADE, 'window_main')
        #Main widget
        self.window_main = self.gui.get_widget('window_main')
        self.window_main.set_icon(load_pixbuf_image('iug')[0])
    
        # Sexy search entry
        self.search_hbox = self.gui.get_widget('search_hbox')
        self.search_entry = SearchEntry(self.icons)
        self.search_hbox.add(self.search_entry)
        self.search_entry.show()
        
        #creates the GamesListView to view a list of games
        self.scrolled_window = self.gui.get_widget('scrolled_window')
        self.treeview_games = GamesListView()
        self.scrolled_window.add(self.treeview_games)
        self.treeview_games.show()
        
        #create the description listview to show games info.
        self.scrolled_description = self.gui.get_widget('scrolled_description')
        self.treeview_description = DescriptionTreeView()
        self.scrolled_description.add(self.treeview_description)
        self.treeview_description.show()
        
        #Application menu
        self.menu_download = self.gui.get_widget('menu_download')
        self.menu_download.set_sensitive(False)
        self.menu_viewsite = self.gui.get_widget('menu_viewsite')
        self.menu_viewsite.set_sensitive(False)
        self.menu_quit = self.gui.get_widget('menu_quit')
        self.menu_preferences = self.gui.get_widget('menu_preferences')
        self.menu_fullscreen = self.gui.get_widget('menu_fullscreen')
        self.menu_fullscreen.set_sensitive(False)
        self.menu_reportbug = self.gui.get_widget('menu_reportbug')
        self.menu_about = self.gui.get_widget('menu_about')

        #Application buttons
        self.button_close = self.gui.get_widget('button_close')
        self.button_download = self.gui.get_widget('button_download')
        self.button_zoom = self.gui.get_widget("button_zoom")
        self.menu_viewsite.set_sensitive(False)
        self.button_download.set_sensitive(False)
        self.menu_download.set_sensitive(False)
        self.button_zoom.set_sensitive(False)
        
        # image widget to show the game screenshot
        self.image_game = self.gui.get_widget('image_game')
        # create the category treeview
        self.treeview_categories = self.gui.get_widget('treeview_categories')
        renderer_cat_name = gtk.CellRendererText()
        renderer_cat_name.set_property('scale', 1.0)
        column_cat = gtk.TreeViewColumn(MSG_000001,renderer_cat_name)
        column_cat.add_attribute(renderer_cat_name, 'markup', COL_CAT_NAME)
        self.treeview_categories.append_column(column_cat)
        self.treeview_categories.set_search_column(COL_CAT_NAME)
        self.category_selection = self.treeview_categories.get_selection()
        self.category_selection.set_mode(gtk.SELECTION_SINGLE)
        
        self.window_main.show()
        self.connect_events()
        
        self.check_version()
        
        self.fill_category()
        
        self.search_entry.grab_focus()
        
    def connect_events(self):
        # Make things responsible
        self.gui.connect(self.button_zoom,'clicked', self.on_zoom)
        self.gui.connect(self.menu_fullscreen,'activate', self.on_zoom)
        self.gui.connect(self.menu_viewsite,'activate', self.on_menu_viewsite)
        self.gui.connect(self.window_main, 'delete-event', gtk.main_quit)
        self.gui.connect(self.window_main, 'destroy', gtk.main_quit)
        self.gui.connect(self.menu_quit, 'activate', gtk.main_quit)
        self.gui.connect(self.treeview_games,"game-selected", self.on_treeview_games_selected)
        self.gui.connect(self.category_selection,'changed', self.on_treeview_categories_changed)
        self.gui.connect(self.button_download, 'clicked', self.on_button_download)
        self.gui.connect(self.menu_download, 'activate', self.on_button_download)
        self.gui.connect(self.menu_reportbug, 'activate', self.on_menu_reportbug)
        self.gui.connect(self.menu_about, 'activate', self.on_menu_about)
        self.search_entry.connect("terms-changed", self.on_search)
    
    def download_images(self, categoryid):
        need_download = []
        cat = self.actions.get_games({'category':categoryid})
        if cat:
            for n in cat:
                if load_pixbuf_image(n['image_file'])[1]:
                    need_download.append(n)
        if len(need_download)>0:
            dialog = ProgressDialog(self.window_main ,'') 
            dialog.connect("download-failed", self._fileDownloadFailed)
            
            # Download queue
            downloadItems = set()
            for n in need_download:
                    downloadItems.add(DownloadItem('%s image' % n['game'], n['image_url'], os.path.join(CONFIG_DIR, n['image_file'])))
                    
            # Try to download all items
            #response = dialog.download(downloadItems)
            dialog.message('Downloading Games images...')
            response = dialog.download(downloadItems)

            # Destroy wizard
            dialog.destroy()

            # Abort installation if user pressed cancel during the download
            #if response == gtk.RESPONSE_ACCEPT:
            self.window_main.set_sensitive(True) 
             
    def on_search(self, widget, search_string):
        print 'on_search' 
        self.gui.setBusy(self.window_main, True)
        search_terms = search_string.lower()
        model = self.treeview_games.get_model()
        if search_terms != None:
            for it in lib.utils.iterate_list_store(model, model.get_iter_first()):
                aname = model.get_value(it, COL_ITEM).lower()
                if search_terms in aname.split(' '):
                    print "selecting: %s (%s)" % (search_terms, model.get_path(it))
                    self.treeview_games.set_cursor(model.get_path(it))
                    self.gui.setBusy(self.window_main, False)
                    return
        elif len(model) > 0:
            self.treeview_games.set_cursor(0)
        self.gui.setBusy(self.window_main, False)
        
    def on_menu_viewsite(self,widget):
    	game = self.treeview_games.get_selected_game()
    	website = game.website
    	lib.utils.url_open(website)
    
    def on_menu_reportbug(self,widget):
        lib.utils.url_open('https://bugs.edge.launchpad.net/iug/+filebug')

    def on_menu_about(self,widget):
    	dialog = ui.aboutdialog.AboutDialog()
    
    def check_version(self):
        version = IUGVersionChecker()
        if not version.check_version(self.actions):
            dlg = CacheDialog(self.window_main)
            title = MSG_000002
            dlg.set_title(title)
            
            result = dlg.run()
            dlg.destroy()
            if result == gtk.RESPONSE_YES :
                dialog = DownloadWizard(self.window_main,MSG_000003, True)
                dialog.connect("download-failed", self._fileDownloadFailed)
                
                # Download queue
                downloadItems = set()
        
                downloadItems.add(DownloadItem(MSG_000011, 'http://archive.ubuntugames.org/iug/version.txt', '/tmp/version.txt'))
                downloadItems.add(DownloadItem(MSG_000012, 'http://archive.ubuntugames.org/iug/iug.xml', '/tmp/iug.xml'))
                
                # Try to download all items
                response = dialog.download(downloadItems)
        
                # Destroy wizard
                dialog.destroy()
        
                # Abort installation if user pressed cancel during the download.
                txt_file = '/tmp/version.txt'
                xml_file = '/tmp/iug.xml'
                if response == gtk.RESPONSE_ACCEPT:
                    if os.path.exists(txt_file) and os.path.exists(txt_file):
                            self.parse_files(txt_file, xml_file)
                    else:
                        dlg_error = gtk.MessageDialog(None, gtk.DIALOG_MODAL,	gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, None)
                        dlg_error.set_markup(txt_file + ' or ' + xml_file + '\n\nFile not found. Verify if the download was done.')
                        dlg_error.run()
                        dlg_error.destroy()
                        print 'File not found. Verify if the download was done.'
                    
        self.window_main.set_sensitive(True)    
    
    def on_button_download(self, widget):
        game = self.treeview_games.get_selected_game()
        download_type = game.download_type
        install_command = game.download_url
        if download_type == 'wget':
            self.gui.show_info('<b>%s</b>\n%s' % (download_type,install_command), self.window_main)
            dialog = ProgressDialog(self.window_main ,'') 
            dialog.connect("download-failed", self._fileDownloadFailed)
            # Download queue
            downloadItems = set()
            filedownload = os.path.join('/tmp/',game.download_url.split('/')[-1])
            downloadItems.add(DownloadItem(game.game,game.download_url, filedownload))

            # Try to download all items
            #response = dialog.download(downloadItems)
            dialog.message('Downloading Game...')
            response = dialog.download(downloadItems)
            
            if response == gtk.RESPONSE_ACCEPT:
                commands = game.install_command.split('|')
                if lib.utils.get_mimetype(filedownload) == 'application/x-tar':
                    gunzip(filedownload)
                
            # Destroy wizard
            dialog.destroy()
        elif download_type =='deb':
            print 'gnome-terminal --command sudo dpkg -i %s' % game.install_command
            os.system('gnome-terminal --command sudo dpkg -i %s' % game.deb_filename)
        else:
            self.gui.show_info('Instalando:%s' % download_type, self.window_main)
            
    def on_zoom(self, widget):
        zoom = ZoomWindow(self.window_main, self.treeview_games.get_selected_game().image_filename)
        zoom.run()
        
    def _fileDownloadFailed(self, wizard, handle):
        print "Could not fetch file.", handle.item.source
    
    def parse_files(self, versionfile, xmlfile):
        self.gui.setBusy(self.window_main)
       	dversion = open(versionfile).readline()
        dversion = float(dversion)
        print "version:", dversion
        rec = self.actions.get_iugversion()[0]
        id = rec['id']
        lversion = rec['version']
        
        print id, lversion , lversion < dversion,lversion , dversion
        if lversion < dversion :
            self.actions.edit_iugversion({'version': dversion,'id': id, 'version_date': get_current_date()})
            xFile = XML2obj(xmlfile)
            xobj = xFile.get_python_from_xml()
            game = xobj.game
            for n in game:
                exist = self.actions.get_categories({'categoryname':decode(n.category)})
                if not exist:
                    self.actions.add_category({'categoryname':decode(n.category)})
                cat = self.actions.get_categories({'categoryname':decode(n.category)})[0]
                game_exist = self.actions.get_games({'game': decode(n.name)})
                print decode(n.description)
                if not game_exist :
                    game_dict=dict({'category': cat['id'],
                        'game': decode(n.name),
                        'description': decode(n.description),
                        'image_url': decode(n.image_url),
                        'image_file': get_file_name(decode(n.image_url)),
                        'requires': decode(n.requires),
                        'download_url':decode(n.download_url),
                        'download_type':decode(n.download_type),
                        'file_size':decode(n.file_size),
                        'website': decode(n.site),
                        'deb_filename':decode(n.deb_filename),
                        'install_command':decode(n.install_command),
                        'version':decode(n.version),
                        'file_size': decode(n.file_size),
                        'rate':decode(n.rate)})
                    
                    self.actions.add_game(game_dict);
                else:
                    game_dict=dict({'category': cat['id'],
                        'id' : game_exist[0]['id'],
                        'game': decode(n.name),
                        'description': decode(n.description),
                        'image_url': decode(n.image_url),
                        'image_file': get_file_name(decode(n.image_url)),
                        'requires': decode(n.requires),
                        'download_url':decode(n.download_url),
                        'download_type':decode(n.download_type),
                        'file_size':decode(n.file_size),
                        'website': decode(n.site),
                        'deb_filename':decode(n.deb_filename),
                        'install_command':decode(n.install_command),
                        'version':decode(n.version),
                        'file_size': decode(n.file_size),
                        'rate':decode(n.rate)})
                    
                    self.actions.edit_game(game_dict)
                    

        self.gui.setBusy(self.window_main, True)    
            
    def fill_category(self):
        self.gui.setBusy(self.window_main, True)
        model = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_INT)
        self.treeview_categories.set_model(model)
        
        cat = self.actions.get_categories('')
        #added a category to show all games in the list
        model.append([MSG_000026,0])
        for n in cat:
            model.append([n['categoryname'],n['id']])
        
        self.gui.setBusy(self.window_main)
    
    def fill_games(self, categoryid):
        self.gui.setBusy(self.window_main, True)
        self.treeview_games.clear()
        if categoryid == 0:
            cat = self.actions.get_games()
        else:
            cat = self.actions.get_games({'category':categoryid})
        if cat:
            self.download_images(categoryid)
            for n in cat:
                game = Game(n['game'])
                game.game_id = n['id']
                game.category = n['category']
                game.rate = n['rate']
                game.description = n['description']
                game.image_filename = n['image_file']
                game.version = n['version']
                game.file_size = n['file_size']
                game.image_url = n['image_url']
                game.website = n['website']
                game.requires = n['requires']
                game.install_command =  n['install_command']
                game.deb_filename = n['deb_filename']
                game.download_url = n['download_url']
                game.download_type= n['download_type']
                game.localpicture = not load_pixbuf_image(game.image_filename)[1]
                self.treeview_games.add(game)
        self.gui.setBusy(self.window_main)
    
    # widget event handler
    
    def on_treeview_games_selected(self, widget, game):
        self.treeview_description.clear()
        self.image_game.clear()
        self.menu_viewsite.set_sensitive(True)
        self.button_download.set_sensitive(True)
        self.menu_download.set_sensitive(True)
        self.button_zoom.set_sensitive(True)
        self.menu_fullscreen.set_sensitive(True)
        self.treeview_description.add(game)
        pixbuf,isdefault = load_pixbuf_image(game.image_filename)
        pixscaled = self.gui.scale(pixbuf,192,192)
        self.image_game.set_from_pixbuf(pixscaled)
    
    def on_treeview_categories_changed(self, treeview):
        model, iter = treeview.get_selected()
        if iter:
            self.menu_viewsite.set_sensitive(False)
            self.button_download.set_sensitive(False)
            self.menu_download.set_sensitive(False)
            self.button_zoom.set_sensitive(False)
            self.menu_fullscreen.set_sensitive(False)
            self.treeview_description.clear()
            self.image_game.clear()
            self.fill_games( model.get_value(iter,COL_CAT_ITEM))
        
        
# Entry point for testing in source tree
if __name__ == '__main__':
    app = IUG()
    gtk.main()        
