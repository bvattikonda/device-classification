#!/usr/bin/env python 
from collections import defaultdict

devices = {'Mobile Phone': ['iPhone', 'Android Phone', 'Windows Phone'],
    'PC': ['Generic', 'Laptop', 'Desktop'],
    'Tablet': ['iPad', 'Android Tablet'],
    'Movie Player': [],
    'Game Console': ['XBox', 'Wii', 'PlayStation'],
    'EBook Reader': ['Kindle', 'Nook'],
    'Mac': ['Macbook', 'iMac'],
    'Unknown': []}

def identify_device_by_domains(mac_to_domains):
    mac_to_device = defaultdict(str)
    for mac, domains in mac_to_domains.iteritems():
        if 'iphone-wu.apple.com' in domains:
            mac_to_device[mac] = 'iPhone'
        elif 'www.msftncsi.com' in domains:
            mac_to_device[mac] = 'PC'
        elif 'ncsi.glbdns.microsoft.com' in domains:
            mac_to_device[mac] = 'PC'
        elif 'm.youtube.com' in domains:
            mac_to_device[mac] = 'Mobile Phone'
        elif 'todo-g7g.amazon.com' in domains:
            mac_to_device[mac] = 'Kindle'
        elif 'atv-ext.amazon.com' in domains:
            mac_to_device[mac] = 'TV'
        elif 'android.clients.google.com' in domains:
            for domain in domains:
                if domain.startswith('mtalk'):
                    mac_to_device[mac] = 'Android Phone'
                    break 
                if domain.startswith('mobile'):
                    mac_to_device[mac] = 'Android Phone'
                    break 
        else:
            for domain in domains:
                if domain.endswith('m.wikipedia.org'):
                    mac_to_device[mac] = 'Mobile Phone'
                    break
                if domain.endswith('m.wikimedia.org'):
                    mac_to_device[mac] = 'Mobile Phone'
                    break
                if domain.startswith('m.'):
                    mac_to_device[mac] = 'Mobile Phone'
                    break
                if domain.startswith('mobile.'):
                    mac_to_device[mac] = 'Mobile Phone'
                    break
    return mac_to_device
