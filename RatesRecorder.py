import os
import itertools
import time
from selenium import webdriver
from collections import defaultdict
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


uber_fare_list = ["Base fare","Long pickup fee","Per-minute to pickup","Per-mile to pickup","Booking fee",
                  "Minimum fare","Per-minute","Per-mile","Cancellation fee","Rider no-show fee",'Standard rider-initiated cancellation fee','Per-minute prior to cancellation','Per-mile prior to cancellation','Number of riders']

uber_types = ['UberX','Pool','UberCab','Comfort','UberXL','Black','Black SUV','Select','Lux']


iterlist = list(itertools.product(uber_types, uber_fare_list))
temp = []
title = 'City,State,'
for idx, i in enumerate(iterlist):
    temp.append(i[0]+' '+i[1])
    title = title + i[0]+' '+i[1]
    if idx != len(iterlist) - 1:
            title = title + ', '
# print(title)


def read_city_list(mode=False):
    city_list = []
    with open('cities.csv','r') as f:
        text = f.read()
        line = text.splitlines()
        del line[0]
        for l in line:
            words = l.split(',')
            city = words[1] + ',' + words[2]
            if mode:
                city = city+',USA'
            city_list.append(city)
    return city_list


def get_fare_uber(city):
    start = city
    end = city
    driver = webdriver.Chrome('./chromedriver')
    try:
        driver.get("https://www.uber.com/in/en/price-estimate/")
        elem = driver.find_element_by_name("pickup")
        elem.send_keys(start)
        time.sleep(2)
        elem.send_keys(Keys.ENTER)
        elem = driver.find_element_by_name("destination")
        elem.send_keys(end)
        time.sleep(2)
        elem.send_keys(Keys.ENTER)
        time.sleep(2)
        driver.find_element_by_xpath("//*[contains(text(), 'All rides')]").click()
        xpath = "//div[@class='vo']//*[local-name()='svg']"
        svg = driver.find_elements_by_xpath(xpath)
        type_fare = defaultdict()
        del svg[-1]
        for s in svg:
            time.sleep(2)
            s.click()
            time.sleep(2)
            container = driver.find_element_by_xpath("//div[@role='dialog']")
            type = container.find_element_by_tag_name('h3').text
            spans = container.find_elements_by_tag_name('span')
            del spans[-1]
            for idx, s in enumerate(spans):
                if s.text in uber_fare_list:
                    type_fare[type + ' ' + s.text] = spans[(idx + 1)].text
            button = container.find_element_by_tag_name('button')
            button.click()
        type_fare = dict(type_fare)
        output = city+','
        for t in temp:
            output = output + type_fare.get(t, 'N/A') + ','
        print(output)
        driver.close()
        return None
    except Exception as err:
        return city


def get_fare_lyft(city):
    start = city
    end = city
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome('./chromedriver',options=chrome_options)
    try:
        driver.get("https://www.lyft.com/rider/fare-estimate#estimate")
        elem = driver.find_element_by_xpath("//input[@placeholder='Enter pick-up location']")
        elem.send_keys(start)
        time.sleep(0.5)
        elem.send_keys(Keys.ENTER)
        elem = driver.find_element_by_xpath("//input[@placeholder='Enter drop-off location']")
        elem.send_keys(end)
        time.sleep(0.5)
        elem.send_keys(Keys.ENTER)
        time.sleep(0.5)
        driver.find_element_by_xpath("//*[contains(text(), 'GET ESTIMATE') and @type='submit']").click()
        time.sleep(0.5)
        driver.find_element_by_xpath("//a[contains(text(), 'More')]").click()
        time.sleep(1)
        area = driver.find_elements_by_xpath("//div[@class='YlsZXe'][1]")
        target = area[0]
        output = city + ','
        for table in target.find_elements_by_class_name("_1V8sen"):
            output = output + table.find_element_by_tag_name('th').text+','
            for td in table.find_elements_by_tag_name('td'):
                output = output + td.text + ','
        print(output)
    except Exception as err:
        print(err)
        return city


if __name__ == '__main__':
    for c in read_city_list(True):
        get_fare_lyft(c)
