#! /usr/bin/env python
# encoding: utf-8

VERSION='0.2'
PLUGINNAME='party-lockdown'
APPNAME='rb-' + PLUGINNAME

srcdir = 'src'
blddir = 'build'

import Scripting
Scripting.g_gz = 'gz'

def set_options(opt):
    opt.tool_options('python') # options for disabling pyc or pyo compilation

def configure(conf):
    conf.check_tool('python')
    conf.check_python_version((2,4,2))

    conf.check_python_module('gobject')
    conf.check_python_module('gtk')
    conf.check_python_module('gconf')

    conf.env['PLUGINNAME'] = PLUGINNAME

def build(bld):
    obj = bld.new_task_gen('py')
    obj.find_sources_in_dirs('.', exts=['.py'])
    obj.install_path = None

    import misc
    obj = bld.new_task_gen('subst')
    obj.source = 'party-lockdown.rb-plugin.in'
    obj.target = 'party-lockdown.rb-plugin'
    obj.dict = {'PLUGINNAME': PLUGINNAME, 'VERSION': VERSION}
    obj.fun = misc.subst_func

    import Options, os.path
    if not bld.env.get_destdir():
        Options.options.destdir = os.path.expanduser('~/.gnome2/rhythmbox/plugins')

    bld.install_files(PLUGINNAME, '*.py')
    bld.install_files(PLUGINNAME, '*.glade')
    bld.install_files(PLUGINNAME, 'party-lockdown.rb-plugin')


