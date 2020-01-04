#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 10:57:33 2020

@author: lavanyasingh
"""

from bs4 import BeautifulSoup
import csv
from selenium import webdriver

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
                    count += 1

if __name__ == '__main__':
    with open("results.csv", "a") as outf:
        w = csv.writer(outf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow(['date', 'category', 'app', 'position', 'os'])
    write_data(CATEGORIES_IOS, URL_IOS, "ios")
    write_data(CATEGORIES_ANDROID, URL_ANDROID, "android")
    