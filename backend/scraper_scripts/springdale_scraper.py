from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sqlite3
import time
import os, json
import datetime

from selenium.webdriver.common import options

db_path = os.path.expandvars("/home/oldmoldycake/Projects/nwa_calendar/backend/events.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
url = "https://www.downtownspringdale.org/events"

driver.get(url)
scrolls = 2
scrolls_pause_time = 2

for i in range(scrolls):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scrolls_pause_time)

time.sleep(2)

next_page_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next Events')]"))
        )
full_html = driver.page_source
soup = BeautifulSoup(full_html,'lxml')
current_page = 1

while current_page < 4:
    print(current_page)
    full_html = driver.page_source
    soup = BeautifulSoup(full_html,'lxml')

    content_containers = soup.find_all('div', class_="eapp-events-calendar-grid-item")
    
    for content in content_containers[:-2]:
        script_tag = content.find('script', type='application/ld+json')

        raw_json = script_tag.string

        event_json = json.loads(raw_json)

        event_link = "https://www.downtownspringdale.org/events"
        event_name = event_json['name']
        start_date = event_json['startDate']
        end_date = event_json['endDate']
        event_description = event_json['description']
        location = event_json['location']['address']['streetAddress']

        record_event_sql = f"""
        INSERT INTO events (event_link, event_title, event_description, location, datetime_start, datetime_end)
        VALUES(?,?,?,?,?,?)
        """

        insert_event_sql = (
                event_link,
                event_name,
                event_description,
                location,
                start_date,
                end_date if end_date is not None else start_date
                )
        cursor.execute(record_event_sql, insert_event_sql)
        conn.commit()

    driver.execute_script("arguments[0].click();", next_page_button)
    time.sleep(1)
    
    for i in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scrolls_pause_time)
    next_page_button = WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next Events')]"))
            )
    if next_page_button is None:
        print("Bailing")
        exit()
        
    current_page = current_page + 1
