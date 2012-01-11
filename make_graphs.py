#!/usr/bin/env python

# Script to make graphs for the devices that are being classified.

from datetime import datetime
from collections import defaultdict
import os
import sys
import argparse
import matplotlib.font_manager
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import ScalarFormatter
from graph_functions import *
import psycopg2

# Figure dimensions
fig_width = 5
fig_length = 2.25

MARKERS = ['b-+', 'g-x', 'c-s', 'm-^', 'y->', 'r-p']
MARKEVERY = 10 
LEGEND_PROP = matplotlib.font_manager.FontProperties(size=9)
TITLE_PROP = matplotlib.font_manager.FontProperties(size=9)
LABEL_PROP = matplotlib.font_manager.FontProperties(size=9)

matplotlib.rcParams['axes.labelsize'] = 10
matplotlib.rcParams['xtick.labelsize'] = 10
matplotlib.rcParams['ytick.labelsize'] = 10

# Can be used to adjust the border and spacing of the figure
fig_left = 0.15
fig_right = 0.91
fig_bottom = 0.17
fig_top = 0.90
fig_hspace = 0.5

###############################################################################
# Configuration parameters end here
###############################################################################

def create_figure():
    fig = Figure()
    fig.set_size_inches(fig_width, fig_length, forward=True)
    Figure.subplots_adjust(fig, left = fig_left, right = fig_right, bottom = fig_bottom, top = fig_top, hspace = fig_hspace)
    return fig

def print_figure(fig, destination_directory, filename, extension):
    canvas = FigureCanvasAgg(fig)
    if extension == '.png':
        canvas.print_figure(os.path.join(destination_directory, \
            filename + extension), dpi = 110)
    elif extension == '.eps':
        canvas.print_eps(os.path.join(destination_directory,\
            filename + extension), dpi = 110)

# return the number of days for which each device has been seen
def get_dates_data():
    conn = psycopg2.connect(user = 'bvattikonda', database =\
        'bismark_openwrt_live_v0_1', host = '/tmp', port = '5434')
    cur = conn.cursor()
    cur.execute('SET search_path to bismark_passive')
    cur.execute('SELECT mac_address, eventstamp, bytes_transferred FROM\
        bytes_per_device_per_day_memoized')
    values = cur.fetchall()
    device_visibility = defaultdict(set)
    for mac, timestamp, bytes_transferred in values:
        if mac == 'unknown':
            continue
        if bytes_transferred > 0:
            device_visibility[mac].add(datetime.date(timestamp))

    return [len(device_visibility[mac]) for mac in device_visibility]

# return the number of devices which have been seen for certain number of days
def get_device_duration():
    conn = psycopg2.connect(user = 'bvattikonda', database =\
        'bismark_openwrt_live_v0_1', host = '/tmp', port = '5434')
    cur = conn.cursor()
    cur.execute('SET search_path to bismark_passive')
    cur.execute('SELECT mac_address, eventstamp, bytes_transferred FROM\
        bytes_per_device_per_day_memoized')
    values = cur.fetchall()
    device_visibility = defaultdict(set)
    for mac, timestamp, bytes_transferred in values:
        if mac == 'unknown':
            continue
        if bytes_transferred > 0:
            device_visibility[mac].add(datetime.date(timestamp))
    duration_to_devices = defaultdict(int)
    max_duration = 0
    for mac, dates in device_visibility.iteritems():
        duration_to_devices[len(dates)] += 1
        if len(dates) > max_duration:
            max_duration = len(dates)

    for duration in reversed(xrange(2, max_duration + 1)):
        duration_to_devices[duration - 1] += duration_to_devices[duration]

    return xrange(1, max_duration + 1), [duration_to_devices[days]\
        for days in xrange(1, max_duration + 1)]

# return the number of devices which have been seen for atleast a certain number
# of days and have accessed the DNS
def get_dns_device_duration():
    conn = psycopg2.connect(user = 'bvattikonda', database =\
        'bismark_openwrt_live_v0_1', host = '/tmp', port = '5434')
    cur = conn.cursor()
    cur.execute('SET search_path to bismark_passive')
    cur.execute('SELECT mac_address, eventstamp, bytes_transferred FROM\
        bytes_per_device_per_day_memoized')
    values = cur.fetchall()
    device_visibility = defaultdict(set)
    for mac, timestamp, bytes_transferred in values:
        if mac == 'unknown':
            continue
        if bytes_transferred > 0:
            cur.execute("SELECT mac_address, domain from domains_accessed\
                where mac_address = '%s'" % mac)
            dns_access_values = cur.fetchall()
            if len(dns_access_values):
                device_visibility[mac].add(datetime.date(timestamp))
    
    duration_to_devices = defaultdict(int)
    max_duration = 0
    for mac, dates in device_visibility.iteritems():
        duration_to_devices[len(dates)] += 1
        if len(dates) > max_duration:
            max_duration = len(dates)

    for duration in reversed(xrange(2, max_duration + 1)):
        duration_to_devices[duration - 1] += duration_to_devices[duration]

    return xrange(1, max_duration + 1), [duration_to_devices[days]\
        for days in xrange(1, max_duration + 1)]

# return the average number of hours a device has been seen
def get_visibility_time():
    conn = psycopg2.connect(user = 'bvattikonda', database =\
        'bismark_openwrt_live_v0_1', host = '/tmp', port = '5434')
    cur = conn.cursor()
    cur.execute('SET search_path to bismark_passive')
    cur.execute('SELECT mac_address, eventstamp, bytes_transferred FROM\
        bytes_per_device_per_hour_memoized')
    values = cur.fetchall()
    visibility_time = defaultdict(lambda: defaultdict(set))
    for mac_address, timestamp, bytes_transferred in values:
        if mac_address == 'unknown':
            continue
        visibility_time[mac_address][datetime.date(timestamp)].add(\
            timestamp.replace(minute = 0, second = 0, microsecond = 0))
    avg_visibility = defaultdict(float)
    for mac_address in visibility_time:
        if len(visibility_time[mac_address]) > 1:
            avg_visibility[mac_address] = sum([len(hours) for day, hours in\
                visibility_time[mac_address].iteritems()]) /\
                float(len(visibility_time[mac_address]))

    return [avg_visibility[mac_address] for mac_address in avg_visibility]

def main():
    parser = argparse.ArgumentParser(description = 'Generate graphs')
    parser.add_argument('--extension', default = '.png',\
        help = 'File format in which graphs are wanted (eps or png)')
    parser.add_argument('--destination', required = True, dest =\
        'destination_dir', help = 'Directory to which graphs should be saved')
    args = parser.parse_args()

    print 'Graph for days of visibility each device'
    fig = create_figure()
    subplot = fig.add_subplot(1, 1, 1)
    plot_data = get_dates_data()
    plot_cdf(subplot, plot_data)
    subplot.set_xlabel('Number of days', fontproperties = LABEL_PROP)
    subplot.set_ylabel('CDF', fontproperties = LABEL_PROP)
    subplot.set_title('Device visibility', fontproperties = TITLE_PROP)
    subplot.set_ylim(ymin = 0)
    print_figure(fig, args.destination_dir, 'device_visibility', args.extension)

    print 'Graph for number of devices with different visibility'
    fig = create_figure()
    subplot = fig.add_subplot(1, 1, 1)
    xlist, ylist = get_device_duration()
    xlist_dns, ylist_dns = get_dns_device_duration()
    subplot.plot(xlist, ylist, label = 'All', marker = '+',\
        markevery = MARKEVERY)
    subplot.plot(xlist_dns, ylist_dns, label = 'DNS user', marker = '^',\
        markevery = MARKEVERY)
    subplot.set_xlabel('Number of days', fontproperties = LABEL_PROP)
    subplot.set_ylabel('Number of devices', fontproperties = LABEL_PROP)
    subplot.set_title('Device visibility', fontproperties = TITLE_PROP)
    subplot.legend(prop = LEGEND_PROP)
    subplot.set_ylim(ymin = 0)
    print_figure(fig, args.destination_dir, 'devices_vs_duration',\
        args.extension)

    print 'Graph for average duration of visibility each day'
    fig = create_figure()
    subplot = fig.add_subplot(1, 1, 1)
    plot_data = get_visibility_time()
    plot_cdf(subplot, plot_data)
    subplot.set_xlabel('Number of hours a day', fontproperties = LABEL_PROP) 
    subplot.set_ylabel('CDF', fontproperties = LABEL_PROP)
    subplot.set_title('Avg. duration of visibility', fontproperties =
    TITLE_PROP)
    subplot.set_ylim(ymin = 0)
    print_figure(fig, args.destination_dir, 'visibility_duration',\
        args.extension)

if __name__ == '__main__':
    main()
