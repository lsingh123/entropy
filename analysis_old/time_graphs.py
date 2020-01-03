#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 09:49:16 2019

@author: lavanyasingh
"""

from pcapng import FileScanner
from pcapng.blocks import EnhancedPacket
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
from ipwhois import IPWhois, exceptions
import os
from matplotlib import pyplot as plt
#import whois

class Grapher:
    
    def __init__(self):
        self.domains = {}
    
    def getDest(self, file):
        dest_ips = []
    
        with open(file, "rb") as fp:
            scanner = FileScanner(fp)
            for block in scanner:
                    
                if isinstance(block, EnhancedPacket):
                        
                    decoded = Ether(block.packet_data)
                    pl1 = decoded.payload
                    if isinstance(pl1, IP):
                        dest_ips.append(pl1.dst)
        return dest_ips
        
    def getOwners(self, dest_ips):
        for ip in dest_ips:
            if ip not in self.domains:
                try:
                    domain = IPWhois(ip)
                    results = domain.lookup_rdap(depth=1, asn_methods=['dns', 'whois', 'http'], bootstrap = False, retry_count = 1)
                    self.domains.update({ip:results['asn_description']})
                except (exceptions.IPDefinedError) as ex:
                    self.domains.update({ip:None})
                    print(ex, ip)
        
    def getDestOwners(self, file):
        dest_ips = self.getDest(file)
        self.getOwners(dest_ips)
        dest_owners = []
        for ip in dest_ips:
            if ip in self.domains and self.domains[ip] != None:
                dest_owners.append(self.domains[ip])
        return dest_owners
    
    def graphOwners(self, file):
        owners = self.getDestOwners("data/"+file)
        fig,ax = plt.subplots()
        time = [i for i in range(len(owners))]
        print(owners)
        owners_small = [owner.split(" ")[0] for owner in owners]
        ax.scatter(time, owners_small, s=0.75)
        plt.title(file.split(".")[0], fontsize=15)
        plt.xlabel('Packet Number', fontsize=12)
        plt.ylabel('Destination Owner', fontsize = 12)
        plt.tight_layout()
        plt.show()
        #plt.savefig("graphs/"+file.split(".")[0]+".png", dpi=fig.dpi)
        plt.close(fig = fig)
    
    def graphAll(self):
        files = os.listdir(os.getcwd()+"/data")
        files.remove(".DS_Store")
        for file in files:
            #if file.replace(".pcapng", ".png") not in os.listdir(os.getcwd() + "/graphs"):
            if file == ("iphoneforgeahead1.pcapng"):
                print(file)
                try:
                    self.graphOwners(file)
                except Exception as ex:
                    print(ex, file)
                    raise ex

if __name__ == '__main__':
    #grapher = Grapher()
    #grapher.graphAll()
    print(len({'AMAZON-02 - Amazon.com, Inc., US', 'AS-CRITEO - Criteo Corp., US', 'COGECO-PEER1 - Cogeco Peer 1, CA', 'CMCS - Comcast Cable Communications, LLC, US', 'DOUBLE-VERIFY - DoubleVerify, Inc., US', 'AS-CHOOPA - Choopa, LLC, US', 'HIGHWINDS2 - Highwinds Network Group, Inc., US', 'HIGHWINDS3 - Highwinds Network Group, Inc., US', 'MICROSOFT-CORP-MSN-AS-BLOCK - Microsoft Corporation, US', 'FASTLY - Fastly, US', 'SOFTLAYER - SoftLayer Technologies Inc., US', 'FACEBOOK - Facebook, Inc., US', 'CNNIC-ALIBABA-US-NET-AP Alibaba (US) Technology Co., Ltd., CN', 'GOOGLE - Google LLC, US', 'TAOBAO Zhejiang Taobao Network Co.,Ltd, CN', 'CLOUDFLARENET - Cloudflare, Inc., US', 'AKAMAI-AS - Akamai Technologies, Inc., US', 'APPLE-ENGINEERING - Apple Inc., US', 'EDGECAST - MCI Communications Services, Inc. d/b/a Verizon Business, US', 'AMAZON-AES - Amazon.com, Inc., US'}
))