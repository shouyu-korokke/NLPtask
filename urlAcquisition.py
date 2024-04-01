import requests
from bs4 import BeautifulSoup
import csv

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

            publish_date_element = soup.find('li', class_='news-section-bar')
            publish_date = publish_date_element.text.strip()
            print(f"Publish date: {publish_date}\n")

            # print("Success to get publish date\n")
            update_date_element = soup.find('li', class_='news-section-bar', string='Update-')
            update_date = update_date_element.find('span', class_='icon qb-clock').text.strip() if update_date_element else None
            # print("Success to get update date\n")
            meta_location_element = soup.find('li', class_='news-section-bar').find('span', class_='icon fa fa-map-marker')
            meta_location = meta_location_element.next_sibling.strip()  # Extracting the text next to the span element
            # print("Success to get meta location\n")
            title_element = soup.find('title')
            title = title_element.text.strip()
            # print("Success to get title\n")
            html_text = soup.find('div', class_='news-article-content').get_text(separator='\n').strip() if soup.find('div', class_='news-article-content') else None
            # print("Success to get html_text\n")
            raw_text = soup.find('div', class_='news-article-content').get_text(separator='\n', strip=True).strip() if soup.find('div', class_='news-article-content') else None
            # print("Success to get raw text\n")
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


if __name__ == "__main__":
    tag_id = 54
    i = 1
    article_urls = []
    articles_data = []
    while True:
        current_page = fetch_articles_from_api(tag_id,i)
        if current_page:
            #print("List of article URLs:"+f'{i}')
            #for url in article_urls:
                #print(url)
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