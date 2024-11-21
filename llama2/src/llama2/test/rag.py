import requests

access_token = "please_token"

#セッションID(発行されたセッションIDを以下に張り付けて下さい)
session_id="17EuBECnCHpFzV82"

#RAG有プロンプトURL
url = "http://133.89.44.20:49152/RAG_inference/"

#プロンプト(任意に書き換えてみてください)
prompt = "ほげほげ株式会社とは？"

response = requests.get(url + f"?session_id={session_id}&prompt={prompt}&key={access_token}")


#ステータスチェック
if response.status_code == 200:
  #正常終了
  print(f"Status OK:{response.status_code}")
  print(f"{response.text}")
else:
  #異常終了
  print(f"Bad Status:{response.status_code}")
  print(response.text)