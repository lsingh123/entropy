#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 20:09:19 2019

@author: lavanyasingh
"""

from pcapng import FileScanner
from pcapng.blocks import EnhancedPacket
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
from ipwhois import IPWhois, exceptions
import os
from matplotlib import pyplot as plt

domain_owners = {}

def getDest(file):
    
    dest_ips = set()

    with open(file, "rb") as fp:
        scanner = FileScanner(fp)
        for block in scanner:
                
            if isinstance(block, EnhancedPacket):
                    
                decoded = Ether(block.packet_data)
                pl1 = decoded.payload
                if isinstance(pl1, IP):
                    dest_ips.add(pl1.dst)
    return dest_ips

def getOwners(dest_ips):
    owners = {}
    for ip in dest_ips:
        try:
            domain = IPWhois(ip)
            results = domain.lookup_rdap(depth=1, asn_methods=['dns', 'whois', 'http'])
            #print(results['asn_description'])
            owners.update({ip:results['asn_description']})
        except exceptions.IPDefinedError as ex:
            #owners.update({ip:ex})
            #print(ex)
            None
    return owners

def runAnalysis():
    files = os.listdir(os.getcwd() + "/data")
    owners = {}
    with open("results1.txt", "w") as f:
        for file in files:
            dest_ips = getDest("data/" + file)
            getOwners(dest_ips)
            owners.update({file: getOwners(dest_ips)})
            f.write(file + ": " + str(owners[file]) + "\n")
            print(file, owners[file])

def getDestIPS(file):
    dest_ips = []

    with open(file, "rb") as fp:
        scanner = FileScanner(fp)
        for block in scanner:
            
            if isinstance(block, EnhancedPacket):
                
                decoded = Ether(block.packet_data)
                #print(repr(Ether(block.packet_data))[:400] + '...')
                pl1 = decoded.payload
                if isinstance(pl1, IP):
                    dest_ips.append(pl1.dst)
    return dest_ips

    
def getDestOwners(file):
    dest_ips = getDestIPS(file)
    dest_set = set(dest_ips)
    owners = getOwners(dest_set)
    dest_owners = []
    for ip in dest_ips:
        try:
            dest_owners.append(owners[ip])
        except KeyError:
            None
    return dest_owners

def graphOwners(file):
    owners = getDestOwners("data/"+file)
    fig,ax = plt.subplots()
    time = [i for i in range(len(owners))]
    owners_small = [owner.split(" ")[0] for owner in owners]
    ax.scatter(time, owners_small, s=0.75)
    plt.title(file.split(".")[0], fontsize=15)
    plt.xlabel('Packet Number', fontsize=12)
    plt.ylabel('Destination Owner', fontsize = 12)
    plt.tight_layout()
    #plt.show()
    plt.savefig("graphs/"+file.split(".")[0]+".png", dpi=fig.dpi)

def graphAll():
    files = os.listdir(os.getcwd()+"/data")
    files.remove(".DS_Store")
    for file in files:
        try:
            graphOwners(file)
        except Exception as ex:
            print(ex)
            print(file)
            raise ex

if __name__ == '__main__':
    #runAnalysis()
    #print(matplotlib.matplotlib_fname())
    graphAll()