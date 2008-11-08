#! /usr/bin/env python
# encoding: utf-8
# Gustavo Carneiro, 2007

VERSION='0.1'
PLUGINNAME='party-lockdown'
APPNAME='rb-%s' % PLUGINNAME

srcdir = 'src'
blddir = 'build'

import os.path
import Scripting
Scripting.g_gz = 'gz'

def set_options(opt):
    opt.tool_options('python') # options for disabling pyc or pyo compilation

def configure(conf):
    conf.check_tool('python')
    conf.check_python_version((2,4,2))
    #conf.check_python_headers()

    conf.check_python_module('gobject')
    conf.check_python_module('gtk')
    conf.check_python_module('gconf')

    conf.env['PLUGINNAME'] = PLUGINNAME
    #import Params
    #if not Params.g_options.destdir:
        ##conf.env['DESTDIR'] = Params.g_options.destdir
        ##conf.env['DESTDIR'] = os.path.expanduser('~/.gnome2/rhythmbox/plugins')
        #Params.g_options.destdir = os.path.expanduser('~/.gnome2/rhythmbox/plugins')
    #print 'Installation directory set to \'%s/%s\'' % (conf.env.get_destdir(), PLUGINNAME)

def build(bld):
    obj = bld.create_obj('py')
    obj.find_sources_in_dirs('.', exts=['.py'])
    obj.inst_var = 0
    
    print obj.env.get_destdir()
    import Common, Params
    if not obj.env.get_destdir():
        Params.g_options.destdir = os.path.expanduser('~/.gnome2/rhythmbox/plugins')

    install_files('PLUGINNAME', '', '*.py')
    install_files('PLUGINNAME', '', '*.glade')
    install_files('PLUGINNAME', '', '*.rb-plugin')
    #obj.inst_var = 'DESTDIR'
    #obj.inst_dir = PLUGINNAME


