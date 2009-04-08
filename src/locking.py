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
    types = [
        'hide',
        'hide_with_cond',
        'disable',
        'disable_with_cond'
    ]

    def __init__(self, uim, widget_path, type, *kw):
        if type not in self.types:
            raise ValueError, 'type %s is not implemented'
        self.widget = uim.get_widget(widget_path)
        if type in 'hide disable':
            self._lock_func = self._get_lock_func(type)
        elif type in 'hide_with_cond disable_with_cond':
            cond_func = kw[0]
            lock_func = self._get_lock_func(type)
            def lock_with_cond(hiding):
                if hiding and cond_func():
                    lock_func(True)
                elif not hiding:
                    lock_func(False)
            self._lock_func = lock_with_cond

    def _get_lock_func(self, type):
        if 'hide' in type:
            return self._hide
        elif 'disable' in type:
            return self._disable

    def lock(self):
        self._lock_func(True)

    def unlock(self):
        self._lock_func(False)

    def _hide(self, hiding):
        if hiding:
            self.widget.hide()
        else:
            self.widget.show()

    def _disable(self, disabling):
        self.widget.set_sensitive(not disabling)
        action = self.widget.get_action()
        if action != None:
            action.set_sensitive(not disabling)
    

class LockerManager(object):
    
    def __init__(self, uim, locks=[]):
        self.lockers = []
        self.uim = uim
        for lock in locks:
            if len(lock) == 3:
                paths, type_, func = lock
            else:
                paths, type_ = lock
                func = None
            if type(paths) is list:
                for path in paths:
                    self.lockers.append(WidgetLocker(uim, path, type_, func))
            else:
                self.lockers.append(WidgetLocker(uim, paths, type_, func))

    def shutdown(self):
        for locker in self.lockers:
            del locker

    def add_lock(self, path, type, *kw):
        self.lockers.append(WidgetLocker(self.uim, path, type, kw))

    def lock_all(self):
        for locker in self.lockers:
            locker.lock()

    def unlock_all(self):
        for locker in self.lockers:
            locker.unlock()


class PartyModeLock(object):
    """Class responsible for locking and unlocking Party Mode."""

    def __init__(self, prefs, uim, unlock_glade):
        self.prefs = prefs
        #self.plugin.prefs.on_update(self.prefs_updated)
        self._is_locked = False

        locks = [	
            (['/MenuBar/MusicMenu/MusicImportFileMenu',
              '/MenuBar/MusicMenu/MusicImportFileMenu',
              '/MenuBar/MusicMenu/MusicPropertiesMenu',
              '/MenuBar/ViewMenu/ViewPartyModeMenu',
              '/MenuBar/EditMenu/EditPluginsMenu',
              '/MenuBar/EditMenu/EditPreferencesMenu',
              '/MenuBar/HelpMenu'], 'disable'),
            (['/MenuBar'], 'hide_with_cond',
             lambda: prefs['hide_menu_bar'])
        ]
        self.lockers = LockerManager(uim, locks)

        self.unlock_dialog = UnlockDialog(prefs, unlock_glade, self.unlock_callback)

    def shutdown(self):
        self.lockers.shutdown()
        self.unlock_dialog.shutdown()
        del self.lockers
        del self.unlock_dialog

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
    def __init__(self, prefs, glade_file, callback):
        self.prefs = prefs
        self.callback = callback
        gladexml = gtk.glade.XML(glade_file)
        
        self.dialog = gladexml.get_widget("unlock_dialog")
        self.password = gladexml.get_widget("password")

        self.dialog.connect("response", self.dialog_response)

    def dialog_response(self, dialog, response):
        success = False
        if response == 2:
            if self.password.get_text() == self.prefs['password']:
                success = True

        self.password.set_text('')
        dialog.hide()
        self.callback(success)

    def shutdown(self):
        del self.prefs
        del self.dialog
        del self.password

    def get_dialog(self):
        return self.dialog
