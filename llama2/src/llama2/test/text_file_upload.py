import os
import json
import base64
import requests


text_file = "./tmp_1/OECU_wiki.txt"
url = "http://127.0.0.1:49152/vector_database_2/"
password = "password"
# アップロードするファイル

files = {'file': open(text_file, 'rb')}
response = requests.post(url, files=files)
print(response.text)