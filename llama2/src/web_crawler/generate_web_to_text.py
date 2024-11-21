from modules import url_crawl
from modules import url_to_text

#クロール対象のURL
target_url = "https://www.osakac.ac.jp/"
#保存先のテキストファイルのパス
save_text_path = "/src/text_data/OECU_official-deep4.txt"
#クロールの深さ
max_depth = 4

url_list = url_crawl.crawl(target_url, max_depth)

text = []

for url in url_list:
    print(url)
    if target_url in url:
        text.append(url_to_text.text_conversion(url))
    else:
        print(f"pass through {url}")

for i in range(len(text)):
    with open(save_text_path, "a") as f:
        f.write(str(text[i]))


