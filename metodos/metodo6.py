#!/usr/bin/python
# -*- coding: utf-8 -*- 

"""
Description: This program analize the projects and it obtains the PM of each project according to it detect month to month the professional authors and it add the proportional part make by the rest of authors.
The values of work days by authors have been adjusted with a smoothing function.
"""

import MySQLdb
from datetime import *
import numpy as np

def calendar_commit_month_author(year, month, author):
    M = np.zeros(31, dtype=np.int)
    for aux in author:
        if (int(aux[2].month) == month) & (int(aux[2].year) == year):
            M[int(aux[2].day-1)] += 1
    return M

def smooth(x, window_len=10, window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    import numpy as np    
    t = np.linspace(-2,2,0.1)
    x = np.sin(t)+np.random.randn(len(t))*0.1
    y = smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        #raise ValueError, "Input vector needs to be bigger than window size."
        return x

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s=np.r_[2*x[0]-x[window_len:1:-1], x, 2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    
    if window == 'flat': #moving average
        w = np.ones(window_len,'d')
    else:
        w = getattr(np, window)(window_len)
    y = np.convolve(w/w.sum(), s, mode='same')
    return y[window_len-1:-window_len+1]

def fix_smooth(f_original, len_window, window):
    f_smooth = np.array([], dtype=np.int)
    flag = False
    position = 0
    for i in range(len(f_original)):
        if f_original[i] != 0:
            if i+1 == len(f_original):
                if flag:
                    if len(f_original[position:]) == 7:
                        smooth_aux = smooth(np.array(f_original[position-1:]), len_window, window)
                        smooth_aux = smooth_aux[1:]
                    else:
                        smooth_aux = smooth(np.array(f_original[position:]), len_window, window)
                    f_smooth = np.append(f_smooth, smooth_aux)
                else:
                    f_smooth = np.append(f_smooth, f_original[i])
            elif not flag:
                position = i
                flag = True
        elif f_original[i] == 0 and flag:
            if i+1 == len(f_original):
                if len(f_original[position:i]) == 7:
                    smooth_aux = smooth(np.array(f_original[position-1:i]), len_window, window)
                    smooth_aux = smooth_aux[1:]
                else:
                    smooth_aux = smooth(np.array(f_original[position:i]), len_window, window)
                f_smooth = np.append(f_smooth, smooth_aux)
                f_smooth = np.append(f_smooth, 0)
                flag = False
            elif f_original[i+1] == 0:
                if len(f_original[position:i]) == 7:
                    smooth_aux = smooth(np.array(f_original[position:i+1]), len_window, window)
                    smooth_aux = smooth_aux[:-1]
                else:
                    smooth_aux = smooth(np.array(f_original[position:i]), len_window, window)
                f_smooth = np.append(f_smooth, smooth_aux)
                f_smooth = np.append(f_smooth, 0)
                flag = False
        else:
            f_smooth = np.append(f_smooth, 0)
    return f_smooth

list_projects = []

#list_projects.append('openstack_authors')

list_projects.append('vizgrimoire_vizgrimoirer_cvsanaly')
list_projects.append('openstack_tempest_cvsanaly')
list_projects.append('twbs_bootstrap_cvsanaly')
#GNOME
list_projects.append('gnome_easytag_cvsanaly')
list_projects.append('gnome_gnoduino_cvsanaly')
list_projects.append('gnome_libgee_cvsanaly')
list_projects.append('gnome_chronojump_cvsanaly')
list_projects.append('gnome_gnome_calendar_cvsanaly')
list_projects.append('gnome_libgweather_cvsanaly')
list_projects.append('gnome_kupfer_cvsanaly')
list_projects.append('gnome_gedit_cvsanaly')
list_projects.append('gnome_tracker_cvsanaly')
list_projects.append('gnome_gnome_packagekit_cvsanaly')

for project in range(0, len(list_projects)):
    print 'Project: ' + list_projects[project]
    con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                          db=list_projects[project])
    cursor = con.cursor()

    cursor.execute('SELECT MIN(date) FROM scmlog')
    date_min = cursor.fetchall()[0][0]
    cursor.execute('SELECT MAX(date) FROM scmlog')
    date_max = cursor.fetchall()[0][0]

    period = range(date_min.year,date_max.year)
    period.append(date_max.year)

    query = ('SELECT id from upeople')
    cursor.execute(query)
    upeople = cursor.fetchall()

    authors_commits = []
    authors_ids = []
    for aut in upeople:
        query = ('SELECT people_id FROM people_upeople WHERE upeople_id=%s')
        cursor.execute(query, aut[0])
        people_ids = cursor.fetchall()
        if people_ids:
            list_commits = ()
            for id in people_ids:
                query = ('SELECT committer_id, author_id, author_date FROM scmlog '
                         'WHERE author_id = %s')
                cursor.execute(query, id[0])
                list_commits += cursor.fetchall()
            authors_commits.append(tuple(sorted(list_commits, key=lambda item: item[2])))
            authors_ids.append(people_ids)
    
    tot_authors = len(authors_commits)

    work_authors = []
    for author in authors_commits:
        M_month = []
        for year in period:
            first_month = 1
            last_month = 12
            if year == date_min.year:
                first_month = date_min.month
                last_month = 12
            elif year == date_max.year:
                first_month = 1
                last_month = date_max.month
            for month in range(first_month, last_month+1):
                aut = calendar_commit_month_author(year, month, author)
                work_days = 0
                for i in range(len(aut)):
                    if aut[i] != 0:
                        work_days += 1
                M_month.append(work_days)
        work_authors.append(M_month)

    windows= 'hanning'
    len_window = 7
    
    smooth_work_authors = []
    for aut in work_authors:
        smooth_work_authors.append(fix_smooth(np.array(aut), len_window, windows))
    
    PM = []
    prof_in_month = []
    len_list = len(smooth_work_authors[0])
    for month in range(0, len_list):
        prof_authors = 0
        rest_authors = 0
        min_dw = 10
        for author in range(0, tot_authors):
            if smooth_work_authors[author][month] >= min_dw:
                prof_authors += 1
            else:
                rest_authors += smooth_work_authors[author][month]/11.0
        PM.append(prof_authors + rest_authors)
        prof_in_month.append(prof_authors)

    print 'Total authors: ' + str(tot_authors)
    print 'Total PM: ' + "{0:.2f}".format(np.sum(PM))    
    print 'Professional authors[per month]:'
    print prof_in_month
    print 'Added professional:'
    print np.sum(prof_in_month)
    print
    print '----------------------------------------------'

    cursor.close()
    con.close()
