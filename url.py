import requests
from bs4 import BeautifulSoup
import csv, re
import sys
import json
def fetch_articles_from_api(tag_id, page):
    api_url = f'https://www.unb.com.bd/api/tag-news?tag_id={tag_id}&item={page}'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        article_urls = []
        soup = BeautifulSoup(data['html'], 'html.parser')
        links = soup.select('div.text a')
        for link in links:
            article_urls.append(link['href'])
        return article_urls
    else:
        # print("Failed to fetch articles from the API.")
        return []


def save_to_csv(articles_data):
    with open('accidents_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Publication Date', 'Update Date', 'Meta Location', 'Title', 'HTML Text', 'Raw Text'])
        for article_data in articles_data:
            writer.writerow(article_data)


def extract_dates(soup):
    li_elements = soup.find_all('li')
    publish_date = ""
    update_date = ""
    for li in li_elements:
        if "Publish-" in li.text:
            publish_date = li.text.split("Publish-")[-1].strip()
        if "Update-" in li.text:
            update_date = li.text.split("Update-")[-1].strip()
    return publish_date, update_date


def extract_location(soup):
    meta_location_element = soup.find('li', class_='news-section-bar').find('span', class_='icon fa fa-map-marker')
    if meta_location_element:
        meta_location = meta_location_element.next_sibling.strip()
        return meta_location
    else:
        return ""


def extract_text_data(soup):
    target_div = soup.find('div', class_='text')
    if not target_div:
        return "", ""
    html_text = ''.join(str(p) for p in target_div.find_all('p'))
    raw_text = ' '.join(p.get_text(strip=True) for p in target_div.find_all('p'))
    return html_text, raw_text

def extract_article_info(url):
    response = requests.get(url)
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            publish_date, update_date = extract_dates(soup)
            meta_location = extract_location(soup)
            title_element = soup.find('title')
            title = title_element.text.strip() if title_element else 'Title not found'
            html_text, raw_text = extract_text_data(soup)
            return {
                "PublicationDate": publish_date,
                "UpdateDate": update_date,
                "MetaLocation": meta_location,
                "Title": title,
                "HtmlText": html_text,  # Only include if needed
                "RawText": raw_text
            }

        except Exception as e:
            print(f"Failed to extract information from article: {url}. Error: {e}")
            return None
    else:
        print(f"Failed to fetch article from URL: {url}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        article_info = extract_article_info(url)
        if article_info:
            print(json.dumps(article_info))
            # print("article_info")  # Or handle as needed
        else:
            print("No information could be extracted.")
    else:
        print("Please provide a URL as an argument.")