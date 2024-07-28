import os
import requests
from bs4 import BeautifulSoup

# URLs and resources where we can get general information about TON
TON_SOURCES = [
    "https://ton.org/docs",
    "https://tonscan.org/",
    "https://en.wikipedia.org/wiki/The_Open_Network",
    "https://tonwiki.space/wiki/The_Open_Network",
    "https://docs.ton.org/",
    "https://wallet.tg/",
    "http://ston.fi/" ,
    "https://www.tapps.center/",
    "https://tonstarter.com/",
    "https://core.telegram.org/bots/webapps",
    "https://ton.org/ru/mini-apps",
    "https://tonresear.ch/u/simpson/summary"
    
    # Other necessary resource URLs can be added here
]

# Create folders to store files and texts to download
OUTPUT_DIR = "TON_Library"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_file(url, output_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {output_path}")
    else:
        print(f"Failed to download: {url}")

def save_text(text, filename):
    with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"Saved text: {filename}")

def scrape_and_save_ton_data():
    for source in TON_SOURCES:
        response = requests.get(source)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Save text data
            text = soup.get_text()
            filename = source.split('/')[-1] + '.txt'
            save_text(text, filename)

            # Find and download PDF files and other links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf'):
                    pdf_url = href if href.startswith('http') else source + href
                    pdf_filename = os.path.join(OUTPUT_DIR, os.path.basename(href))
                    download_file(pdf_url, pdf_filename)
        else:
            print(f"Failed to access: {source}")

if __name__ == "__main__":
    scrape_and_save_ton_data()
