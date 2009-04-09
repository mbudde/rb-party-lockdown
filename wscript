#! /usr/bin/env python
# encoding: utf-8

PLUGINNAME  = 'party-lockdown'
APPNAME     = 'rb-party-lockdown'
VERSION     = '0.3'
DESCRIPTION = 'Lock “Party Mode” with a password and disable GUI elements that could be abused.'
WEBSITE     = 'https://launchpad.net/rb-party-lockdown'

srcdir = 'src'
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

    import Options, Utils, os.path
    conf.env['destdir'] = Options.options.destdir
    if not conf.env['destdir']:
        if Options.options.system_wide:
            conf.env['destdir'] = '/usr/lib/rhythmbox/plugins'
        else:
            conf.env['destdir'] = os.path.expanduser('~/.gnome2/rhythmbox/plugins')
    print 'Plugin installation directory :',
    Utils.pprint('GREEN', '%s' % conf.env['destdir'])

    conf.env['PLUGINNAME']  = PLUGINNAME
    conf.env['APPNAME']     = APPNAME
    conf.env['VERSION']     = VERSION
    conf.env['DESCRIPTION'] = DESCRIPTION
    conf.env['WEBSITE']     = WEBSITE

def build(bld):
    import misc
    bld.new_task_gen(
        features='subst',
        source='party-lockdown.rb-plugin.in',
        target='party-lockdown.rb-plugin',
        dict=bld.env,
        fun=misc.subst_func
    )
    bld.compile()

    import Options
    Options.options.destdir = bld.env['destdir']

    bld.install_files(PLUGINNAME, '*.py')
    bld.install_files(PLUGINNAME, '*.glade')
    bld.install_files(PLUGINNAME, 'party-lockdown.rb-plugin')
