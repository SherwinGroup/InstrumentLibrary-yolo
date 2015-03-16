# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 17:30:17 2015

@author: dvalovcin
"""

import numpy as np
import matplotlib.pylab as plt
from matplotlib import rcParams
import scipy.optimize as spo
import glob
import os

rcParams['axes.labelsize'] = 32
rcParams['xtick.labelsize'] = 32
rcParams['ytick.labelsize'] = 32
rcParams['legend.fontsize'] = 32
rcParams['axes.titlesize'] = 32
rcParams['font.size'] = 32
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']

rcParams['xtick.major.size'] = 14
rcParams['xtick.major.width'] = 3
rcParams['ytick.major.size'] = 14
rcParams['ytick.major.width'] = 3
#rcParams['text.usetex'] = True

#ax.spines["right"].set_visible(False)
#ax.spines["top"].set_visible(False)
#ax.spines["left"].set_linewidth(2)
#ax.spines["bottom"].set_linewidth(2)
#
#ax.yaxis.set_ticks_position('left')
#ax.xaxis.set_ticks_position('bottom')
#xticks = ax.xaxis.get_major_ticks()
#xticks[0].tick1On = False
#xticks[-1].tick1On = False
#fig.tight_layout(pad=0.1)
plt.close('all')
def f(x, *p):
    mu = p[0]
    a0 = p[1]
    a1 = p[2]
    a2 = p[3]
    return a0 + a1*(x-mu)**2 + a2*(x-mu)**3
    
def f2(x, *p):
    mu = p[0]
    a = p[1]
    b = p[2]
    c = p[3]
    return a*np.cos(b*(x-mu))**4 + c


frequency = 600
# the transmission of the window as a function of frequency
# more values in the TK manual
T = {300: 0.910,
     400: 0.900,
     500: 0.880,
     600: 0.860}

responsivity = 0.02196 # mJ/mV, as measured by Darren in fall 2014. measured to positive peak


fileList = glob.glob(r".\600GHz_2-26\TK*.csv")
attens = dict()
for name in fileList:
    desc = os.path.basename(name).split('.')[0]
    angle = float(desc[2:4])
    data = np.loadtxt(name, delimiter=',', skiprows=1, usecols=(0,1))
    
    
    v = attens.get(angle, [])
    v.append(data)
    attens[angle] = v

n = 0.0

aves = dict()
for key in attens.keys():
    vals = attens[key]
    aves[key] = np.zeros(vals[0].shape)
    print "key: {}\n\t shape: {}".format(key, aves[key].shape)
    aves[key][:,0] = vals[0][:,0]
    for arr in vals:
        aves[key][:,1] += arr[:,1]
    aves[key][:,1] /= float(len(vals))
    aves[key][:,1] = list(aves[key][:,1]) - sum(aves[key][:100,1])/100


# Fit the peaks to a polynomial to get a better estimate of the peak value
allP = []
maxx = np.empty((0, 2))
for n in aves.keys():
#    plt.figure()
    plt.title(str(n))
    plt.plot(aves[n][:,0], aves[n][:,1])
    idx = np.argmax(aves[n][:,1])
    plt.plot(aves[n][idx-20:idx+20,0], aves[n][idx-20:idx+20,1], linewidth=3)
    
    p, popt = spo.curve_fit(f, aves[n][idx-20:idx+20,0], aves[n][idx-20:idx+20,1], p0=[0.05, 1, 1, 1])
    allP.append(p)
    plt.plot(aves[n][idx-20:idx+20,0], f(aves[n][idx-20:idx+20,0], *p))
    maxx = np.vstack((maxx, [[n, max(f(aves[n][idx-20:idx+20,0], *p))]]))

# convert the peak values to energies
maxx[:,1] = maxx[:,1] / (0.49 * T[frequency]) * responsivity *1000 # peaks measured in volts, responsivity
                                                                   # measured in mJ/mV

maxx = maxx[maxx[:,0].argsort()]


plt.figure()
plt.plot(maxx[:,0], maxx[:,1], 'o')
p, popt = spo.curve_fit(f2, maxx[:,0], maxx[:,1], p0=[0, 4, 0.01, 1])
x = np.linspace(maxx[0,0], maxx[-1,0], 50)
plt.plot(x, f2(x, *p))
print p

#plt.title()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    