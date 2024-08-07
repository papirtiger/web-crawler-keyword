import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import argparse

def crawl_website(start_url, keyword):
    visited = set()
    to_visit = [start_url]
    found_pages = []

    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue

        try:
            response = requests.get(current_url)
            visited.add(current_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                if keyword.lower() in soup.get_text().lower():
                    found_pages.append(current_url)
                    print(f"Fundet '{keyword}' på: {current_url}")

                for link in soup.find_all('a', href=True):
                    new_url = urljoin(current_url, link['href'])
                    if new_url.startswith(start_url) and new_url not in visited:
                        to_visit.append(new_url)

        except Exception as e:
            print(f"Fejl ved crawling af {current_url}: {e}")

    return found_pages

def extract_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        print(f"Fejl ved udtrækning af tekst fra {url}: {e}")
        return ""

def main(start_url, keyword):
    print(f"Starter crawling fra {start_url} og søger efter '{keyword}'")
    found_pages = crawl_website(start_url, keyword)
    
    if found_pages:
        print(f"\nFundet {len(found_pages)} sider med '{keyword}'")
        
        with open("extracted_content.txt", "w", encoding="utf-8") as f:
            for page in found_pages:
                print(f"Udtrækker tekst fra {page}")
                text = extract_text(page)
                f.write(f"URL: {page}\n\n")
                f.write(text)
                f.write("\n\n" + "="*50 + "\n\n")
        
        print(f"\nUdtrukket indhold er gemt i 'extracted_content.txt'")
    else:
        print(f"Ingen sider fundet med '{keyword}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Crawler og Tekstudtrækning")
    parser.add_argument("url", help="Start URL for crawling")
    parser.add_argument("keyword", help="Søgeord at lede efter")
    args = parser.parse_args()

    main(args.url, args.keyword)
