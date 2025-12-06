import sqlite3
from warnings import warn
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os

db_path = os.path.expandvars("/home/oldmoldycake/Projects/nwa_calendar/backend/events.db")
conn = sqlite3.connect(db_path)

cursor = conn.cursor()




chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

url = "https://vibemap.com/events?cities=fayetteville"
print(url)

driver.get(url)
print("Fetched URL")

scrolls = 2
scroll_pause_time = 2


for i in range(scrolls):
    print(f"Processing scroll {i + 1} of {scrolls + 1}") 
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

full_html = driver.page_source

driver.quit()

   
soup = BeautifulSoup(full_html, 'lxml')




event_links = soup.find_all('a', class_="sing-card-inner") 

for event_link in event_links:
    event_link = "https://vibemap.com" + str(event_link.get("href"))
    print(event_link)  
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(event_link)
    print(f"Processing URL: {event_link}")
    time.sleep(3)

    full_html = driver.page_source
    driver.quit()
   
    soup = BeautifulSoup(full_html, 'lxml')
    title_tag = soup.find('h1')  
    
    #Get title
    if title_tag:
        title_text = title_tag.get_text(strip=True)
    else:
        title_text = "No Title Available"
        print("No header tag found")

    #Fetch the events description
    description_container = soup.find('div', class_="description")
    description_text = description_container.get_text(strip=True)

    if description_text is None:
        description_text = "Description not provided"

    #Get location and date
    location_details = soup.find('div', class_="location-details")
    location_fields = location_details.find_all('span', class_='text')
    
    event_date = location_fields[0].get_text()
    event_locantion = location_fields[1].get_text() 

    record_event_sql = f"""
    INSERT INTO events (event_link, event_title, event_description, location, datetime)
    VALUES (?,?,?,?,?) 
    """
    
    record_event_inserts = (
            event_link,
            title_text,
            description_text,
            event_locantion,
            event_date
        )
    cursor.execute(record_event_sql, record_event_inserts)
    conn.commit()

    driver.quit()
