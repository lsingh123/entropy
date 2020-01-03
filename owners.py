#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 11:44:11 2019

@author: lavanyasingh
"""

from pcapng import FileScanner
from pcapng.blocks import EnhancedPacket
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
from ipwhois import IPWhois, exceptions
import os
import csv

class Cacher:
    
    def __init__(self, outfile="owners.csv", sources=['192.168.2.4', '192.168.2.3']):
        self.domains = {}
        self.outfile=outfile
        self.sources = sources
    
    # extract the destination ip address from a wireshark dump
    def getDest(self, file):
        dest_ips = []
    
        with open(file, "rb") as fp:
            scanner = FileScanner(fp)
            for block in scanner:
                    
                if isinstance(block, EnhancedPacket):
                        
                    decoded = Ether(block.packet_data)
                    pl1 = decoded.payload
                    if isinstance(pl1, IP) and pl1.src in self.sources:
                        dest_ips.append(pl1.dst)
        return dest_ips
    
    # lookup owner if not present in self.domains
    def getOwners(self, dest_ips):
        count = 0
        for ip in dest_ips:
            if ip not in self.domains:
                count += 1
                print(count)
                try:
                    domain = IPWhois(ip)
                    results = domain.lookup_rdap(depth=1, asn_methods=['dns', 'whois', 'http'], bootstrap = False, retry_count = 1)
                    self.domains.update({ip:results['asn_description']})
                except (exceptions.IPDefinedError) as ex:
                    self.domains.update({ip:None})
                    print(ex, ip)
    
    # write owners to self.outfile
    def cache_owners(self):
        with open(self.outfile, "w") as outf:
            w = csv.writer(outf, delimiter= ',', quotechar = '"', 
                           quoting = csv.QUOTE_MINIMAL)
            for domain in self.domains:
                w.writerow([domain, self.domains[domain]])

    def main(self):
        files = os.listdir(os.getcwd()+"/data")
        files.remove(".DS_Store")
        for file in files:
            try:
                self.getOwners(self.getDest("data/"+file))
            except Exception as ex:
                print(ex, file)
        self.cache_owners()

if __name__ == '__main__':
    cacher = Cacher()
    cacher.main()
        
    