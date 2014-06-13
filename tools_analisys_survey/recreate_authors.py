#!/usr/bin/python

#
# Given a CSV filename with author merging information
# (for every developer_id, other developer_ids for the same author is given)
# Returns (prints to STDOUT)
#
# In the context of the MSR 2014, this script should be launched as follows:
# $ python recreate_authors.py output_authors_ids.csv
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

import sys

def recreate(filename):

    input = open(filename, 'r')

    idList = []

    while input:
        line = input.readline()
        if not line:
            break
        if line[0] == "#":
            continue
        identifier = line.split('(')[1]
        identifier = identifier[:identifier.find('L,')]
        idList.append(int(identifier))

    return idList

if __name__ == "__main__":
    print recreate(sys.argv[1])
