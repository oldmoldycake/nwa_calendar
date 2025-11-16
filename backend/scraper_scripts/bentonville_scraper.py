from dateutil.relativedelta import relativedelta
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os
import datetime


db_path = os.path.expandvars("/home/oldmoldycake/Projects/nwa_calendar/backend/events.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


driver = webdriver.Chrome(options=chrome_options)

todays_date = datetime.datetime.today().date()
formatted_date = todays_date.strftime('%Y-%m-%d')

one_year_date = todays_date + relativedelta(years=1)
formatted_one_year_date = one_year_date.strftime('%Y-%m-%d')

url = f"https://www.visitbentonville.com/events/?bounds=false&view=list&sort=date&filter_daterange%5Bstart%5D={todays_date}&filter_daterange%5Bend%5D={formatted_one_year_date}"
driver.get(url)
time.sleep(1)
full_html = driver.page_source
driver.quit()
soup = BeautifulSoup(full_html, 'lxml')


events_of_total = soup.find_all('li', class_="info")
events_of_total = events_of_total[0].get_text(strip = True)
parts = events_of_total.split(' of ')

total_events = parts[1]

event_links = []
count = 0
while len(event_links) < int(total_events):
    page_events_tags = soup.find_all('div', class_="item")
    for page_event_tag in page_events_tags:
        header_tag = page_event_tag.find('h4')

        if header_tag is None:
            continue
        header_link_tag = header_tag.find('a')
        header_link = "https://visitbentonville.com" + str(header_link_tag.get("href"))
        event_links.append(header_link) 
        print(header_link) 
    next_page_url = f"https://www.visitbentonville.com/events/?skip={len(event_links)}&bounds=false&view=list&sort=date&filter_daterange%5Bstart%5D={todays_date}&filter_daterange%5Bend%5D={formatted_one_year_date}"
    print(next_page_url)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(next_page_url)
    time.sleep(1)
    full_html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(full_html, 'lxml')


