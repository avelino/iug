import os
import socket
import httplib
import urllib
import urlparse
import tempfile
import shutil
import time
from threading import Thread

import gobject


class DownloadItem(gobject.GObject):
    """ Wraps information about a file being downloaded. """

    def __init__(self, name, source, target):
        gobject.GObject.__init__(self)

        self.name = name
        self.source = source
        self.target = target


# Register DownloadItem GObject type
gobject.type_register(DownloadItem)


class URLInfo(gobject.GObject):
    """ Wrapper class for handle information. """

    def __init__(self, handleInfo):
        gobject.GObject.__init__(self)

        self.size = int(handleInfo["Content-Length"])


# Register URLInfo GObject type
gobject.type_register(URLInfo)


class DownloadHandle(gobject.GObject):
    """ Handle object for file downloads. """

    def __init__(self, item, handle):
        gobject.GObject.__init__(self)

        self.item = item
        self.handle = handle
        self.info = URLInfo(handle.info())

        self.bytesRead = 0


# Register DownloadHandle GObject type
gobject.type_register(DownloadHandle)


class FileDownload(gobject.GObject):
    """ Download manager with cancellation and download queue
        capabilities. """

    BLOCK_SIZE = 2048

    def __init__(self):
        gobject.GObject.__init__(self)

        self.excludedMimeTypes = set(['text/html'])
        self._reset()

    def _reset(self):
        self.totalBytes = 0
        self.totalBytesRead = 0
        self.queue = list()
        self.terminated = False

    def terminate(self):
        """ Abort download. """

        self.terminated = True

    def isTerminated(self):
        """ Determine whether the downloader was terminated or not. """

        return self.terminated

    def _isValidHeader(self, data):
        if self.excludedMimeTypes:
            for type in self.excludedMimeTypes:
                if data.gettype() == type:
                    return False
        return True

    def download(self, items):
        """ Download items in the passed item list. Other classes can hook
            into the download process by connecting to the various status
            signals listed at the bottom of this file. """

        # Reset certain variables
        self._reset()

        self.items = items

        # Spawn worker thread
        worker = Thread(target = self._process)

        worker.start()

        # Return thread object
        return worker

    def _process(self):
        # Use FancyURLopener for accessing URLs
        opener = urllib.FancyURLopener()

        # Open URL handles and build download queue
        for item in self.items:
            # Open URL
            handle = opener.open(item.source)

            # Create download handle
            dlHandle = DownloadHandle(item, handle)

            # Check header (exclude mime-types)
            if self._isValidHeader(handle.info()):
                # Append handle to queue
                self.queue.append(dlHandle)
            else:
                pass
                #self.emit("download-error", dlHandle)
                #return
                
        # Determine total bytes to retrieve
        for dlHandle in self.queue:
            self.totalBytes += dlHandle.info.size

        # Download items
        for dlHandle in self.queue:
            # Emit "download-started" signal
            self.emit("download-item-started", dlHandle)

            # Create temporary file for writing the data to
            tmpfileFd, tmpfilePath = tempfile.mkstemp("-download", "i2t-")

            # Read data from the URL handle
            buffer = dlHandle.handle.read(self.BLOCK_SIZE)
            while buffer:
                # Abort download, if requested
                if self.terminated:
                    dlHandle.handle.close()
                    os.close(tmpfileFd)
                    os.remove(tmpfilePath)
                    return

                # Write data to temp file
                os.write(tmpfileFd, buffer)

                # Keep track of the already retrieved bytes
                dlHandle.bytesRead += len(buffer)
                self.totalBytesRead += len(buffer)

                # Emit "download-progress" signal
                self.emit("download-progress", dlHandle)

                # Read next block
                buffer = dlHandle.handle.read(self.BLOCK_SIZE)

            # Close temporary file
            os.close(tmpfileFd)

            # Move temporary file to destination
            shutil.move(tmpfilePath, dlHandle.item.target)

            # Remove temporary file if it still exists
            try:
                os.remove(tmpfilePath)
            except:
                pass

            # Close download file handle
            dlHandle.handle.close()

            # Emit "download-item-finished" signal
            self.emit("download-item-finished", dlHandle)

        # Emit "download-finished" signal
        self.emit("download-finished")


# Register GObject type
gobject.type_register(FileDownload)

# Register "download-progress" signal
gobject.signal_new("download-item-started", FileDownload, \
        gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, \
        [DownloadHandle])

# Register "download-item-finished" signal
gobject.signal_new("download-item-finished", FileDownload, \
        gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, \
        [DownloadHandle])

# Register "download-error" signal
gobject.signal_new("download-error", FileDownload, \
        gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, \
        [DownloadHandle])

# Register "download-progress" signal
gobject.signal_new("download-progress", FileDownload, \
        gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, \
        [DownloadHandle])

# Register "download-finished" signal
gobject.signal_new("download-finished", FileDownload, \
        gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, \
        [])


