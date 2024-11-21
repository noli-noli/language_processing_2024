import json
import os

# JSONファイルが格納されているディレクトリのパス
directory_path = "/src/llama_tmp"
# 辞書を初期化
combined_data = {}

# ディレクトリ内のすべてのJSONファイルに対して処理を行う
for filename in os.listdir(directory_path):
    if filename.endswith('.json'):
        # JSONファイルのパス
        file_path = os.path.join(directory_path, filename)
        # JSONファイルを読み込んで辞書に追加
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            combined_data[filename] = json_data

# 1つのJSONファイルにまとめて保存
output_file = "./tmp_1/combined.json"
with open(output_file, 'w') as file:
    json.dump(combined_data, file, indent=4)


"""
# 結合されたJSONファイルのパス
combined_json_file = "./tmp_1/combined.json"

# JSONファイルを読み込む
with open(combined_json_file, 'r') as file:
    combined_data = json.load(file)

# 読み込んだJSONデータを元の複数のJSONファイルに展開する
for key, value in combined_data.items():
    print(key)
    with open(f"./tmp_1/{key}", 'w') as f:
        json.dump(value, f, indent=4)
"""


