#
# Party Lockdown
# Copyright (C) 2008, 2009 Michael Budde <mbudde@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import gtk
import gtk.glade
import gconf
import os

class Preference(object):
    def __init__(self, path, default):
        self.gconf = gconf.client_get_default()
        self.path = path
        self.default = default

    def get(self):
        try:
            return self.gconf.get_value(self.path)
        except ValueError:
            self.set(self.default)
            return self.default

    def set(self, val):
        self.gconf.set_value(self.path, val)

    def shutdown(self):
        del self.gconf


class PreferenceManager(object):

    def __init__(self, dir):
        self.prefs_dir = dir
        self.prefs = {}
        self._callbacks = []

    def shutdown(self):
        for key in self.prefs:
            self.prefs[key].shutdown()

    def __getitem__(self, key):
        return self.prefs[key]

    def add_pref(self, key, default):
        path = '%s/%s' % (self.prefs_dir, key)
        if key not in self.prefs:
            self.prefs[key] = Preference(path, default)

    def get(self, key):
        return self.prefs[key].get()

    def set(self, key, value):
        self.prefs[key].set(value)
        for cb in self._callbacks:
            cb(key, value)

    def on_update(self, cb):
        if not cb in self._callbacks:
            self._callbacks.append(cb)


class PartyLockdownPrefs(PreferenceManager):
    plugin_gconf_dir = '/apps/rhythmbox/plugins/party-lockdown'

    def __init__(self, prefs_glade_path):
        super(PartyLockdownPrefs, self).__init__(self.plugin_gconf_dir)

        self.add_pref('password', '')
        self.add_pref('hide_menu_bar', False)

        self.dialog = PartyLockdownPrefsDialog(self, prefs_glade_path)

    def shutdown(self):
        super(PartyLockdownPrefs, self).shutdown()


class PartyLockdownPrefsDialog(object):

    def __init__(self, prefs, prefs_glade_path):
        self.prefs = prefs
        gladexml = gtk.glade.XML(prefs_glade_path)
        
        self._dialog = gladexml.get_widget('preferences_dialog')
        self._password = gladexml.get_widget('password')
        self._password.set_text(self.prefs.get('password'))
        self._hide_menu_bar = gladexml.get_widget('hide_menu_bar')
        self._hide_menu_bar.set_active(self.prefs.get('hide_menu_bar'))

        self._dialog.connect('response', self.dialog_response)

    def shutdown(self):
        del self.prefs
        del self._dialog

    def dialog_response(self, dialog, response):
        self.prefs.set('password', self._password.get_text())
        self.prefs.set('hide_menu_bar', self._hide_menu_bar.get_active())
        dialog.hide()

    def get_dialog(self):
        return self._dialog
