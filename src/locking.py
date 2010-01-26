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
import rb


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
        if hiding: self.widget.hide()
        else: self.widget.show()
        action = self.widget.get_action()
        if action != None:
            action.set_sensitive(not hiding)

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

    def __init__(self, prefs, shell, uim, unlock_ui):
        self.prefs = prefs
        #self.plugin.prefs.on_update(self.prefs_updated)
        self._is_locked = False

        locks = [
            (['/MenuBar/MusicMenu',
              '/MenuBar/ViewMenu/ViewPartyModeMenu',
              '/MenuBar/EditMenu/EditPluginsMenu',
              '/MenuBar/EditMenu/EditPreferencesMenu',
              '/MenuBar/HelpMenu'], 'disable'),
            (['/MenuBar'], 'hide_with_cond',
             lambda: prefs['hide_menu_bar']),
            (['/MenuBar/ControlMenu/ControlPreviousMenu',
              '/MenuBar/ControlMenu/ControlNextMenu',
              '/ToolBar/Previous',
              '/ToolBar/Next'],
             'hide_with_cond',
             lambda: prefs['hide_next_prev'])
        ]
        self.lockers = LockerManager(uim, locks)

        self.unlock_bar = UnlockBar(prefs, shell, unlock_ui, self.unlock_callback)

    def shutdown(self):
        self.lockers.shutdown()
        self.unlock_bar.shutdown()
        del self.lockers
        del self.unlock_bar

    def lock(self):
        if self._is_locked == False:
            self.lockers.lock_all()
            self._is_locked = True

    def unlock(self, callback):
        if self._is_locked == True:
            self.unlock_bar.present()
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


class UnlockBar(object):
    def __init__(self, prefs, shell, ui_file, callback):
        self.prefs = prefs
        self.shell = shell
        self.callback = callback
        builder = gtk.Builder()
        builder.add_from_file(ui_file)

        self.bar = builder.get_object("unlock_bar")
        self.password = builder.get_object("password")

        builder.get_object('cancel').connect("clicked", self.cancel)
        unlock = builder.get_object('unlock')
        unlock.connect("clicked", self.unlock)
        def activate_unlock(widget):
            unlock.clicked()
        self.password.connect('activate', activate_unlock)

    def unlock(self, widget):
        success = False
        if self.password.get_text() == self.prefs['password']:
            success = True

        self.password.set_text('')
        self.hide()
        self.callback(success)

    def cancel(self, widget):
        self.hide()
        self.callback(False)

    def shutdown(self):
        del self.prefs
        del self.shell
        del self.bar
        del self.password

    def present(self):
        self.shell.add_widget(self.bar, rb.SHELL_UI_LOCATION_MAIN_TOP)
        self.password.grab_focus()

    def hide(self):
        self.shell.remove_widget(self.bar, rb.SHELL_UI_LOCATION_MAIN_TOP)
