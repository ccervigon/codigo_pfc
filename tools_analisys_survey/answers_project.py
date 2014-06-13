#!/usr/bin/python

#
# Given a filename with survey data in CSV, returns a 
# dictionary with the developer_id as the key and
# the answers to the survey as following list:
# [commitment, hours, percentage, int(days), int(commits)]
#
# In the context of the MSR 2014, the usual filename used
# as input should be "answers_openstack.csv"
#

#
# Copyright (C) 2014 GSyC/LibreSoft - Universidad Rey Juan Carlos
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Gregorio Robles <grex@gsyc.urjc.es>

def survey(filename):
    input = open(filename, 'r')

    surveyDict = {}
    while 1:
        line = input.readline()
        if not line:
            break
        if line[0] == "#":
            continue
        devel = line[:-1].split('\t')
        ident = devel[2]
        hours = devel[3]
        if '>' in hours or '<' in hours:
            hours = hours[1:]
        commitment = devel[6]
        percentage = devel[4]
        if '>' in percentage or '<' in percentage:
            percentage = percentage[1:]
        days = devel[-2]
        commits = devel[-1]
#    if hours in ['30', '40', '45'] and commitment in ['full', 'part'] and int(commits) > 0:
        surveyDict[int(ident)] = [commitment, hours, percentage, int(days), int(commits)]
    return surveyDict

if __name__ == "__main__":
    import sys
    print survey(sys.argv[1])
