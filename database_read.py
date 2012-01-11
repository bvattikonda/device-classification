#!/usr/bin/env python

import psycopg2
from datetime import datetime
from collections import defaultdict

class BismarkPassivePostgresDatabase(object):
    def __init__(self, user, password, host, port, database):
        self._conn = psycopg2.connect(user=user, 
                                      password = password,
                                      host = host,
                                      port = port,
                                      database=database,
                                      sslmode = 'allow')
        cur = self._conn.cursor()  
        cur.execute('SET search_path TO bismark_passive')
        cur.close()
        self._conn.commit()
    
    def export_mac_to_bismark_id(self):
        cur = self._conn.cursor()
        cur.execute('SELECT DISTINCT mac_address, node_id from \
            bytes_per_device_per_minute')
        values = cur.fetchall()
        mac_to_bismark_id = defaultdict(str)
        for mac_address, node_id in values:
            mac_to_bismark_id[mac_address] = node_id
        return mac_to_bismark_id 

    def export_device_visibility(self):
        cur = self._conn.cursor()
        cur.execute('SELECT mac_address, eventstamp, bytes_transferred FROM\
            bytes_per_device_per_day_memoized')
        values = cur.fetchall()
        device_visibility = defaultdict(set)
        for mac, timestamp, bytes_transferred in values:
            if mac == 'unknown':
                continue
            if bytes_transferred > 0:
                device_visibility[mac].add(datetime.date(timestamp))
        return device_visibility

    def export_mac_to_domains(self, devices_of_interest):
        ''' For each device, retun the set of domains that the device has
        visited'''
        device_to_domains = defaultdict(set)    
        cur = self._conn.cursor()
        for device in devices_of_interest:
            cur.execute("SELECT mac_address, domain FROM domains_accessed\
                where mac_address = '%s'" % device)
            data = cur.fetchall()
            for mac_address, domain in data:
                device_to_domains[mac_address].add(domain)

        return device_to_domains
