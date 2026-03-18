import requests
from bs4 import BeautifulSoup
import urllib.parse

def extract_text(soup):
    """
    Extracts and cleans text from a BeautifulSoup object.
    """
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def scrape_page(url):
    """
    Scrapes text from a given URL.
    """
    if not url or not url.startswith('http'):
        return ""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = extract_text(soup)
            return text[:10000] # Increased limit for more context
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    return ""

def scrape_website(homepage_url):
    """
    Scrapes homepage and tries to find and scrape an about page.
    Reuses the first request to find the "About" link.
    """
    if not homepage_url:
        return ""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    homepage_text = ""
    about_text = ""

    try:
        response = requests.get(homepage_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            homepage_text = extract_text(soup)[:10000]

            # Find About page link
            about_url = None
            for link in soup.find_all('a', href=True):
                link_text = link.text.lower()
                link_href = link['href'].lower()
                if 'about' in link_text or 'about' in link_href:
                    about_url = urllib.parse.urljoin(homepage_url, link['href'])
                    break

            if about_url:
                about_text = scrape_page(about_url)

    except Exception as e:
        print(f"Error scraping website {homepage_url}: {e}")

    return f"HOMEPAGE:\n{homepage_text}\n\nABOUT PAGE:\n{about_text}"
