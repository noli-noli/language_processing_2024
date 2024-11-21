import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

url_list = []

# URLからHTMLを取得する関数
def get_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        print("Error:", e)
        return None

# URLからリンクを取得する関数
def extract_links(html, base_url):
    links = set()
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href.startswith('http'):
            links.add(href)
        else:
            links.add(urljoin(base_url, href))
    return links

# URLを探索する関数
def crawl(url, max_depth, current_depth=1, visited=None):
    global url_list

    if visited is None:
        visited = set()
    elif current_depth > max_depth:
        return
    elif url in visited:
        return
    else:
        visited.add(url)
    
    url_list.append(url)

    print(f"Crawling {url} at depth {current_depth}")

    html = get_html(url)
    if html:
        links = extract_links(html, url)
        for link in links:
            parsed_link = urlparse(link)
            if parsed_link.scheme in ['http', 'https']:
                crawl(link, max_depth, current_depth + 1, visited)
    
    return url_list

"""
if __name__ == "__main__":
    start_url = "https://www.osakac.ac.jp/"
    max_depth = 2
    crawl(start_url,max_depth)
"""