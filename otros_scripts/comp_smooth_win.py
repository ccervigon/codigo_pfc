#!/usr/bin/python

import MySQLdb
from datetime import *
import numpy as np
import matplotlib.pyplot as plt

class Info_diff:
    def __init__(self):
        self.media = []
        self.desv_tip = []

def calendar_commit_month_author(year, month, author):
    M = np.zeros(31, dtype=np.int)
    for aux in author:
        if (int(aux[2].month) == month) & (int(aux[2].year) == year):
            M[int(aux[2].day-1)] += 1
    return M

def estadistica_smooth(list_aux, info, limit_up, limit_down):
    for i in range(0, len(list_aux)):
        info.media.append(np.nan)
        info.desv_tip.append(np.nan)
        for j in range(i+1, len(list_aux)):
            diff = list_aux[j] / list_aux[i] - 1
            diff = diff[np.isfinite(diff)]
            diff = np.absolute(diff)
            diff_aux = np.sort(diff)[limit_down:-limit_up]*100
            info.media.append(np.mean(diff_aux))
            info.desv_tip.append(np.std(diff_aux))

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
    for i in range(0, len(f_original)):
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
                    smooth_aux = smooth(np.array(f_original[position-1:i]), len_window, window)
                    smooth_aux = smooth_aux[1:]
                else:
                    smooth_aux = smooth(np.array(f_original[position:i]), len_window, window)
                f_smooth = np.append(f_smooth, smooth_aux)
                f_smooth = np.append(f_smooth, 0)
                flag = False
        else:
            f_smooth = np.append(f_smooth, 0)
    return f_smooth

list_projects = []
#list_projects.append('vizgrimoire_vizgrimoirer_cvsanaly')
#list_projects.append('openstack_tempest_cvsanaly')
#list_projects.append('twbs_bootstrap_cvsanaly')
#GNOME
#list_projects.append('gnome_easytag_cvsanaly')
#list_projects.append('gnome_gnoduino_cvsanaly')
#list_projects.append('gnome_libgee_cvsanaly')
#list_projects.append('gnome_chronojump_cvsanaly')
#list_projects.append('gnome_gnome_calendar_cvsanaly')
list_projects.append('gnome_libgweather_cvsanaly')
#list_projects.append('gnome_kupfer_cvsanaly')
#list_projects.append('gnome_gedit_cvsanaly')
#list_projects.append('gnome_tracker_cvsanaly')
#list_projects.append('gnome_gnome_packagekit_cvsanaly')

for project in range(0, len(list_projects)):
    print 'Project: ' + list_projects[project]
    con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                          db=list_projects[project])
    cursor = con.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM people')
    tot_authors = int(cursor.fetchall()[0][0])
    
    cursor.execute('SELECT MIN(date) FROM scmlog')
    date_min = cursor.fetchall()[0][0]
    date_min = date_min.year
    cursor.execute('SELECT MAX(date) FROM scmlog')
    date_max = cursor.fetchall()[0][0]
    date_max = date_max.year
    
    period = range(date_min,date_max)
    period.append(date_max)
    
    authors = []
    for i in range(1,tot_authors+1):
        query = ('SELECT committer_id, author_id, author_date FROM scmlog '
                  'WHERE author_id = %s ORDER BY author_date')
        cursor.execute(query, i)
        authors.append(cursor.fetchall())

    work_authors_month = []
    work_authors_days = []
    work_authors_week = []
    
    for author in authors:
        M_month = []
        M_days = np.array([])
        for year in period:
            for month in range(1, 13):
                aut = calendar_commit_month_author(year, month, author)
                M_days = np.concatenate((M_days, aut))
                work_days = 0
                for i in range(0, len(aut)):
                    if aut[i] != 0:
                        work_days += 1
                M_month.append(work_days)   #CONTAMOS EN ESTE CASO LOS DIAS TRABAJADOS AL MES Y NO LOS COMMITS AL MES
                
        work_authors_days.append(M_days)
        work_authors_month.append(M_month)

    for author in range(0, len(authors)):
        ulti = 0
        M_week = []
        for i in range(4, len(work_authors_days[author]), 4):
            M_week.append(np.sum(work_authors_days[author][i-4:i]))
            ulti = i
        if ulti < len(work_authors_days[author]):
            M_week.append(np.sum(work_authors_days[author][ulti:]))
        work_authors_week.append(M_week)

    windows=['hanning']
    len_windows = [1, 7]
    id_author = 273
    print 'Dias totales sin smooth: ' + str(np.sum(work_authors_month[id_author]))
    
    list_aux_month = []
    list_aux_days = []
    list_aux_week = []
    for w in range(0, len(windows)):
        i = 0
        for len_window in len_windows:
            i += 1
            smooth_work_days_authors = []
            for aut in work_authors_month:
                smooth_work_days_authors.append(fix_smooth(np.array(aut), len_window, windows[w]))
            list_aux_month.append(smooth_work_days_authors[id_author])
            smooth_work_days_authors = []
            for aut in work_authors_days:
                smooth_work_days_authors.append(fix_smooth(np.array(aut), len_window, windows[w]))
            list_aux_days.append(smooth_work_days_authors[id_author])
            smooth_work_days_authors = []
            for aut in work_authors_week:
                smooth_work_days_authors.append(fix_smooth(np.array(aut), len_window, windows[w]))
            list_aux_week.append(smooth_work_days_authors[id_author])

            
            #REPRESENTACION GRAFICA
            ax = plt.subplot(len(len_windows),1,i)
            ax.bar(np.arange(len(list_aux_month[-1])), list_aux_month[-1])
            plt.axhline(10, color = 'g')
            plt.axhline(12, color = 'b')
            plt.axhline(15, color = 'r')
            ax.set_xlim(left=0, right=len(list_aux_month[-1]))
            ax.set_ylim(bottom=0, top=30)
            textstr = 'Ancho de ventana: ' + str(len_window)
            props = dict(boxstyle = 'round', facecolor = 'red', alpha = 0.15)
            ax.text(0.02, 0.86, textstr, transform = ax.transAxes, fontsize = 10, verticalalignment = 'top', horizontalalignment = 'left', bbox = props)
            
        
        #REPRESNTACION GRAFICA
        plt.subplot(len(len_windows),1,1)
        plt.title(windows[w])
        plt.savefig('figuras/prueba/author' + str(id_author) + '_' + list_projects[project] + '_' + windows[w] + '_month.png', dpi = 200)
        plt.close()
        

    info_month = Info_diff()
    info_days = Info_diff()
    info_week = Info_diff()
    estadistica_smooth(list_aux_month, info_month, 3, 1)
    estadistica_smooth(list_aux_days, info_days, 100,10)
    estadistica_smooth(list_aux_week, info_week, 30, 10)

    print '------------MONTH--------------'
    print 'Medias:'
    print np.around(info_month.media, decimals=2)
    print 'Desv tipicas:'
    print np.around(info_month.desv_tip, decimals=2)
    
    aux_media = np.array(info_month.media)
    print 'Media entre medias:', np.mean(aux_media[np.isfinite(aux_media)])
    aux_desv = np.array(info_month.desv_tip)
    print 'Media entre desv_tip:', np.std(aux_desv[np.isfinite(aux_desv)])
    print

    print '------------DAYS--------------'
    print 'Medias:'
    print np.around(info_days.media, decimals=2)
    print 'Desv tipicas:'
    print np.around(info_days.desv_tip, decimals=2)
    
    aux_media = np.array(info_days.media)
    print 'Media entre medias:', np.mean(aux_media[np.isfinite(aux_media)])
    aux_desv = np.array(info_days.desv_tip)
    print 'Media entre desv_tip:', np.std(aux_desv[np.isfinite(aux_desv)])
    print
    
    print '------------WEEK--------------'
    print 'Medias:'
    print np.around(info_week.media, decimals=2)
    print 'Desv tipicas:'
    print np.around(info_week.desv_tip, decimals=2)
    
    aux_media = np.array(info_week.media)
    print 'Media entre medias:', np.mean(aux_media[np.isfinite(aux_media)])
    aux_desv = np.array(info_week.desv_tip)
    print 'Media entre desv_tip:', np.std(aux_desv[np.isfinite(aux_desv)])
    print

    cursor.close()
    con.close()
