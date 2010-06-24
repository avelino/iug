# -*- coding: utf-8 -*-
#
#  Laudeci Oliveira <laudeci@gmail.com>
#
#  Copyright 2008 UbuntuGames DevTeam.
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
import locale
import gettext
from gettext import gettext as _

APP_VERSION = '0.1.00-0'
APP_ICON_NAME = 'iug'
APP_NAME = 'iug'
I18N_DIR = "/usr/share/locale/"

def get_path(default,  destination):

    if not os.path.exists(destination):
        return os.path.abspath(default)
    else:
        return os.path.abspath(destination)
    
# ---- i18n ----
locale.setlocale(locale.LC_ALL, "")
gettext.bindtextdomain(APP_NAME, I18N_DIR)
gettext.textdomain(APP_NAME)

gtk.glade.bindtextdomain(APP_NAME, I18N_DIR)
gtk.glade.textdomain(APP_NAME)
gettext.install(APP_NAME, I18N_DIR, unicode=1)

language = locale.setlocale(locale.LC_ALL, '')
end = language.find('.')
language = language[:end]

#enumeration constants
(COL_CAT_NAME, COL_CAT_ITEM) = range(0,2)

# Columns of the game store
(COL_NAME, COL_ITEM, COL_POPCON) = range(3)

#Folder for configurarion file
if not os.path.exists(os.path.expanduser('~/.iug/')):
    CONFIG_DIR  = os.makedirs(os.path.expanduser('~/.iug/'))

CONFIG_DIR  = os.path.expanduser('~/.iug/')
#configuration file name
CONFIG_FILE  = os.path.join(CONFIG_DIR, 'iug.config')
#Local base path, where iug is located (runtime)
BASE_PATH = os.path.abspath(os.curdir)

MAIN_GLADE = get_path('/usr/share/iug/data/glade/iug.glade',  os.path.join(BASE_PATH ,'data/glade/iug.glade'))

#application strings
MSG_000001 = _('Category')
MSG_000002 = _('<b><big>The list of available games is out of date.</big></b>\n\nTo reload the list you need a working internet connection. \
                    \n If you want to stay with your old list, click close button.')
MSG_000003 = _('Downloading files')
MSG_000004 = _('Establishing connection...')
MSG_000005 = _('Could not download %s.')
MSG_000006 = _('Downloading %s')
MSG_000007 = 'Total: %(percent)d%% [%(bytes)d/%(total)d kB]'
MSG_000008 = '%(name)s: %(percent)d%% [%(bytes)d/%(total)d kB]'
MSG_000009 = _('Enjoyable')
MSG_000010 = _('Game')
MSG_000011 = _('IUG games version')
MSG_000012 = _('IUG games list')
MSG_000013 = _('Name')
MSG_000014 = _('Description')
MSG_000015 = _('System Requeriments')
MSG_000016 = _('Size')
MSG_000017 = _('Website')
MSG_000018 = _('Version')
MSG_000019 = ("<b>Retrieving:</b>")
MSG_000020 = _('Stars')
MSG_000021 = '<b>%s</b>\n<small>%s\n<b>'+ MSG_000016 +':</b>%s\t<b>'+ MSG_000018 +':</b>%s</small>'
MSG_000022 = _('Ubuntu Games Installer is a easy and fast away to get games in your Ubuntu')
MSG_000023 = _('''Ubuntu Games Installer is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.\n
Ubuntu Games Installer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.\n
You should have received a copy of the GNU General Public License
along with Hotwire; if not, write to the Free Software Foundation, Inc.,
51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA''')
MSG_000024 = _('Could not find the default browser.')
MSG_000025 = _('Error')
MSG_000026 = _('All')
