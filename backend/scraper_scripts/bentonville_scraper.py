from dateutil.relativedelta import relativedelta
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os
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
while len(event_links) < 12:
    page_events_tags = soup.find_all('div', class_="item")
    for page_event_tag in page_events_tags:
        header_tag = page_event_tag.find('h4')

        if header_tag is None:
            continue
        header_link_tag = header_tag.find('a')
        header_link = "https://visitbentonville.com" + str(header_link_tag.get("href"))
        event_links.append(header_link) 
    next_page_url = f"https://www.visitbentonville.com/events/?skip={len(event_links)}&bounds=false&view=list&sort=date&filter_daterange%5Bstart%5D={todays_date}&filter_daterange%5Bend%5D={formatted_one_year_date}"
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(next_page_url)
    time.sleep(1)
    full_html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(full_html, 'lxml')


for event_link in event_links:
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(event_link)
    time.sleep(1)
    full_html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(full_html, 'lxml')
    
    #Get Description
    description_container_tag = soup.find('div', class_="core-styles")
    description = description_container_tag.get_text(strip=True)
      
    
    info_container = soup.find('div', class_='info-section')
    
    header = info_container.find('h1')
    event_title = header.get_text(strip=True)
    
    #Gate dates
    date_info = soup.find('dl', class_ = "priority-info")
    date_label = date_info.find('dt', string='Dates:')
    date_text = date_label.find_next_sibling('dd').get_text(strip=True)
    dates = date_text.split(' - ')

    if len(dates) == 2:
        start_date, end_date = dates
    else:
        start_date, end_date = [dates, None]

    date_fornmat ="%B %d, %Y"

    formatted_start_date = datetime.datetime.strptime(start_date.strip(), date_fornmat)
    formatted_end_date = datetime.datetime.strptime(end_date.strip(), date_fornmat)
    
    formatted_start_date = formatted_start_date.strftime("%Y-%m-%d")
    formatted_end_date = formatted_end_date.strftime("%Y-%m-%d")
   
    #Get the location
    location_container = soup.find('div', class_="two-line-wrap")
    location_tags = location_container.find_all('span')
    
    location = location_tags[0].get_text() + " " + location_tags[1].get_text()
    
    record_event_sql = f"""
    INSERT INTO events (event_link, event_title, event_description, location, datetime_start, datetime_end
    VALUES(?,?,?,?,?,?)
    """

    insert_event_sql = (
            event_link,
            event_title,
            description,
            location,
            start_date,
            end_date if end_date is not None else start_date
            )
    cursor.execute(record_event_sql, insert_event_sql)
    conn.commit()
            
     
    

    

    print("\n\n")





