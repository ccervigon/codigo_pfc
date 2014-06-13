#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb
import argparse
from subprocess import call
import os

list_projects = []
list_projects.append('VizGrimoire/VizGrimoireR')
list_projects.append('openstack/tempest')
list_projects.append('twbs/bootstrap')
#GNOME
list_projects.append('GNOME/easytag')
list_projects.append('GNOME/gnoduino')
list_projects.append('GNOME/libgee')
list_projects.append('GNOME/chronojump')
list_projects.append('GNOME/gnome-calendar')
list_projects.append('GNOME/libgweather')
list_projects.append('GNOME/kupfer')
list_projects.append('GNOME/gedit')
list_projects.append('GNOME/tracker')
list_projects.append('GNOME/gnome-packagekit')

# Parse command line options
parser = argparse.ArgumentParser(description="""Scripts to execute the models""")
parser.add_argument("-u",
                    help = "MySQL user name",
                    required = True)
parser.add_argument("-p",
                    help = "MySQL password",
                    required = True)
parser.add_argument("--dir",
                    help="Projects extraction directory (must exist). Default: /tmp",
                    default = '/tmp')

args = parser.parse_args()

for project in list_projects:
    # Open database connection and get a cursor
    con = MySQLdb.connect(host='localhost', user=args.u, passwd=args.p) 
    cursor = con.cursor()
    # Create (and maybe remove) the database
    dbPrefix = project.replace('/', '_').lower()
    dbPrefix = dbPrefix.replace('-', '_')
    dbname = dbPrefix + "_cvsanaly"
    cursor.execute('DROP DATABASE IF EXISTS ' + dbname)
    cursor.execute('CREATE DATABASE ' + dbname +
                   ' CHARACTER SET utf8 COLLATE utf8_unicode_ci')
    
    gitdir = project.split('/', 1)[1]
    call(['rm', '-rf', args.dir + '/' + gitdir])
    call(["git", "clone", "https://github.com/" + project + ".git",
          args.dir + '/' + gitdir])
    
    call(["cvsanaly2", "-u", args.u, "-p", args.p, "-d", dbname, "--extensions=CommitsLOC", args.dir + '/' + gitdir])
    
    cursor.close()
    con.close()

print
print 'Running Models'
print 'Running count_pm.py...',
os.system('python count_pm.py > result_count_pm.txt')
print 'Done'
print 'Running count_pm2.py...',
os.system('python count_pm2.py > result_count_pm2.txt')
print 'Done'
print 'Running count_pm3.py...',
os.system('python count_pm3.py > result_count_pm3.txt')
print 'Done'
print
print 'Script completed (You can see the results on files "result_count_pm*.txt", created in the current directory)'
