## Party Lockdown - Rhythmbox plugin ##

The purpose of this plugin is to protect "Party Mode" with a password to
prevent users from going out of "Party Mode". It also disables some menu 
items and other widgets that could be abused or is not useful in a party
situation.

If you want to report a bug or ask a question please go to
[the project's page](https://launchpad.net/rb-party-lockdown) at Launchpad.


### Installation ###

To install the plugin run:

    ./waf configure
    ./waf install

This defaults to installing the plugin system-wide.
To install "user-wide" use:

    ./waf configure --user-wide

The plugin will be install to `~/.local/share/rhythmbox/plugins`.
This requires that you run at least Rhythmbox version 0.12.0. If
you are running an older version install with:

    ./waf configure --destdir=~/.gnome2/rhythmbox/plugins


### License ###

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

See `COPYING` for the full GNU General Public License.
