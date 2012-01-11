#!/usr/bin/env python

import os 
import sys 
import argparse
import re
from collections import defaultdict
from database_read import *
from domains_to_device import *

# return a dictionary mapping '-' separated OUI in hex to manufacturer
def get_oui_information(filename):
    oui_to_manufacturer = defaultdict(str)
    fileHandle = open(filename, 'r')
    for line in fileHandle:
        if '(hex)' in line:
            splitline = line.split(None, 2)
            oui = splitline[0].strip().lower()
            manufacturer = splitline[2].strip()
            oui_to_manufacturer[oui] = manufacturer
    return oui_to_manufacturer 

def identify_devices_of_interest(device_visibility, num_days):
    devices_of_interest = set()
    for mac_address, dates in device_visibility.iteritems():
        if len(dates) > num_days:
            devices_of_interest.add(mac_address)
    return devices_of_interest 

def get_args():
    parser = argparse.ArgumentParser(description = 'Classify devices')
    parser.add_argument('--oui_filename', required = True,\
        dest = 'oui_filename',\
        help = 'IEEE oui database, can be found at\
        http://standards.ieee.org/develop/regauth/oui/oui.txt')
    parser.add_argument('--top',\
        dest = 'topsites',\
        help = 'Alexa CSV file with the top sites')
    parser.add_argument('--database',\
        default = 'bismark_openwrt_live_v0_1',\
        help = 'Name of database')
    parser.add_argument('--host',\
        default = '/tmp',\
        help = 'Database host')
    parser.add_argument('--port',\
        default = 5434,\
        help = 'Database port')
    parser.add_argument('--user',\
        default = 'bvattikonda',\
        help = 'Database user')
    parser.add_argument('--password',\
        default = '',\
        help = 'Database password')
    return parser.parse_args()

def main():
    args = get_args()
    oui_to_manufacturer = get_oui_information(args.oui_filename)
    # Connect to the database
    database = BismarkPassivePostgresDatabase(args.user, args.password,\
        args.host, args.port, args.database)
    # Identify the dates on which each device has been seen
    device_visibility = database.export_device_visibility() 
    # Identify devices which have been around for more than 'days'
    devices_of_interest = identify_devices_of_interest(device_visibility, 1)
    print len(devices_of_interest)
    # Identify the domains the devices visited
    mac_to_domains = database.export_mac_to_domains(devices_of_interest)
    print len(mac_to_domains)
    # Classify the device based on domain information
    mac_to_device = identify_device_by_domains(mac_to_domains)
    print len(mac_to_device)
    # Identify the bismark router to which the device is connected
    mac_to_bismark_id = database.export_mac_to_bismark_id()
    
    f = open('temp.txt', 'w')
    for mac, domains in mac_to_domains.iteritems():
        if mac not in mac_to_device:
            print >>f, mac, domains, '\n'
     
    sys.exit(1)
    top_file = open(args.topsites, 'r')
    top_sites = list()
    for line in top_file:
        domain = line.strip().split(',')[1]
        top_sites.append((domain, re.compile(r'(^|\.)%s$' % domain)))


    f = open('temp.txt', 'w')
    for mac, domains in mac_to_domains.iteritems():
        if mac not in mac_to_device:
            print >>f, mac, len(domains),
            print_domains = set()
            for fulldomain in domains:
                for domain, pattern in top_sites:
                    if pattern.search(fulldomain):
                        print_domains.add(domain)
            print >>f, print_domains, '\n'
             
if __name__ == '__main__':
    main()
