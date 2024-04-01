import requests
from bs4 import BeautifulSoup
import csv, re


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
        #print("Failed to fetch articles from the API.")
        return []


# Needed: <publication date>;<update date>;<meta location>;<title>;<HTML text>;<rawtext>
def extract_article_info(url):
    response = requests.get(url)
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            # print(soup.prettify())  # Print the HTML content for debugging
            (publish_date, update_date) = extract_publish_date(soup)
            meta_location_element = soup.find('li', class_='news-section-bar').find('span', class_='icon fa fa-map-marker')
            meta_location = meta_location_element.next_sibling.strip()
            title_element = soup.find('title')
            title = title_element.text.strip()
            (html_text, raw_text) = extract_text_data(soup)
            return publish_date, update_date, meta_location, title, html_text, raw_text
        except AttributeError:
            print(f"Failed to extract information from article: {url}")
            return None
    else:
        print(f"Failed to fetch article from URL: {url}")
        return None


def save_to_csv(articles_data):
    with open('accidents_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Publication Date', 'Update Date', 'Meta Location', 'Title', 'HTML Text', 'Raw Text'])
        for article_data in articles_data:
            writer.writerow(article_data)


def extract_publish_date(soup):
    li_elements = soup.find_all('li')
    publish_date = ""
    update_date = ""
    for li in li_elements:
        if "Publish-" in li.text:
            publish_date = li.text.split("Publish-")[-1].strip()
        if "Update-" in li.text:
            update_date = li.text.split("Update-")[-1].strip()
    return publish_date, update_date


def extract_update_date(soup):
    li_elements = soup.find_all('li')
    for li in li_elements:
        if "Update-" in li.text:
            return li.text.split("Update-")[-1].strip()
    return "-"


def extract_text_data(soup):
    target_div = soup.find('div', class_='text')
    if not target_div:
        return "", ""
    html_text = ''.join(str(p) for p in target_div.find_all('p'))
    raw_text = ' '.join(p.get_text(strip=True) for p in target_div.find_all('p'))
    return html_text, raw_text

if __name__ == "__main__":
    tag_id = 54
    i = 1
    article_urls = []
    articles_data = []
    while True:
        current_page = fetch_articles_from_api(tag_id,i)
        if current_page:
            #print("List of article URLs:"+f'{i}')
            for url in article_urls:
                print(url)
            article_urls.extend(current_page)
        else:
            break
        i = i + 1

    for url in article_urls:
        article_info = extract_article_info(url)
        if article_info:
            articles_data.append(article_info)

    save_to_csv(articles_data)

    #article_urls is what you need. I'd suggest to nest everything in main in a function.
    #!!there are over 100 pages of lists of articles. it might take a few seconds to run. Uncomment the print statements if you want to see it.