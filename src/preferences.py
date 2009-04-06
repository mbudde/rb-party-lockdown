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

import os
import gtk
import gtk.glade
import gconf


class GConfPreferences(object):
    """Convenience class taking care of getting and setting
    GConf keys.
    """

    defaults = {}

    def __init__(self, gconf_dir, defaults={}):
        """Init class. defaults should be a dict containing
        key-value pairs of default preferences.
        """
        self.defaults.update(defaults)
        self.gconf_dir = gconf_dir
        self._gconf = gconf.client_get_default()

    def get_path(self, key):
        if '/' in key:
            raise ValueError, "key must not contain '/'"
        if self.gconf_dir[-1] == '/':
            return self.gconf_dir + key
        else:
            return '/'.join([self.gconf_dir, key])
        
    def __getitem__(self, key):
        """Get preference. If a GConf key does not exist
        create it with the value from defaults and return
        this value. If a default value does not exist raise 
        ValueError.
        """
        try:
            return self._gconf.get_value(self.get_path(key))
        except ValueError, msg:
            if key in self.defaults:
                self.__setitem__(key, self.defaults[key])
                return self.defaults[key]
            else:
                raise ValueError, msg

    def __setitem__(self, key, val):
        """Set GConf key."""
        self._gconf.set_value(self.get_path(key), val)

    def __delitem__(self, key):
        """Unset GConf key."""
        self._gconf.unset(self.get_path(key))

    def __contains__(self, key):
        """Return true if the GConf key exists, otherwise
        return false.
        """
        try:
            self.__getitem__(key)
            return True
        except ValueError:
            return False

    def watch(self, key, cb):
        """Call the callback function 'cb', passing a string
        containing the key name, when the GConf key is changed.
        """
        if not self.__contains__(key):
            raise ValueError, 'key %s does not exist' % self.get_path(key)
        id = self._gconf.notify_add(self.get_path(key), cb, key)
        return id

    def unwatch(self, id):
        self._gconf.notify_remove(id)


class PreferenceWrapper(object):
    """A wrapper class that takes care of keeping GConf preferences
    and widgets in sync.
    """
    
    def __init__(self, prefs):
        self.prefs = prefs

    def wrap(self, key, widget, get_method, set_method, signal):
        set_method(widget, self.prefs[key])
        def update_pref(widget):
            self.prefs[key] = get_method(widget)
        widget.connect(signal, update_pref)

    def wrap_toggle(self, key, widget):
        self.wrap(key, widget,
                  get_method=lambda w: w.get_active(),
                  set_method=lambda w, v: w.set_active(v),
                  signal='toggled')

    def wrap_textinput(self, key, widget):
        self.wrap(key, widget,
                  get_method=lambda w: w.get_text(),
                  set_method=lambda w, v: w.set_text(v),
                  signal='changed')


class PreferenceDialog(PreferenceWrapper):

    def __init__(self, prefs, prefs_glade_path):
        PreferenceWrapper.__init__(self, prefs)
        gladexml = gtk.glade.XML(prefs_glade_path)
        
        self._dialog = gladexml.get_widget('preferences_dialog')

        password = gladexml.get_widget('password')
        hide_menu_bar = gladexml.get_widget('hide_menu_bar')
        self.wrap_textinput('password', password)
        self.wrap_toggle('hide_menu_bar', hide_menu_bar)

        self._dialog.connect('response', lambda d, r: self._dialog.hide())

    def get_dialog(self):
        return self._dialog
