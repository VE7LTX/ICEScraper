# Importing tools for our adventure
import requests  # Like a magic spell to talk to websites
from bs4 import BeautifulSoup  # A magnifying glass to look closely at website pages
import sqlite3  # A tool to create and use our diary (database)
from urllib.parse import urljoin, urlparse, urlunparse  # Helpers to work with website addresses
import os  # Helps us work with files and folders on our computer
import logging  # Like a notebook to jot down any problems we encounter
from datetime import datetime  # A clock and calendar to know the current time and date

# Setting up a diary to note down any problems during our website adventure.
logging.basicConfig(filename='scraping.log', level=logging.ERROR)

def ensure_correct_url_format(url):
    """
    Make sure the website address is written correctly, like checking if you have 
    the full address before you start your adventure.
    Talking Point: Imagine you have a map, but it's missing some details. 
    This function fills in those missing pieces to make sure you can find the treasure!
    """
    parsed_url = urlparse(url)  # Breaking the address into smaller parts
    scheme = parsed_url.scheme  # Like 'http' or 'https', the beginning of a web address
    netloc = parsed_url.netloc  # The main part of the address, like 'example.com'
    
    # Fill in missing parts of the map (URL) if they're not there
    if not scheme:
        scheme = "http"
    if not netloc:
        netloc = parsed_url.path
        path = ""
    else:
        path = parsed_url.path

    return urlunparse((scheme, netloc, path, "", "", ""))

def create_db_filename(base_url):
    """
    Create a special name for our notebook (database) using the website's name and the current date.
    Talking Point: It's like naming your diary with the place you're exploring and the date 
    you went on the adventure, so you always remember when you found your treasures.
    """
    parsed_url = urlparse(base_url)  # Splitting the base URL into parts
    domain_name = parsed_url.netloc.replace("www.", "").replace('.', '_')  # Cleaning the main part of the address
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Getting the current date and time for our diary's name
    db_filename = f"{domain_name}_{timestamp}.db"  # Creating a unique name for the diary
    return db_filename

# Asking for the first website we want to explore
base_url = input("Enter the base URL to start scraping (e.g., 'https://example.com'): ")
# Making sure the website address is just right for our journey
base_url = ensure_correct_url_format(base_url)

# Creating a unique diary (database file) to jot down our findings
db_filename = create_db_filename(base_url)
db_path = os.path.join(os.getcwd(), db_filename)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
# Setting up a page in our diary to list down all the paths (URLs) we find
cursor.execute("CREATE TABLE IF NOT EXISTS urls (url TEXT UNIQUE)")

def scrape_page(url):
    """
    Explore a webpage and find all the paths (links) it has.
    Talking Point: Imagine this as our treasure hunter looking around a room for doors 
    and windows leading to new rooms. Every new door or window found is a new adventure!
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look at each link on the page and note it down if it's a path we haven't seen before
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            if not cursor.execute("SELECT url FROM urls WHERE url = ?", (full_url,)).fetchone():
                cursor.execute("INSERT INTO urls (url) VALUES (?)", (full_url,))
                conn.commit()
                yield full_url
    except requests.RequestException as e:
        # If we run into problems exploring a room, we write that down too
        logging.error(f"RequestException occurred for URL: {url} with error: {str(e)}")

# Preparing our list of places to explore
visited_urls = set()
url_queue = [base_url]

# The journey begins! We start exploring each place one by one
while url_queue:
    current_url = url_queue.pop(0)
    # Making sure we don't explore the same place twice
    if current_url not in visited_urls:
        visited_urls.add(current_url)
        # For each new place, find more paths and add them to our adventure list
        for new_url in scrape_page(current_url):
            if new_url not in visited_urls:
                url_queue.append(new_url)

# After the adventure, make sure all our findings are safely written in our diary
try:
    conn.commit()
finally:
    # Closing our diary and keeping it safe
    conn.close()

# Final Talking Point: Think of this as the end of a great adventure. We've explored 
# many places, found lots of paths, and kept a detailed diary of all our discoveries. 
# It's important to remember to explore kindly and respectfully!
