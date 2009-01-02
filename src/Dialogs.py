# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2009 Michael Budde <mbudde@gmail.com>
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

import gobject, gtk

class PreferenceDialog(object):
    def __init__(self, plugin):
        self.plugin = plugin
        glade_file = self.plugin.find_file('party-lockdown-prefs.glade')
        self.gladexml = gtk.glade.XML(glade_file)
        
        self.dialog = self.gladexml.get_widget('preferences_dialog')
        self.password = self.gladexml.get_widget('password')
        self.hide_menu_bar = self.gladexml.get_widget('hide_menu_bar')

        self.dialog.connect("response", self.dialog_response)

        self.password.set_text(self.plugin.prefs.get_password())
        self.hide_menu_bar.set_active(self.plugin.prefs.get_hide_menu_bar())

    def dialog_response(self, dialog, response):
        self.plugin.prefs.set_password(self.password.get_text())
        self.plugin.prefs.set_hide_menu_bar(self.hide_menu_bar.get_active())
        dialog.hide()

    def get_dialog(self):
        return self.dialog


class UnlockDialog(object):
    def __init__(self, plugin, callback):
        self.plugin = plugin
        self.callback = callback
        glade_file = self.plugin.find_file('party-lockdown-unlock.glade')
        self.gladexml = gtk.glade.XML(glade_file)
        
        self.dialog = self.gladexml.get_widget("unlock_dialog")
        self.password = self.gladexml.get_widget("password")

        self.dialog.connect("response", self.dialog_response)

    def dialog_response(self, dialog, response):
        success = False
        if response == 2:
            if self.password.get_text() == self.plugin.prefs.get_password():
                success = True

        self.password.set_text('')
        dialog.hide()
        self.callback(success)

    def get_dialog(self):
        return self.dialog
