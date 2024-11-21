import requests

access_token = "please_token"

#RAG無プロンプトURL
url = "http://133.89.44.20:49152/Normal_inference/"

#プロンプト
prompt = "ほげほげ株式会社の電話番号とは"

response = requests.get(url + f"?prompt={prompt}&key={access_token}")


#ステータスチェック
if response.status_code == 200:
  #正常終了
  print(f"Status OK:{response.status_code}")
  print(f"{response.text}")
else:
  #異常終了
  print(f"Bad Status:{response.status_code}")
  print(response.text)