import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# URLs and resources where we can get general information about TON
TON_SOURCES = [
    "https://ton.org/docs",
    "https://tonscan.org/",
    "https://en.wikipedia.org/wiki/The_Open_Network",
    "https://docs.ton.org/",
    "https://wallet.tg/",
    "http://ston.fi/",
    "https://www.tapps.center/",
    "https://tonstarter.com/",
    "https://core.telegram.org/bots/webapps",
    "https://ton.org/en/mini-apps",
    "https://tonresear.ch/u/simpson/summary",
    "https://core.telegram.org"
    # Other necessary resource URLs can be added here
]

# Create folders to store files and texts to download
OUTPUT_DIR = "TON_Library"
os.makedirs(OUTPUT_DIR, exist_ok=True)

visited_urls = set()
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

total_links = 0
successful_downloads = 0
failed_downloads = 0

def download_file(url, output_path):
    global successful_downloads, failed_downloads
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, stream=True, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"✅ Downloaded: {output_path}")
            successful_downloads += 1
            return
        except requests.RequestException as e:
            print(f"❌ Failed to download: {url}, attempt: {attempt + 1}, error: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    print(f"❌ Failed to download after {MAX_RETRIES} attempts: {url}")
    failed_downloads += 1

def save_text(text, filename):
    safe_filename = "".join([c if c.isalnum() else "_" for c in filename])
    with open(os.path.join(OUTPUT_DIR, safe_filename), 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"✅ Saved text: {filename}")

def scrape_and_save_ton_data(url, depth=2):
    global total_links, successful_downloads, failed_downloads
    if url in visited_urls or depth == 0:
        return
    visited_urls.add(url)
    total_links += 1
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            break
        except requests.RequestException as e:
            print(f"❌ Failed to access: {url}, attempt: {attempt + 1}, error: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    else:
        print(f"❌ Failed to access after {MAX_RETRIES} attempts: {url}")
        failed_downloads += 1
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Save text data
    text = soup.get_text()
    filename = urlparse(url).netloc + '_' + os.path.basename(urlparse(url).path) + '.txt'
    save_text(text, filename)

    # Find and download PDF files and other links
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(url, href)
        total_links += 1

        if href.endswith('.pdf') or href.endswith('.doc') or href.endswith('.docx'):
            file_extension = os.path.splitext(href)[1]
            file_filename = os.path.join(OUTPUT_DIR, os.path.basename(href))
            download_file(full_url, file_filename)
        elif urlparse(full_url).netloc == urlparse(url).netloc:  # Only follow internal links
            scrape_and_save_ton_data(full_url, depth - 1)

if __name__ == "__main__":
    print("\nStarting the TON data scraping process...\n")
    for source in TON_SOURCES:
        scrape_and_save_ton_data(source)
    
    print("\n\n📊 Analysis Report:")
    print(f"🔗 Total links processed: {total_links}")
    print(f"✅ Successful downloads: {successful_downloads}")
    print(f"❌ Failed downloads: {failed_downloads}")
    print("\nProcess completed!")
