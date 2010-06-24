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

import time
from os import path

import gtk
import gobject
from lib.download import FileDownload
from lib.download import DownloadHandle
from lib.utils import GTKWrappers
from lib.constants import *
from lib.logger import Logger
from lib.constants import * 

class ProgressDialogBase(gtk.Dialog):
    def __init__(self, title = None, parent = None, message = ''):
        gtk.Dialog.__init__(self, title, parent, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
        
        self.set_default_size(300, 100)
        vbox = self.vbox

        hbox = gtk.HBox(False, 12)
        hbox.set_border_width(12)
        vbox.pack_start(hbox, True, True)
        
        img = gtk.Image()
        img.set_from_icon_name("system-software-update",gtk.ICON_SIZE_LARGE_TOOLBAR)
        hbox.pack_start(img, False, False)

        vbox = gtk.VBox()
        hbox.pack_end(vbox, True, True)

        lbl = gtk.Label(MSG_000019)
        lbl.set_use_markup(True)
        align = gtk.Alignment(0.0, 0.0)
        align.add(lbl)
        vbox.add(align)

        self.label = gtk.Label("")
        self.label.set_use_markup(True)
        align = gtk.Alignment(0.0, 0.0)
        align.add(self.label)
        vbox.add(align)

        self.progressbar_cache = gtk.ProgressBar()
        vbox.add(self.progressbar_cache)

        self.vbox.show_all()
        
        
        
class ProgressDialog(ProgressDialogBase):
    # Register "download-failed" signal
    #__gsignals__ = { 
    #    "download-failed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (DownloadHandle,))
    #}
    def __init__(self, parent = None, title ='', ):
        ProgressDialogBase.__init__(self, title, parent)
        
        self.set_icon_name("system-software-update")
        
        # Cancel button
        cancelButton = gtk.Button(None, gtk.STOCK_CANCEL)
        cancelButton.connect("clicked", self._cancel)
        self.action_area.add(cancelButton)
        cancelButton.show()
        
        self.workerThread = None
        
        self.downloader = FileDownload()
        
         # Connect to download signals
        self.downloader.connect("download-error", self._error)
        self.downloader.connect("download-item-started", self._itemStarted)
        self.downloader.connect("download-item-finished", self._itemFinished)
        self.downloader.connect("download-finished", self._finished)
        self.downloader.connect("download-progress", self._progress)
        self.downloader.excludedMimeTypes.add("text/html")
        
        # Initialize default progress bar contents
        self.totalBytes = 0
        self.totalBytesRead = 0
    
    def message(self, message):
        "Set the message on the dialog."
        self.label.set_markup(message)

    def download(self, items):
        """ Execute dialog, download the passed list of items. """

        # Show dialog
        self.show()

        # Use passed list as download queue
        self.items = items

        # Force refresh
        while gtk.events_pending():
            gtk.main_iteration(False)

        self.progressbar_cache.set_text(MSG_000004)

        # Start download
        self.workerThread = self.downloader.download(self.items)

        # Enter main loop
        return self.run()

    def _finished(self, downloader):
        gtk.gdk.threads_enter()
        self.response(gtk.RESPONSE_ACCEPT)
        self.hide()
        gtk.gdk.threads_leave()
        

    def _error(self, downloader, handle):
        gtk.gdk.threads_enter()

        # Terminate download process
        downloader.terminate()

        # Emit error signal
        self.emit("download-failed", handle)

        # Log error
        Logger.error("DownloadWizard", MSG_000005 % (handle.item.source))

        # Close dialog
        self.response(gtk.RESPONSE_REJECT)

        gtk.gdk.threads_leave()

    def _itemStarted(self, downloader, handle):
        gtk.gdk.threads_enter()
        self.item = handle.item
        gtk.gdk.threads_leave()

    def _itemFinished(self, downloader, handle):
        gtk.gdk.threads_enter()
        while gtk.events_pending():
            gtk.main_iteration(False)
        gtk.gdk.threads_leave()

    def _progress(self, downloader, handle):
        gtk.gdk.threads_enter()

        self.totalBytes = downloader.totalBytes
        self.totalBytesRead = downloader.totalBytesRead

        self._updateProgressBars()

        gtk.gdk.threads_leave()

    def _updateProgressBars(self):
        if self.downloader.terminated:
            return
        if self.totalBytes != 0:
            totalFraction = float(self.totalBytesRead) / \
                    float(self.totalBytes)
            totalPercent = totalFraction * 100

            totalText = MSG_000007 \
                    % {"percent": totalPercent,
                       "bytes": self.totalBytesRead / 1000,
                       "total": self.totalBytes / 1000}

            self.progressbar_cache.set_fraction(totalFraction)
            self.progressbar_cache.set_text(totalText)
        else:
            self.progressbar_cache.set_text("Total")

        return True

    def _cancel(self, *args):
        if self.workerThread:
            self.downloader.terminate()

        self.response(gtk.RESPONSE_CANCEL)


# Register "download-failed" signal
gobject.signal_new("download-error", ProgressDialog, \
        gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, \
        (DownloadHandle,))
    
