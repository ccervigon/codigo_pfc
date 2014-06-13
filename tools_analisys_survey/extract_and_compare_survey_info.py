#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb
from datetime import *
import numpy as np
import sys
import sqlite3
import csv

def calendar_commit_month_author(year, month, author):
    """
    This method take a month and a year of one author and it returns an array of
    31 integers with the number of commits done on each day.
    """
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


if __name__ == "__main__":
    db_survey = sys.argv[1]
    db_project = sys.argv[2]
    dir_to_save = sys.argv[3]

    con2 = sqlite3.connect(db_survey)
    con2.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    cursor2 = con2.cursor()

    con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                          db=db_project)
    cursor = con.cursor()

    cursor.execute('SELECT MIN(date) FROM scmlog')
    date_min = cursor.fetchall()[0][0]
    cursor.execute('SELECT MAX(date) FROM scmlog')
    date_max = cursor.fetchall()[0][0]

    period = range(date_min.year,date_max.year)
    period.append(date_max.year)

    authors_commits = []
    authors_id = []
    authors_work = []
    authors_consider = []
    query = ('SELECT upeople_id,resp1,resp4 from surveyApp_survey_author')
    for aut in cursor2.execute(query):
        authors_work.append(aut[1])
        authors_consider.append(aut[2])
        query = ('SELECT people_id FROM people_upeople WHERE upeople_id=%s')
        cursor.execute(query, aut[0])
        people_ids = cursor.fetchall()
        if people_ids:
            list_commits = ()
            for id in people_ids:
                query = ('SELECT committer_id, author_id, date FROM scmlog '
                         'WHERE author_id = %s')
                cursor.execute(query, id[0])
                list_commits += cursor.fetchall()
            authors_commits.append(tuple(sorted(list_commits, key=lambda item: item[2])))
            authors_id.append(aut[0])

    tot_authors = len(authors_commits)

    work_authors = []
    commits_author = []
    aux=0
    for author in authors_commits:
        M_month = []
        N_month = []
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
                N_month.append(np.sum(aut))
        work_authors.append(M_month)
        commits_author.append(N_month)

    work_agreg = []
    commits_agreg = []
    for author in range(len(authors_id)):
        work_agreg.append(np.sum(work_authors[author][-6:]))
        commits_agreg.append(np.sum(commits_author[author][-6:]))

    with open(dir_to_save + "info_authors.csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerow(['Upeople_id', 'Sum of activity by the author in the last 6 months', 'Sum of commits by the author in the last 6 months'])
        for i in range(len(work_agreg)):
            writer.writerow([authors_id[i], work_agreg[i], commits_agreg[i]])

    windows= 'hanning'
    len_window = 7

    smooth_work_authors = []
    for aut in work_authors:
        smooth_work_authors.append(fix_smooth(np.array(aut), len_window, windows))

    len_list = len(smooth_work_authors[0])
    PM_authors = []
    min_dw = 10
    for author in range(tot_authors):
        PM_author = []
        for month in range(-6, 0):
            if smooth_work_authors[author][month] >= min_dw:
                PM_author.append(1)
            else:
                PM_author.append(smooth_work_authors[author][month]/11.0)
        PM_authors.append(PM_author)

    pm_tot_author = []
    pm_comp_author = []
    pm_comp_perc_author = []

    pm_full = np.array([1,1,1,1,1,1])
    pm_part = np.array([0.5,0.5,0.5,0.5,0.5,0.5])
    pm_occa = np.array([0.25,0.25,0.25,0.25,0.25,0.25])
    for author in range(tot_authors):
        print 'Author_upeople_id:', authors_id[author]
        print 'He considers himself:', authors_consider[author]
        print 'He works in the project:', authors_work[author]
        print 'PM per month:', PM_authors[author]
        print 'Total PM:', np.sum(PM_authors[author])
        print 'Matrix [[PM_model, PM_consider, PM_work]x6 last months]'
        if authors_consider[author] == 'full':
            pm_consider = pm_full
        elif authors_consider[author] == 'part':
            pm_consider = pm_part
        else:
            pm_consider = pm_part
        if authors_work[author] == '45':
            pm_work = np.zeros(6)
            pm_work.fill(1)
        elif authors_work[author] == 'None':
            pm_work = np.zeros(6)
            pm_work.fill(0)
        else:
            pm_work = np.zeros(6)
            pm_work.fill(float(authors_work[author])/40)

        pms = [np.sum(PM_authors[author]), np.sum(pm_consider), np.sum(pm_work)]
        pm_tot_author.append(pms)

        pms_comp = [np.abs(pms[1]-pms[0]), np.abs(pms[2]-pms[0])]
        pm_comp_author.append(pms_comp)

        pms_comp_perc = [100*(pms_comp[0]/pms[0]), 100*(pms_comp[1]/pms[0])]
        pm_comp_perc_author.append(pms_comp_perc)

        print np.matrix([np.array(PM_authors[author]),pm_consider,pm_work])
        print 'Errores cometidos:'
        print 'PM_Model:', "{0:.2f}".format(pms[0]), 'PM_consider:', "{0:.2f}".format(pms[1]), 'Differencia:', "{0:.2f}".format(pms_comp[0]), 'Diff %:', "{0:.2f}".format(pms_comp_perc[0])
        print 'PM_Model:', "{0:.2f}".format(pms[0]), 'PM_work:', "{0:.2f}".format(pms[2]), 'Differencia:', "{0:.2f}".format(pms_comp[1]), 'Diff %:', "{0:.2f}".format(pms_comp_perc[1])
        print 'PM_consider:', "{0:.2f}".format(pms[1]), 'PM_work:', "{0:.2f}".format(pms[2]), 'Differencia:', "{0:.2f}".format(np.abs(np.sum(pm_work)-np.sum(pm_consider))), 'Diff %:', "{0:.2f}".format(100*(np.sum(pm_consider)-np.sum(pm_work))/np.sum(pm_work))
        print '------------------------------------------------'

    cursor.close()
    con.close()
