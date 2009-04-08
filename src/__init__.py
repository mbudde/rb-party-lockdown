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
from preferences import GConfPreferences, PreferenceDialog

PARTY_LOCKDOWN_GCONF_PATH = '/apps/rhythmbox/plugins/party-lockdown'
PREFS_DIALOG_GLADE = 'party-lockdown-prefs.glade'
UNLOCK_DIALOG_GLADE = 'party-lockdown-unlock.glade'

LOCK_TOGGLE_UI = """
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
    default_prefs = {
        'password': '',
        'hide_menu_bar': False,
    }

    def __init__(self):
        rb.Plugin.__init__(self)

    def activate(self, shell):
        self.prefs = GConfPreferences(PARTY_LOCKDOWN_GCONF_PATH,
                                      self.default_prefs)
        pref_glade = self.find_file(PREFS_DIALOG_GLADE)
        self.pref_dialog = PreferenceDialog(self.prefs, pref_glade)

        uim = shell.get_ui_manager()
        unlock_glade = self.find_file(UNLOCK_DIALOG_GLADE)
        self.partymode_lock = PartyModeLock(self.prefs, uim, unlock_glade)

        # Connect callback for Party Mode toggle
        self.partymode_toggle = uim.get_widget('/MenuBar/ViewMenu/ViewPartyModeMenu')
        self.pmt_id = self.partymode_toggle.connect('toggled', self.partymode_toggled)

        # Set up action for Party Mode lock
        self.lock_toggle = gtk.ToggleAction('ToggleLockPartyMode',
                                            _('Lock Party Mode'),
                                            _('Password protect party mode'),
                                            'rb-lock-partymode')
        self.lt_id = self.lock_toggle.connect('toggled', self.lock_toggled)
        self.action_group = gtk.ActionGroup('LockPartyModePluginActions')
        self.action_group.add_action_with_accel(self.lock_toggle, 'F12')
        self.ui_id = uim.add_ui_from_string(LOCK_TOGGLE_UI)
        uim.insert_action_group(self.action_group, 0)
        uim.ensure_update()

        if not shell.get_party_mode():
            self.lock_toggle.set_sensitive(False)

    def deactivate(self, shell):
        self.partymode_lock.shutdown()
        del self.prefs
        del self.pref_dialog
        del self.partymode_lock

        # Clean up UI
        uim = shell.get_ui_manager()
        self.partymode_toggle.disconnect(self.pmt_id)
        self.lock_toggle.disconnect(self.lt_id)
        uim.remove_ui(self.ui_id)
        uim.remove_action_group(self.action_group)
        uim.ensure_update()
        del self.partymode_toggle
        del self.lock_toggle
        del self.action_group

    def create_configure_dialog(self, dialog=None):
        if not dialog:
            dialog = self.pref_dialog.get_dialog()
        dialog.present()
        return dialog

    def partymode_toggled(self, widget):
        if widget.get_active():
            self.lock_toggle.set_sensitive(True)
        else:
            self.lock_toggle.set_sensitive(False)

    def lock_toggled(self, widget):
        if widget.get_active():
            self.partymode_lock.lock()
        else:
            self.partymode_lock.unlock(self.unlock_callback)

    def unlock_callback(self, success):
        if not success:
            self.lock_toggle.set_active(True)

