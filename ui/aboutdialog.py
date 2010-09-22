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

import gtk
from lib.constants import *
from lib.utils import load_pixbuf_image

class AboutDialog(gtk.AboutDialog):
	def __init__(self):
		gtk.AboutDialog.__init__(self)
		self.set_name("IUG")
		self.set_logo(load_pixbuf_image('temp.jpg')[0])
		self.set_version("1.0")
		self.set_website("http://www.ubuntugames.org")
		self.set_comments(MSG_000022)
		self.set_artists(['Carlos Donizete "Coringao" <coringao@ubuntu.com>'])
		self.set_authors(['Laudeci Oliveira <laudeci@ubuntu.com>', 'Thiago Avelino <thiagoavelinoster@gmail.com>', 'Carlos Donizete <coringao@ubuntu.com>'])
		self.set_copyright("Copyright (C) 2009 Carlos Donizete <coringao@ubuntu.com>")
		self.set_license(MSG_000023)
		self.run()
		self.destroy()
