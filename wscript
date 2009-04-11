#! /usr/bin/env python
# encoding: utf-8

PLUGINNAME  = 'party-lockdown'
APPNAME     = 'rb-party-lockdown'
VERSION     = '0.3'
DESCRIPTION = 'Lock “Party Mode” with a password and disable GUI elements that could be abused.'
WEBSITE     = 'https://launchpad.net/rb-party-lockdown'

srcdir = '.'
blddir = 'build'

import Scripting
Scripting.g_gz = 'gz'

def set_options(opt):
    #opt.tool_options('python') # options for disabling pyc or pyo compilation
    opt.add_option('--system-wide', action='store_true', default=True,
                   help='install plugin system-wide (default)')
    opt.add_option('--user-wide', dest='system_wide', action='store_false',
                   help="install plugin in current user's home directory")

def configure(conf):
    #conf.check_tool('python')
    #conf.check_python_version((2,4,2))
    #conf.check_python_module('gobject')
    #conf.check_python_module('gtk')
    #conf.check_python_module('gconf')
    conf.check_tool('misc')

    import Options, Utils, os.path
    conf.env['destdir'] = os.path.expanduser(Options.options.destdir)
    if not conf.env['destdir']:
        if Options.options.system_wide:
            conf.env['destdir'] = '/usr/lib/rhythmbox/plugins'
        else:
            conf.env['destdir'] = os.path.expanduser('~/.local/share/rhythmbox/plugins')
    conf.check_message_1('Plugin installation directory')
    conf.check_message_2('%s' % conf.env['destdir'])

    conf.env['PLUGINNAME']  = PLUGINNAME
    conf.env['APPNAME']     = APPNAME
    conf.env['VERSION']     = VERSION
    conf.env['DESCRIPTION'] = DESCRIPTION
    conf.env['WEBSITE']     = WEBSITE

def build(bld):
    bld.new_task_gen(
        features='subst',
        source='src/party-lockdown.rb-plugin.in',
        target='party-lockdown.rb-plugin',
        dict=bld.env
    )
    bld.compile()

    import Options
    Options.options.destdir = bld.env['destdir']

    bld.install_files(PLUGINNAME, 'src/*.py')
    bld.install_files(PLUGINNAME, 'src/*.glade')
    bld.install_files(PLUGINNAME, 'party-lockdown.rb-plugin')
