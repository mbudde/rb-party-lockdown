# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 Michael Budde <mbudde@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

# Base on ConfgiureDialog.py from Rhythmbox plugin 'jump-to-playing'
#     http://www.stevenbrown.ca/blog/archives/254
#     Copyright (C) 2007,2008 Steven Brown

import gobject, gtk, gtk.glade
import gconf
from os import system, path

class Preferences(object):
    def __init__(self):
        self.gconf = gconf.client_get_default()
        self.gconf_keys = {'password': '/apps/rhythmbox/plugins/party-lockdown/password',
                           'hide_menu_bar': '/apps/rhythmbox/plugins/party-lockdown/hide_menu_bar'}

        if self.get_password() is None:
            self.set_password('')

        if self.get_hide_menu_bar is None:
            self.set_hide_menu_bar(True)

        self.callback = None
    
    def set_password(self, val):
        self.gconf.set_string(self.gconf_keys['password'], val)
        self._notify_callback()

    def get_password(self):
        return self.gconf.get_string(self.gconf_keys['password'])

    def set_hide_menu_bar(self, val):
        self.gconf.set_bool(self.gconf_keys['hide_menu_bar'], val)
        self._notify_callback()

    def get_hide_menu_bar(self):
        return self.gconf.get_bool(self.gconf_keys['hide_menu_bar'])

    def on_update(self, callback):
        self.callback = callback

    def _notify_callback(self):
        if self.callback != None:
            self.callback()


