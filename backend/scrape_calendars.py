from re import subn
import subprocess, sys
import sqlite3


try:
    conn = sqlite3.connect('events.db')

    cursor = conn.cursor()


    create_table_sql = """
    CREATE TABLE IF NOT EXISTS events ( 
        id INTEGER PRIMARY KEY,
        event_link TEXT,
        event_title TEXT,
        event_description TEXT,
        datetime TEXT,
        location TEXT
        )
        """

    cursor.execute(create_table_sql)

    drop_table_sql = "DELETE FROM events"

    cursor.execute(drop_table_sql)

    conn.commit()


    print("---Table prepared---")
except Exception as e:
    print(f"Failed to prepare database {e}")
    exit()


scrapers_to_run = [
        "/home/oldmoldycake/Projects/nwa_calendar/backend/scraper_scripts/fayetteville_scraper.py"
        ]


print("Starting scraper scripts---")
for scraper in scrapers_to_run:
    command = [sys.executable, scraper]

    try:
        subprocess.run(command)
        print(f"{command} has run sucessfully!")
    except Exception as e:
        print(f"Failed to run scraper {command}: {e}")

    


