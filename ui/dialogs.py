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

from os import path

import gtk
import pango

class IUGHeading(gtk.DrawingArea):

    BORDER = 6
    SPACING = 12
    ICON_SIZE = 48

    def __init__(self, title):
        gtk.Widget.__init__(self)

        self.title = title
        self.subTitle = None
        self.icon = None
        self.iconName = None

        self.connect("realize", self._realize)
        self.connect("size-request", self._size_request)
        self.connect("expose_event", self._expose)
        self.connect("style-set", self._style_set)

    def _realize(self, widget):
        self.realize()

        # Allocate the widget window
        self.window = gtk.gdk.Window(self.get_parent_window(),
                self.get_allocation().width,
                self.get_allocation().height,
                gtk.gdk.WINDOW_CHILD,
                self.get_events() | gtk.gdk.EXPOSURE_MASK,
                gtk.gdk.INPUT_OUTPUT,
                "",
                self.get_allocation().x,
                self.get_allocation().y,
                self.get_visual(),
                self.get_colormap())
        self.window.set_user_data(self)

        # Connect the style to the window
        self.get_style().attach(self.window)

        # Set background color
        self.window.set_background(self.get_style().base[gtk.STATE_NORMAL])

    def _size_request(self, widget, requisition):
        pixbufWidth = 0
        pixbufHeight = 0

        # Determine dimensions of the title text
        layout = self.make_layout()
        width, height = layout.get_pixel_size()

        # Determine dimensions of the pixbuf
        pixbuf = self.make_pixbuf()
        if pixbuf:
            pixbufWidth = pixbuf.get_width()
            pixbufHeight = pixbuf.get_height()

        # Determine base dimensions
        requisition.width = width + pixbufWidth + (0, self.SPACING)[pixbufWidth > 0]
        requisition.height = max(self.ICON_SIZE, max(pixbufHeight, height))

        # Add border
        requisition.width += 2 * self.BORDER
        requisition.height += 2 * self.BORDER

    def _expose(self, widget, event):
        # Determine whether we're using LTR or RTL
        rtl = self.get_direction() == gtk.TEXT_DIR_RTL

        # Determine initial horizontal position
        if rtl:
            x = self.get_allocation().width - self.BORDER
        else:
            x = self.BORDER

        # Check if we have a pixbuf to render
        pixbuf = self.make_pixbuf()

        if pixbuf:
            # Determine pixbuf dimensions
            width = pixbuf.get_width()
            height = pixbuf.get_height()

            # Determine vertical position
            y = (self.get_allocation().height - height) / 2

            # Determine horizontal position for the pixbuf
            # pixbufX =

            # Render the pixbuf
            self.window.draw_pixbuf(self.get_style().black_gc, pixbuf, 0, 0,
                    (x, x - width)[rtl], y, width, height,
                    gtk.gdk.RGB_DITHER_NORMAL, 0, 0)

            # Update the horizontal position
            x += (1, -1)[rtl] * (width + self.SPACING)

        # Generate the title layout
        layout = self.make_layout()
        width, height = layout.get_pixel_size()

        # Determine vertical position
        y = (self.get_allocation().height - height) / 2

        # Render the title
        self.get_style().paint_layout(self.window, self.state, True,
                event.area, self, "heading", (x, x - width)[rtl], y, layout)

        return False

    def _style_set(self, widget, oldStyle):
        if self.window:
            self.window.set_background(self.get_style().base[gtk.STATE_NORMAL])

    def make_pixbuf(self):
        pixbuf = None

        if self.icon:
            pixbuf = self.icon
        elif self.iconName:
            # Determine icon theme for the current screen
            screen = self.get_screen()
            theme = gtk.icon_theme_get_for_screen(screen)

            # Load pixbuf
            pixbuf = theme.load_icon(self.iconName, self.ICON_SIZE,
                    gtk.ICON_LOOKUP_USE_BUILTIN)

        return pixbuf

    def make_layout(self):
        titleLength = 0
        text = str()

        # Add main title
        if self.title:
            titleLength = len(self.title)
            text += self.title

        # Add subtitle, if any
        if self.subTitle:
            # Add empty line between title and subtitle
            if self.title:
                text += "\n"

            text += self.subTitle

        # Allocate and setup a new layout from the widget's context
        layout = pango.Layout(self.get_pango_context())
        layout.set_text(text)

        # Allocate an attribute list (large bold title)
        attrs = pango.AttrList()
        attribute = pango.AttrScale(pango.SCALE_LARGE, 0, titleLength)
        attrs.insert(attribute)
        attribute = pango.AttrWeight(pango.WEIGHT_BOLD, 0, titleLength)
        attrs.insert(attribute)
        layout.set_attributes(attrs)

        return layout

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title
        self.queue_draw()

    def get_subtitle(self):
        return self.subTitle

    def set_subtitle(self, title):
        self.subTitle = title
        self.queue_draw()

    def get_icon_name(self):
        return self.iconName

    def set_icon_name(self, name):
        self.iconName = name
        self.queue_draw()

    def get_icon(self):
        return self.icon

    def set_icon(self, pixbuf):
        self.icon = pixbuf
        self.queue_draw()


class IUGTitledDialog(gtk.Dialog):

    def __init__(self, title=None, parent=None, flags=0, buttons=None):
        gtk.Dialog.__init__(self, title, parent, flags, buttons)

        # Reset subtitle
        self.subtitle = None

        # Remove the main container
        #self.remove(self.vbox)

        # Add new vbox without border
        #vbox = gtk.VBox(False, 0)
        #self.add(vbox)
        #vbox.show()

        # Add the heading
        self.heading = IUGHeading(title)
        self.vbox.pack_start(self.heading, False, False, 0)
        self.heading.show()

        # Add the separator
        separator = gtk.HSeparator()
        self.vbox.pack_start(separator, False, False, 0)
        separator.show()

        # Re-add the the main dialog box again
        #vbox.pack_start(self.vbox, True, True, 0)

        self.connect("notify::icon", lambda *args: self._update_heading())
        self.connect("notify::icon-name", lambda *args: self._update_heading())
        self.connect("notify::title", lambda *args: self._update_heading())

        self._update_heading()

    def _update_heading(self):
        self.heading.set_icon(self.get_icon())
        self.heading.set_icon_name(self.get_icon_name())
        self.heading.set_title(self.get_title())

    def get_subtitle(self):
        return self.subTitle

    def set_subtitle(self, title):
        self.subTitle = title
        self.heading.set_subtitle(title)


def showMessage(parent, msg, type, buttons=gtk.BUTTONS_OK):
   dialog = gtk.MessageDialog(parent, \
           gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, \
           type, buttons, msg)
   retval = dialog.run()
   dialog.destroy()
   return retval

def forceRefresh():
    while gtk.events_pending():
        gtk.main_iteration(False)

