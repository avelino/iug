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

from datetime import datetime
from datetime import timedelta
from lib.actions import Actions
from lib.utils import str_to_date

class IUGVersionChecker():
    
    def __init__(self):
        self.initial_date = str_to_date((datetime.now()- timedelta(10)).strftime('%Y-%m-%d'))
    
    def check_version(self, actions):
        records = actions.get_iugversion()
        if len(records) > 0 :
            dbdate = str_to_date(records[0]['version_date'])
        else:
            actions.add_iugversion({'version':'1.0', 'version_date':(datetime.now()- timedelta(10)).strftime('%Y-%m-%d')})
            dbdate = self.initial_date
        
        current = datetime.date(datetime.now())
        
        if (current - dbdate).days > 5:
            return False
        else:
            return True
