from trafilatura import fetch_url, extract

def text_conversion(url):
    document = fetch_url(url)
    text = extract(document)

    return text