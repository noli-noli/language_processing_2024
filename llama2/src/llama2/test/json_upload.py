import os
import json
import base64
import requests


access_token = "please_token"


vector_database = "./vector_database.json"
url = "http://133.89.44.20:49152/vector_database_upload/"

#ベクトルデータベースの転送処理
tmp = {'file': open(vector_database, 'rb')}
response = requests.post(url, files=tmp)

#ステータスチェック
if response.status_code == 200:
  #正常終了
  print(f"Status OK:{response.status_code}")
  print(response.text)
else:
  #異常終了
  print(f"Bad Status:{response.status_code}")
  print(response.text)


#vector_database
"""
json_path = "./context.json"
vector_database = "./vector_database.json"
url = "http://133.89.44.20:49152/vector_database_create/"
# アップロードするファイル

files = {'file': open(json_path, 'rb')}
response = requests.post(url, files=files)
#ステータスチェック
if response.status_code == 200 :
  print(f"Status OK:{response.status_code}")
  #正常終了
  response_json = json.loads(response.text)
  response_json.update({"key" : access_token})
  with open(vector_database, 'w') as f:
      json.dump(response_json, f, indent=4)
else:
  #異常終了
  print(f"Bad Status:{response.status_code}")
  print(response.text)
"""
