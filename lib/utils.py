# -*- coding: utf-8 -*-
#
#  Laudeci Oliveira <laudeci@ubuntu.com>
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
import os
import gtk
import gc
import webbrowser 
from gtk import glade
import datetime
import sys, string
import re
import gzip
import bz2
import tarfile
import mimetypes
import xml.sax.handler
from defaulticon import xpm_data
from lib.constants import *


non_id_char = re.compile('[^_0-9a-zA-Z]')

def get_mimetype(file):
    mimetypes.init()
    return mimetypes.guess_type(file)[0]

def gunzip(file):
    '''Gunzip the given file and then remove the file.'''
    
    archive = tarfile.open(file,'r:gz')
    archive.debug = 1    # Display the files beeing decompressed.
    for tarinfo in archive:
        archive.extract(tarinfo, r'/tmp') 
    archive.close()

def _name_mangle(name):
    return non_id_char.sub('_', name)

def wrap_text(text, width = 60):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width = width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

def decode(result):
    try:
        return result.encode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError), e:
         print str(e);
         return  result.replace(result[e.start],'\xc2\xae')
    except:
        if not result:    
            return ''

def get_current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def get_file_name(sname):
    if len(sname) >0:
        return sname.split('/')[-1]
    else:
        return sname

def load_pixbuf_image(image_name):
        if os.path.exists(os.path.join(CONFIG_DIR , '%s') % image_name):
            return gtk.gdk.pixbuf_new_from_file(os.path.join(CONFIG_DIR , '%s') % image_name), False
        else:
            pixmap = gtk.gdk.pixbuf_new_from_xpm_data(xpm_data)
            return pixmap, True #tk.gdk.pixbuf_new_from_file(os.path.expanduser('~/.iug/ubuntugames.png')) , True
        
class XML2obj():
    """
        A simple class to converts XML data into native Python object.
    """
    
    
    def __init__(self, inFileName):
        self.src = ""
        for n in open(inFileName).readlines():
            self.src = self.src + str(n)
        
    def get_python_from_xml(self):
        builder = TreeBuilder()
        if isinstance(self.src,basestring):
            xml.sax.parseString(self.src, builder)
        else:
            xml.sax.parse(self.src, builder)
        return builder.root._attrs.values()[0]
    
class DataNode(object):
    def __init__(self):
        self._attrs = {}    # XML attributes and child elements
        self.data = None    # child text data
        
    def __len__(self):
        # treat single element as a list of 1
        return 1
    
    def __getitem__(self, key):
        if isinstance(key, basestring):
            return self._attrs.get(key,None)
        else:
            return [self][key]
        
    def __contains__(self, name):
        return self._attrs.has_key(name)
    
    def __nonzero__(self):
        return bool(self._attrs or self.data)
    
    def __getattr__(self, name):
        if name.startswith('__'):
            # need to do this for Python special methods???
            raise AttributeError(name)
        return self._attrs.get(name,None)
    
    def _add_xml_attr(self, name, value):
        if name in self._attrs:
            # multiple attribute of the same name are represented by a list
            children = self._attrs[name]
            if not isinstance(children, list):
                children = [children]
                self._attrs[name] = children
            children.append(value)
        else:
            self._attrs[name] = value
            
    def __str__(self):
        return self.data or ''
    
    def __repr__(self):
        items = sorted(self._attrs.items())
        if self.data:
            items.append(('data', self.data))
        return u'{%s}' % ', '.join([u'%s:%s' % (k,repr(v)) for k,v in items])
        
class TreeBuilder(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.stack = []
        self.root = DataNode()
        self.current = self.root
        self.text_parts = []
        
    def startElement(self, name, attrs):
        self.stack.append((self.current, self.text_parts))
        self.current = DataNode()
        self.text_parts = []
        # xml attributes --> python attributes
        for k, v in attrs.items():
            self.current._add_xml_attr(_name_mangle(k), v)
            
    def endElement(self, name):
        text = ''.join(self.text_parts).strip()
        if text:
            self.current.data = text
        if self.current._attrs:
            obj = self.current
        else:
            # a text only node is simply represented by the string
            obj = text or ''
        self.current, self.text_parts = self.stack.pop()
        self.current._add_xml_attr(_name_mangle(name), obj)
        
    def characters(self, content):
        self.text_parts.append(content)
            
class GTKWrappers():
    _title_format = '<span weight="bold" size="larger">%s</span>'
    
    def __init__(self):
       self.glade = None
    
    def get_glade(self,glade_file, domain_name):
        """
            Returns a reference for a glade object.
        """
        self.glade =  glade.XML(glade_file, domain_name)
    
    def get_widget(self, widget_name):
        """
            Reeturns a reference for a widget in a glade.
        """
        return self.glade.get_widget(widget_name)
    
    def connect(self,widget, event_name, function_callback, *args):
        """
            Connect widgets signals to callback functions
        """
        return widget.connect(event_name, function_callback, *args)
    
    def process_events(self):
        """
            Proccess all wainting events like drawing window.
        """
        gtk.gdk.flush()
        while gtk.events_pending():
            gtk.main_iteration(False)
    
    def setBusy(self,window_main, flag = False):
        """ Show a watch cursor if the app is busy for more than 0.3 sec.
            Furthermore provide a loop to handle user interface events """
        if window_main.window is None:
            return
        if flag :
            window_main.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        else:
            window_main.window.set_cursor(None)
        #while gtk.events_pending():
        #    gtk.main_iteration()
    
    def scale( self, image, width, height ):
        """
            Resizes an image to make it visible using an aspect ratio.
            @param image
        """
        h,w = image.get_height(), image.get_width()
        width_max, height_max = width, height
        width=float( image.get_width() )
        height=float( image.get_height() )
        if ( width/width_max ) > ( height/height_max ):
            height=int( ( height/width )*width_max )
            width=width_max
        else:
            width=int( ( width/height )*height_max )
            height=height_max

        image = image.scale_simple( width, height, gtk.gdk.INTERP_HYPER )
        gc.collect() # Tell Python to clean up the memory
        return image
    
    def show_question_yesno(self, text, parentWindow=None, title=''):
        dlg = gtk.MessageDialog (parentWindow,
                                 gtk.DIALOG_MODAL,
                                 gtk.MESSAGE_QUESTION,
                                 gtk.BUTTONS_YES_NO)
        # Dialog Title
        title = title and title or _('Question')
        dlg.set_markup(self._title_format % title)
        dlg.format_secondary_markup(text)
        response = dlg.run()
        dlg.destroy()
        return response == gtk.RESPONSE_YES

    def show_error(self, text, parentWindow=None, title=''):
        dlg = gtk.MessageDialog(parentWindow,
                               gtk.DIALOG_MODAL,
                               gtk.MESSAGE_ERROR,
                               gtk.BUTTONS_OK)
        # Dialog Title
        title = title and title or MSG_000025
        dlg.set_markup(self._title_format % title)
        dlg.format_secondary_markup(text)
        dlg.run()
        dlg.destroy()
        return

    def show_error_question(self, text, parentWindow=None, title=''):
        dlg = gtk.MessageDialog(parentWindow,
                               gtk.DIALOG_MODAL,
                               gtk.MESSAGE_ERROR,
                               gtk.BUTTONS_YES_NO)
        # Dialog Title
        title = title and title or _('Error')
        dlg.set_markup(self._title_format % title)
        dlg.format_secondary_markup(text)
        response = dlg.run()
        dlg.destroy()
        return response == gtk.RESPONSE_YES

    def show_info(self, text, parentWindow=None, title=''):
        dlg = gtk.MessageDialog(parentWindow,
                               gtk.DIALOG_MODAL,
                               gtk.MESSAGE_INFO,
                               gtk.BUTTONS_OK)
        # Dialog Title
        title = title and title or _('Information')
        dlg.set_markup(self._title_format % title)
        dlg.format_secondary_markup(text)
        dlg.run()
        dlg.destroy()
        return
    
class ZoomWindow(gtk.Window):
    def __init__(self, parent, image_path = ''):
            gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
            self.image_path = image_path
            self.pixbuf,isdefault = load_pixbuf_image(self.image_path)
            
            self.resizing = False
            self.set_skip_taskbar_hint(True)
            self.set_skip_pager_hint(True)
            self.set_transient_for(parent)
            self.set_size_request(200, 300)
            
            self.eventbox = gtk.EventBox()
            self.image = gtk.Image()
            self.image.set_property('can-focus', True)
            self.eventbox.add(self.image)
            self.add(self.eventbox)
            self.last_allocation = None
            self.eventbox.connect('button-press-event', self.on_clicked)
            self.eventbox.connect('key-press-event', self.on_clicked)
            self.image.connect_after('size-allocate', self.on_size_allocate)
            self.connect('focus-out-event', self.on_focus_out)
            
    def on_focus_out(self, wnd, event):
        self.destroy()
        return False
    
    def on_size_allocate(self, widget, allocation):
        if (self.last_allocation is not None and
            self.last_allocation[0] == allocation.width and
            self.last_allocation[1] == allocation.height): return
        self.last_allocation = allocation.width, allocation.height

        (ww, wh) = self.last_allocation
        pixscaled = self.pixbuf.scale_simple( ww, wh, gtk.gdk.INTERP_BILINEAR )
        self.image.set_from_pixbuf(pixscaled)
        gc.collect()
        
    def on_clicked(self, widget, *args):
        self.destroy()
        return False

    def run(self):
        self.show_all()
        self.fullscreen()
        return True
    
def xmlescape(s):
    from xml.sax.saxutils import escape
    if s==None:
        return ""
    else:
        return escape(s)

def force_string(dic):
    """ Force string type """
    if not isinstance(dic, dict):
        return dic
    ret = {}
    for i in range(len(dic)):
        key = dic.keys()[i]
        value = dic.values()[i]
        if not isinstance(key, basestring):
            key = str(key)
        if not isinstance(value, basestring):
            value = str(value)
        ret[key] = value
    return ret

def str_to_date(strdate):
    dt = strdate.split()[0]
    sep = [c for c in dt if not c.isdigit()][0]
    dtPieces = [int(p) for p in dt.split(sep)]
    return datetime.date(dtPieces[0], dtPieces[1], dtPieces[2])

def iterate_list_store(store, it):
    """ iterate over a gtk tree-model, returns a gtk.TreeIter for each element
    """
    if not it:
        raise StopIteration
    yield it
    while True:
        it = store.iter_next(it)
        if it == None:
            raise StopIteration
        yield it

def url_open(url):
    try:
        webbrowser.open(url)
    except:
        GTKWrappers().show_error(MSG_000024,title=MSG_000025)
