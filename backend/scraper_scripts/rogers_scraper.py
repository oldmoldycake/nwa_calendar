import os
import sqlite3
from warnings import warn
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os

from selenium.webdriver.common import options

db_path = os.path.expandvars("/home/oldmoldycake/Projects/nwa_calendar/backend/events.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
url = "https://www.destinationrogers.com/things-to-do-rogers/events-rogers/"

driver.get(url)
time.sleep(2)
full_html = driver.page_source

soup = BeautifulSoup(full_html, 'lxml')

next_page_button = driver.find_element(By.ID, "next-page")
total_page_tag = soup.find('div', id="total-pages")
total_pages = int(total_page_tag.get_text(strip = True))
current_page = 1

event_links = []
while current_page < total_pages:
    event_link_tags = soup.find_all('a', class_="button right")
    
    for event_link_tag in event_link_tags:
        event_link = event_link_tag.get('href')
        print(event_link)
        event_links.append(event_link)
    driver.execute_script("arguments[0].click();", next_page_button)
    time.sleep(1)
    full_html = driver.page_source
    soup = BeautifulSoup(full_html, 'lxml')

        
    total_pages = total_pages + 1
