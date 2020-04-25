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
    with open("owners2.csv", "r") as inf:
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
    return filename[start:filename.find(".")]

def load_categories():
    with open("sampling_2.csv", "r", ) as inf:
        reader = csv.reader(inf)
        next(reader)
        
        categories = {}
        
        for line in reader:
            categories.update({get_app(line[0]) + "2":line[4].replace(" ", "").lower()})  
    return categories
    
def extract_data(file):
                     
    
    destinations = get_dest()
    categories = load_categories()
    
    with open(file, "rb") as fp, open("parsed_2.csv", "a") as outf:
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
                    if pl1.src == '192.168.2.4':
                        data = [pl1.src, pl1.dst, destinations[pl1.dst], 
                                  parse_summary(pl1.mysummary()), get_device(pl1.src),
                                  pl1.len, app, categories[app]]
                        w.writerow(data)

def write_data():
    
    load_categories()
    files = os.listdir(os.getcwd()+"/data/round2")
    with open("parsed_2.csv", "w") as outf:
        w = csv.writer(outf, delimiter= ',', quotechar = '"', 
                           quoting = csv.QUOTE_MINIMAL)
        w.writerow(["source", "dest_ip", "dest_owner", "type", "operating system", "length", "app", "category"])
    for file in files:
        print(file)
        extract_data("data/round2/" + file)
        

if __name__ == '__main__':
    write_data()
