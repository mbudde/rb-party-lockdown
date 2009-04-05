#
# Party Lockdown
# Copyright (C) 2009 Michael Budde <mbudde@gmail.com>
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

class WidgetLocker(object):
    def __init__(self, uim, widget_path):
        self.widget = uim.get_widget(widget_path)

class DisableWidgetLocker(WidgetLocker):
    def _disable(self, disabling):
        self.widget.set_sensitive(not disabling)
        action = self.widget.get_action()
        if action != None:
            action.set_sensitive(not disabling)

    def lock(self):
        self._disable(True)

    def unlock(self):
        self._disable(False)

class HideWidgetLocker(WidgetLocker):
    def _hide(self, hiding):
        hiding and self.widget.hide() or self.widget.show()

    def lock(self):
        self._hide(True)

    def unlock(self):
        self._hide(False)

class HideWidgetLockerWithPref(HideWidgetLocker):
    def __init__(self, uim, widget_path, pref, value=True):
        super(HideWidgetLockerWithPref, self).__init__(uim, widget_path)
        self.pref = pref
        self.lock_val = value

    def lock(self):
        if self.pref.get() == self.lock_val:
            self._hide(True)


class LockerManager(object):
    
    def __init__(self, uim):
        self.lockers = []
        self.uim = uim

    def shutdown(self):
        for locker in self.lockers:
            del locker

    def add_lock(self, path, type, pref=None, lock_value=None):
        if type == 'disable':
            self.lockers.append(DisableWidgetLocker(self.uim, path))
        if type == 'hide':
            self.lockers.append(HideWidgetLocker(self.uim, path))
        if type == 'hide_with_pref':
            if not pref == None:
                if lock_value == None:
                    self.lockers.append(HideWidgetLockerWithPref(self.uim, path, pref))
                else:
                    self.lockers.append(HideWidgetLockerWithPref(self.uim, path, pref,
                                                                 lock_value))

    def lock_all(self):
        for locker in self.lockers:
            locker.lock()

    def unlock_all(self):
        for locker in self.lockers:
            locker.unlock()


class PartyModeLock(object):
    """Class responsible for locking and unlocking Party Mode."""

    def __init__(self, plugin):
        self.plugin = plugin
        self.plugin.prefs.on_update(self.prefs_updated)
        self._is_locked = False

        self.lockers = LockerManager(plugin.shell.get_ui_manager())
        self.lockers.add_lock(
            '/MenuBar/MusicMenu/MusicImportFileMenu', 'disable'
        )
        self.lockers.add_lock(
            '/MenuBar/MusicMenu/MusicImportFolderMenu', 'disable'
        )
        self.lockers.add_lock(
            '/MenuBar/MusicMenu/MusicPropertiesMenu', 'disable'
        )
        self.lockers.add_lock(
            '/MenuBar/ViewMenu/ViewPartyModeMenu', 'disable'
        )
        self.lockers.add_lock(
            '/MenuBar/EditMenu/EditPluginsMenu', 'disable'
        )
        self.lockers.add_lock(
            '/MenuBar/EditMenu/EditPreferencesMenu', 'disable'
        )
        self.lockers.add_lock(
            '/MenuBar/HelpMenu', 'disable'
        )
        self.lockers.add_lock(
            '/MenuBar', 'hide_with_pref', plugin.prefs['hide_menu_bar']
        )

        self.unlock_dialog = UnlockDialog(plugin, self.unlock_callback)

    def shutdown(self):
        self.lockers.shutdown()
        self.unlock_dialog.shutdown()
        del self.lockers
        del self.unlock_dialog
        del self.plugin

    def lock(self):
        if self._is_locked == False:
            self.lockers.lock_all()
            self._is_locked = True

    def unlock(self, callback):
        if self._is_locked == True:
            self.unlock_dialog.get_dialog().present()
            self.on_unlock_cb = callback

    def unlock_callback(self, success):
        if success:
            self.lockers.unlock_all()
            self._is_locked = False
        if self.on_unlock_cb:
            self.on_unlock_cb(success)
        self.on_unlock_cb = None

    def prefs_updated(self, key, val):
        pass
        

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
            if self.password.get_text() == self.plugin.prefs.get('password'):
                success = True

        self.password.set_text('')
        dialog.hide()
        self.callback(success)

    def shutdown(self):
        del self.plugin
        del self.gladexml
        del self.dialog
        del self.password

    def get_dialog(self):
        return self.dialog
