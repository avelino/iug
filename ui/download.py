# $Id$
#
# vi:set ts=4 sw=4 sts=4 et ai nocindent:
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307 USA

import time
from os import path

import gtk
import gobject

from lib.constants import *
from lib.download import FileDownload, DownloadHandle
#from lib.threads import GIdleThread, Queue
from lib.logger import Logger
from dialogs import IUGTitledDialog


class DownloadError(Exception):

    def __init__(self, item):
        self.item = item

    def __str__(self):
        return repr(self.item)


class DownloadWizard(IUGTitledDialog):

    def __init__(self, parent, title, showtotalprogress = False):
        IUGTitledDialog.__init__(self, title, parent,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)

        self.show_total_progress = showtotalprogress
        # Basic window setup
        self.set_default_size(500, 0)

        self.workerThread = None

        # Cancel button
        cancelButton = gtk.Button(None, gtk.STOCK_CANCEL)
        cancelButton.connect("clicked", self._cancel)
        self.action_area.add(cancelButton)
        cancelButton.show()

        self.set_icon_name("system-software-update")

        # Progress frame
        progressBox = gtk.VBox(False, 6)
        progressBox.set_border_width(6)
        self.vbox.pack_start(progressBox, False, True, 0)
        progressBox.show()

        # Item progress bar
        self.itemProgress = gtk.ProgressBar()
        progressBox.add(self.itemProgress)
        self.itemProgress.show()
        if self.show_total_progress:
            # Total progress bar
            self.totalProgress = gtk.ProgressBar()
            progressBox.add(self.totalProgress)
            self.totalProgress.show()

        # Create file download object
        self.downloader = FileDownload()

        # Connect to download signals
        self.downloader.connect("download-error", self._error)
        self.downloader.connect("download-item-started", self._itemStarted)
        self.downloader.connect("download-item-finished", self._itemFinished)
        self.downloader.connect("download-finished", self._finished)
        self.downloader.connect("download-progress", self._progress)
        #self.downloader.excludedMimeTypes.add("text/html")

        # Initialize default progress bar contents
        self.totalBytes = 0
        self.totalBytesRead = 0
        self.itemBytes = 0
        self.itemBytesRead = 0
        self.itemName = str()

    def setTitle(self, str):
        self.set_title(str)
        self.set_subtitle(str)

    def download(self, items):
        """ Execute dialog, download the passed list of items. """

        # Show dialog
        self.show()

        # Use passed list as download queue
        self.items = items

        # Force refresh
        while gtk.events_pending():
            gtk.main_iteration(False)

        self.itemProgress.set_text(MSG_000004)
        if self.show_total_progress:
            self.totalProgress.set_text(MSG_000004)

        # Start download
        self.workerThread = self.downloader.download(self.items)

        # Enter main loop
        return self.run()
        #self.show()

    def _finished(self, downloader):
        gtk.gdk.threads_enter()
        self.response(gtk.RESPONSE_ACCEPT)
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
        self.set_subtitle(MSG_000006 % handle.item.name)
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
        self.itemBytes = handle.info.size
        self.itemBytesRead = handle.bytesRead
        self.itemName = handle.item.name

        self._updateProgressBars()

        gtk.gdk.threads_leave()

    def _updateProgressBars(self):
        if self.downloader.terminated:
            return
        if self.show_total_progress:
            if self.totalBytes != 0:
                totalFraction = float(self.totalBytesRead) / \
                        float(self.totalBytes)
                totalPercent = totalFraction * 100
    
                totalText = MSG_000007 \
                        % {"percent": totalPercent,
                           "bytes": self.totalBytesRead / 1000,
                           "total": self.totalBytes / 1000}
    
                self.totalProgress.set_fraction(totalFraction)
                self.totalProgress.set_text(totalText)
            else:
                self.totalProgress.set_text("Total")

        if self.itemBytes != 0:
            itemFraction = float(self.itemBytesRead) / float(self.itemBytes)
            itemPercent = itemFraction * 100

            itemText = MSG_000008 \
                    % {"name": self.itemName,
                       "percent": itemPercent,
                       "bytes": self.itemBytesRead / 1000,
                       "total": self.itemBytes / 1000}

            self.itemProgress.set_fraction(itemFraction)
            self.itemProgress.set_text(itemText)
        else:
            self.itemProgress.set_text(self.itemName)

        return True

    def _cancel(self, *args):
        if self.workerThread:
            self.downloader.terminate()

        self.response(gtk.RESPONSE_CANCEL)


# Register "download-failed" signal
gobject.signal_new("download-failed", DownloadWizard, \
        gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, \
        [DownloadHandle])


