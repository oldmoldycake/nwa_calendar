import os, datetime
from re import PatternError
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
print(f"Total Pages: {total_pages}")
current_page = 0  

event_links = []
while current_page < total_pages:
    event_link_tags = soup.find_all('a', class_="button right")
    
    for event_link_tag in event_link_tags:
        event_link = event_link_tag.get('href')
        event_links.append(event_link)
    driver.execute_script("arguments[0].click();", next_page_button)
    time.sleep(1)
    full_html = driver.page_source
    soup = BeautifulSoup(full_html, 'lxml')

        
    current_page = current_page + 1
driver.quit()

for event_link in event_links:
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(event_link)
    time.sleep(1)
    full_html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(full_html,'lxml')

    event_title = soup.find('h1')
    event_title = event_title.get_text()
    print(event_title)
    
    description_container = soup.find_all('p')
    description_text = description_container[4].get_text()

    location_date_container = soup.find('div', class_="profile-info-block")
    location_date_container = location_date_container.find_all('div', class_="col link")
    

    date = location_date_container[0].get_text()
    input_format = "%A, %b %d, %Y, %I:%M %p"
    date_object = datetime.datetime.strptime(date, input_format)
    output_format = "%Y-%m-%d"
    date = date_object.strftime(output_format)
    location = location_date_container[1].get_text()
     
    record_event_sql = f"""
    INSERT INTO events (event_link, event_title, event_description, location, datetime_start, datetime_end)
    VALUES(?,?,?,?,?,?)
    """

    insert_event_sql = (
        event_link,
        event_title,
        description_text,
        location,
        date,
        date
            )

    cursor.execute(record_event_sql, insert_event_sql)
    conn.commit()

    break

