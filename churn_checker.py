#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 10:57:33 2020

@author: lavanyasingh
"""

from bs4 import BeautifulSoup
import csv
from selenium import webdriver
import pandas as pd

URL_IOS = "https://sensortower.com/ios/rankings/top/iphone/us/"
CATEGORIES_IOS = ["games", "social-networking", "shopping", "lifestyle", "finance", "kids"]

URL_ANDROID = "https://sensortower.com/android/rankings/top/mobile/us/"
CATEGORIES_ANDROID = ["dating", "game", "lifestyle", "social", "shopping", "finance", "family"]

DATES = ["2020-01-04", "2019-12-27"]

def get_soup(url):
    driver = webdriver.Chrome()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    return soup

# get a list of 50 apps for a given URL
def get_apps(url):
    soup = get_soup(url)
    names = []
    table = soup.find("table", attrs={"class":"rankings-table table"})
    rows = table.find('tbody', attrs={"class":"rankings-app-body"}).find_all('tr')
    for row in rows:
        app = row.find_all(lambda tag: tag.name == 'td')[3]
        name = app.find('section', attrs={"class":"app-info"}).find("a", attrs={"class":"name"}).text
        names.append(name)
    return names

def write_data(categories, base_url, os):
    with open("rankings.csv", "a") as outf:
        w = csv.writer(outf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for date in DATES:
            for category in categories:
                url = base_url + category + "?date=" + date
                apps = get_apps(url)
                count = 0
                for app in apps:
                    print(app)
                    count += 1
                    w.writerow([date, category, app, count, os])

def get_dataframe():
    results = {"date":[], "category":[], "app":[], "ranking":[], "os":[]}
    with open("rankings.csv", "r", errors='ignore') as inf:
        reader = csv.reader(inf, delimiter=',', quotechar = '"')
        for line in reader:
            results["date"].append(line[0])
            results["category"].append(line[1])
            results["app"].append(line[2])
            results["ranking"].append(int((int(line[3]) + 1)/2))   # i messed up the ranking numbers lol
            results["os"].append(line[4])
    return pd.DataFrame.from_dict(results)

def get_overlaps():
    apps = get_dataframe()
    categories = {"games":"game", "game":"game", "social-networking":"social", 
                  "social":"social", "dating":"lifestyle", "lifestyle":"lifestyle", 
                  "shopping":"shopping", "finance":"finance", "kids":"kids", "family":"kids"}
    apps["category"] = [categories[category] for category in apps.category]
    cat_dict = {category:None for category in apps.category.unique()}
    for category in cat_dict:
        date1 = set(apps[apps.category == category][apps.date == '1/4/20'].app)
        date2 = set(apps[apps.category == category][apps.date == '12/27/19'].app)
        total = len(apps[apps.category == category][apps.date == '1/4/20'])
        cat_dict[category] = len(list(date1 & date2))/total*100
    overlaps = pd.DataFrame(sorted(cat_dict.items(), key=lambda x: x[1], reverse=True), 
                            columns=["Category", "Overlap %"])
    print(overlaps)

apps = get_dataframe()
categories = {"games":"game", "game":"game", "social-networking":"social", 
                  "social":"social", "dating":"lifestyle", "lifestyle":"lifestyle", 
                  "shopping":"shopping", "finance":"finance", "kids":"kids", "family":"kids"}
apps["category"] = [categories[category] for category in apps.category]
print(apps[apps.category=="shopping"].app)
    