import requests

url = "http://127.0.0.1:49152"

prompt = "ブルーアーカイブとは"

session = "sgkJqk5qRqlEF0jm"

#response = requests.get(url + f"/process/?session_id={session}&prompt={prompt}?&path=/src/llama2/test/tmp_1")
response = requests.get(url + f"/process/?session_id={session}&prompt={prompt}")

print(response.text)