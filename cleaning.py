#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 13:41:52 2019

@author: lavanyasingh
"""

import pandas as pd
from pcapng import FileScanner
from pcapng.blocks import EnhancedPacket
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
import os
import csv

def parse_summary(summary):
    return summary.split(" ")[3]

def get_device(source):
    if source == '192.168.2.4':
        return 'ios'
    if source == '192.168.2.3':
        return 'android'
    return ''

def get_dest():
    destinations = {}
    with open("owners.csv", "r") as inf:
        reader = csv.reader(inf, delimiter=',', quotechar = '"')
        for row in reader:
            destinations.update({row[0]: row[1]})
    return destinations
        
def get_app(filename):
    start = filename.find("nexus")
    if start == -1:
        start = filename.find("iphone") + 6
    else:
        start += 5
    return filename[start:filename.find(".")-1]

def extract_data(file):
    
    destinations = get_dest()
    
    
    with open(file, "rb") as fp, open("parsed.csv", "a") as outf:
        app = get_app(file)
        w = csv.writer(outf, delimiter= ',', quotechar = '"', 
                           quoting = csv.QUOTE_MINIMAL)
        
        scanner = FileScanner(fp)
        for block in scanner:
                    
            if isinstance(block, EnhancedPacket):
                        
                decoded = Ether(block.packet_data)
                pl1 = decoded.payload
                
                if isinstance(pl1, IP):
                    # for some reason I get a scapy library error unless I break
                    # this if statement into two separate ones - wtf
                    if pl1.src == '192.168.2.4' or pl1.src == '192.168.2.3':
                        data = [pl1.src, pl1.dst, destinations[pl1.dst], 
                                  parse_summary(pl1.mysummary()), get_device(pl1.src),
                                  pl1.len, app]
                        w.writerow(data)

def write_data():
    files = os.listdir(os.getcwd()+"/data")
    files.remove(".DS_Store")
    with open("parsed.csv", "w") as outf:
        w = csv.writer(outf, delimiter= ',', quotechar = '"', 
                           quoting = csv.QUOTE_MINIMAL)
        w.writerow(["source", "dest_ip", "dest_owner", "type", "operating system", "length", "app"])
    for file in files:
        print(file)
        extractData("data/" + file)
    

