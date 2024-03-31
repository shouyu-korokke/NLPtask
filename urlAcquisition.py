import requests
from bs4 import BeautifulSoup

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

if __name__ == "__main__":
    tag_id = 54
    i = 1
    article_urls = []
    while True:
        current_page = fetch_articles_from_api(tag_id,i)
        if current_page:
            #print("List of article URLs:"+f'{i}')
            #for url in article_urls:
            #    print(url)
            article_urls.extend(current_page)
        else:
            break
        i = i + 1
        
    
    #article_urls is what you need. I'd suggest to nest everything in main in a function.
    #!!there are over 100 pages of lists of articles. it might take a few seconds to run. Uncomment the print statements if you want to see it.