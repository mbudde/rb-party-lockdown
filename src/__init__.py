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

import rhythmdb, rb
import gobject, gtk

from Preferences import Preferences
from Dialogs import PreferenceDialog, UnlockDialog

ui_lock_toggle = """
<ui>
  <menubar name="MenuBar">
    <menu name="ViewMenu" action="View">
      <placeholder name="ViewMenuModePlaceholder">
        <menuitem name="LockPartyModeToggle" action="ToggleLockPartyMode"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""


class PartyLockdown(rb.Plugin):
    def __init__(self):
        rb.Plugin.__init__(self)

    def activate(self, shell):
        self.shell = shell
        self.prefs = Preferences()
        uim = shell.get_ui_manager()

        self.lock_toggle = LockToggle(self)

        # Connect callbacks
        self.party_mode_toggle = uim.get_widget('/MenuBar/ViewMenu/ViewPartyModeMenu')
        self.pmt_conn_id = self.party_mode_toggle.connect('toggled',  self.party_mode_toggled)

    def deactivate(self, shell):
        self.party_mode_toggle.disconnect(self.pmt_conn_id)
        self.lock_toggle = None

    def party_mode_toggled(self, widget):
        "Enable menu item when party mode is enabled."
        
        if widget.get_active():
            self.lock_toggle.action.set_sensitive(True)
        else:
            self.lock_toggle.action.set_sensitive(False)

    def create_configure_dialog(self, dialog=None):
        if not dialog:
            dialog = PreferenceDialog(self).get_dialog()

        dialog.present()

        return dialog


class LockToggle(object):
    def __init__(self, plugin):
        self.plugin = plugin
        self.uim = plugin.shell.get_ui_manager()

        self.plugin.prefs.on_update(self.prefs_updated)

        # Setup locking action
        self.action = gtk.ToggleAction('ToggleLockPartyMode', 'Lock Party Mode',
                                       'Password protect party mode', None)
        self.action.connect('toggled', self.lock_toggled)
        self.action_group = gtk.ActionGroup('LockPartyModePluginActions')
        self.action_group.add_action_with_accel(self.action, 'F12')
        self.uim.insert_action_group(self.action_group, 0)

        # FIXME: we could be starting in party mode
        self.action.set_sensitive(False)
        self.is_locked = False

        # Setup UI
        self.ui_toggle = self.uim.add_ui_from_string(ui_lock_toggle)
        self.uim.ensure_update()

        self.unlock_dialog = UnlockDialog(self.plugin, self.unlock_callback)

        self.prefs_updated()

    def __del__(self):
        self.uim.remove_ui(self.ui_toggle)
        self.uim.remove_action_group(self.action_group)

        self.action_group = None
        self.action = None

        self.uim.ensure_update()

    def prefs_updated(self):
        # FIXME: This function is ugly and useless
        # Widgets to be disabled when locking down
        widgets_disable_paths = ['/MenuBar/MusicMenu/MusicImportFileMenu',
                                 '/MenuBar/MusicMenu/MusicImportFolderMenu',
                                 '/MenuBar/MusicMenu/MusicPropertiesMenu',
                                 '/MenuBar/ViewMenu/ViewPartyModeMenu',
                                 '/MenuBar/EditMenu/EditPluginsMenu',
                                 '/MenuBar/EditMenu/EditPreferencesMenu',
                                 '/MenuBar/HelpMenu']
        self.widgets_disable = list([self.uim.get_widget(path) for 
                                     path in widgets_disable_paths])

        # Widgets to be hidden when locking down
        widgets_hide_paths = []
        if self.plugin.prefs.get_hide_menu_bar():
            widgets_hide_paths.append('/MenuBar')
        self.widgets_hide = list([self.uim.get_widget(path) for
                                  path in widgets_hide_paths])

    def lock_toggled(self, widget):
        "Lock/unlock party mode"

        if widget.get_active():
            assert self.is_locked == False, 'trying to lock but we are already locked'
            self.is_locked = True
            self.disable_widgets()
        else:
            assert self.is_locked == True, 'trying to unlock but we are already unlocked'
            self.unlock_dialog.get_dialog().present()
            self.is_locked = False

    def unlock_callback(self, success):
        if success:
            self.enable_widgets()
        if not success:
            self.action.set_active(True)

    def enable_widgets(self):
        self.disable_widgets(False)
        
    def disable_widgets(self, disable=True):
        for widget in self.widgets_disable:
            widget.set_sensitive(not disable)
            action = widget.get_action()
            if action != None:
                action.set_sensitive(not disable)

        for widget in self.widgets_hide:
            if not disable:
                widget.show()
            else:
                widget.hide()

