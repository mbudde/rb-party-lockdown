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

import rb
import rhythmdb

from locking import PartyModeLock
from preferences import PartyLockdownPrefs

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
        super(PartyLockdown, self).__init__()

    def activate(self, shell):
        """Activate plugin."""
        self.shell = shell
        glade_path = self.find_file('party-lockdown-prefs.glade')
        self.prefs = PartyLockdownPrefs(glade_path)
        self.party_mode_lock = PartyModeLock(self)

        uim = shell.get_ui_manager()

        # Connect callback for Party Mode toggle
        self.party_mode_toggle = uim.get_widget('/MenuBar/ViewMenu'\
                                           '/ViewPartyModeMenu')
        self.pmt_conn_id = self.party_mode_toggle.connect('toggled',
                                            self.party_mode_toggled)

        # Set up action for Party Mode lock
        self.lock_toggle = gtk.ToggleAction('ToggleLockPartyMode',
                                            'Lock Party Mode',
                                            'Password protect party mode',
                                            None)
        self.action_conn_id = self.lock_toggle.connect('toggled',
                                                       self.lock_toggled)
        self.action_group = gtk.ActionGroup('LockPartyModePluginActions')
        self.action_group.add_action_with_accel(self.lock_toggle, 'F12')
        uim.insert_action_group(self.action_group, 0)

        if not self.party_mode_toggle.get_active():
            self.lock_toggle.set_sensitive(False)

        self.ui_toggle = uim.add_ui_from_string(ui_lock_toggle)
        uim.ensure_update()


    def deactivate(self, shell):
        """Deactivate plugin."""
        uim = shell.get_ui_manager()

        self.prefs.shutdown()
        self.party_mode_lock.shutdown()
        del self.prefs
        del self.party_mode_lock
        del self.shell

        # Clean up UI
        self.party_mode_toggle.disconnect(self.pmt_conn_id)
        self.lock_toggle.disconnect(self.action_conn_id)
        uim.remove_ui(self.ui_toggle)
        uim.remove_action_group(self.action_group)
        del self.party_mode_toggle
        del self.lock_toggle
        del self.action_group

        uim.ensure_update()

    def create_configure_dialog(self, dialog=None):
        """Show configure dialog and return dialog object."""
        if not dialog:
            dialog = self.prefs.dialog.get_dialog()
        dialog.present()
        return dialog

    def party_mode_toggled(self, widget):
        """Enable menu item when party mode is enabled."""
        if widget.get_active():
            self.lock_toggle.set_sensitive(True)
        else:
            self.lock_toggle.set_sensitive(False)

    def lock_toggled(self, widget):
        if widget.get_active():
            self.party_mode_lock.lock()
        else:
            self.party_mode_lock.unlock(self.unlock_callback)

    def unlock_callback(self, success):
        if not success:
            self.lock_toggle.set_active(True)

