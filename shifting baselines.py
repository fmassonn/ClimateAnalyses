#!/usr/bin/python3

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
from matplotlib.dates import DateFormatter
from dateutil.relativedelta import *
import matplotlib.font_manager as fm

prop = fm.FontProperties(fname="/Users/massonnetf/Library/Fonts/ProximaNova-Regular.otf")

import os

def getUccle():
    myList = list()
    import csv
    with open('./data_uccle.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter= '\t', )
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                year = int(row[0][:4])
                month = int(row[0][4:6])
                day = int(row[0][6:8])
                
                value1 = float(row[2])
                value2 = float(row[1])
                value = (value1 + value2) / 2
                # mean taken as mean between max and min
                myList.append([datetime.date(year, month, day) , value\
                               ])
            line_count += 1
    return myList

data = getUccle()



yearb = data[0][0].year
yeare = data[-1][0].year 
winlength = 30 # Number of years to average
sampleYear = 2018 # Year to plot data for
doSampleCycle = True
for y1 in np.arange(yearb, yeare - winlength):
    print(y1)
    y2 = y1 + winlength - 1
    
    # Compute annual cycle, ignore moron's 29 Feb
    # For this consider a non-leap year, like 2005
    cycle = list()
    
    d = 0
    thisDate = datetime.date(2005, 1, 1)
    days2005 = [thisDate + datetime.timedelta(days = nt) for nt in np.arange(0.0, 365)]
    while thisDate <= datetime.date(2005, 12, 31):

        
        # Get current day and month
        thisDay = thisDate.day
        thisMonth = thisDate.month
        
        # Gather all data for days and month matchinc those current day 
        # and month, for year in between y1 and y2 included
        
        cycle.append(np.mean([d[1] for d in data if  d[0].day == thisDay \
                            and d[0].month == thisMonth \
                            and d[0].year  >= y1        \
                            and d[0].year  <= y2]))
        
    
        thisDate += datetime.timedelta(days = 1)
    
    cycle = np.array(cycle)
    
    # Compute anomalies for sampleYear
    rawData = np.array([d[1] for d in data if d[0].year == sampleYear])
    anomalies = rawData - cycle
    fig, ax = plt.subplots(1, 1, figsize = (7, 7 / 3), dpi = 300, facecolor = "black")
    ax.plot(days2005, cycle, color = "white", lw = 1.5)
    ax.set_facecolor("black")
    # Plot bars with raw data
    # ax.bar(days2005, rawData)
    # Plot anomalies
    ax.set_ylabel("°C", color = "white", rotation = 0, fontproperties = prop)
    ax.set_title("Température moyenne journalière à Uccle en " \
                 + str(sampleYear), color = "white", fontproperties = prop)
    
    
    # Horizontal grid
    for lab in [-10, -5, 0, 5, 10, 15, 20, 25, 30, 35]:
        if lab == 0.0:
            lw = 1.0
        else:
            lw = 0.2
        
        if lab % 10 == 0:
            ax.text(days2005[0], lab, str(lab), color = "white", \
                    va = "center", ha = "right", fontproperties = prop)
        ax.plot((days2005[0], days2005[-1]), (lab, lab), color = [0.5, 0.5, 0.5], \
                lw = lw, zorder = -10)

    
    for j, d in enumerate(days2005):
        xmin, xmax = -10, 10
        color = plt.cm.RdBu_r(int((anomalies[j]- xmin) * 255 / (xmax - xmin)))[:3]
        ax.bar(days2005[j], anomalies[j], bottom = cycle[j], color = color)
    # Fill between to alternate months
    for m in range(1, 13):
        if m % 2 == 0:
            alpha = 0.2
        else:
            alpha = 0.1
            #color = [0.95, 0.95, 0.95]
        d1 = datetime.date(2005, m, 1)
        d2 = datetime.date(2005, m, 1) + relativedelta(months = 1) #- datetime.timedelta(days = 1)
        ax.fill_between((d1, d2), (-30, -30), (30, 30), color = "white", \
                        alpha = alpha, lw = 0)
        month = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", \
                 "Aoû", "Sep", "Oct", "Nov", "Déc"][m - 1]
        ax.text(d1 + timedelta(days = 15), -8, month, color = "white", \
                fontproperties = prop, ha = "center")
    
    ax.set_xlim(datetime.date(2005, 1, 1), datetime.date(2005,12,31))
    ax.set_ylim(-10.0, 30.0)
    ax.text(days2005[35], 25, "Normale " + str(y1) + "-" + str(y2), \
            color = "white", fontproperties = prop, va = "center")
    if doSampleCycle:
        # For legend
        sampleCycle = cycle[15:30] - np.mean(cycle[15:30]) + 25
        doSampleCycle = False
    ax.plot(days2005[15:30], sampleCycle, color = "white", lw = 1.5)
    fig.savefig("./figs/" + "fig_" + str(sampleYear) + "_" + str(y1) + "-" +str(y2) + ".png")
    
print("HELLO")
stop()


years = np.arange(1901, 2018 + 1)
myList = list()
for y in years:
    tmp = np.mean([d[1] for d in data \
                   if d[0].year == int(y)])

    myList.append(tmp)
        

series = np.array(myList)


for y in np.arange(1931, 2019):
    print(y)
    # We browse through all years and compute anomalies relative 
    # to the three closest full decades
    
    ye = int(np.floor(y / 10) * 10)
    yb = ye - 30 + 1
    
    fig , ax = plt.subplots(2, 1, figsize = (5, 5), dpi = 300)

    # Plot raw data

    ax[0].set_ylim(5, 15)
    ax[0].grid()
    
    for j, year in enumerate(np.arange(1901, 2019)):
        # If before current year, in green
        if year <= y:
            ax[0].bar(year, series[j], color = "lightgreen", alpha = 0.8)
        else:
            ax[0].bar(year, series[j], edgecolor = "white", \
                      color = "black", lw = 0.2)
        
        
    ax[0].set_facecolor("black")
    ax[0].set_xlim(1900, 2021)

    
    avg = np.mean(series[(years >= yb) * (years <= ye)])
    ax[0].plot((yb, ye), (avg, avg), color = "white", lw = 2)


    ano = series - avg
    for j, year in enumerate(np.arange(1901, 2019)):
        if year <= y:
            color = plt.cm.RdBu_r(int((ano[j] + 3) * 255 / 6))
            ax[1].bar(year, ano[j], color = color, lw = 0)
        else:
            ax[1].bar(year, ano[j], edgecolor = "white", \
                      color = "black", lw = 0.2)
    ax[1].set_xlim(1900, 2021)
    ax[1].set_facecolor("black")
    ax[1].set_axisbelow(True)
    ax[1].grid()
    ax[1].set_ylim(-2.5, 2.5)
    ax[1].set_title("Anomalies par rapport à la moyenne " + \
                    str(yb) + "-" + str(ye))
    
    ax[0].text(yb, 11, "Période de référence", color = "white")
    ax[0].set_ylabel("°C")
    ax[0].set_title("Température annuelle moyenne à Uccle")
    ax[0].set_axisbelow(True)


    fig.tight_layout()
    fig.savefig("./figs/fig_" + str(y) + ".png")






