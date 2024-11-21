import os
import json
import zipfile


############################################
## ディレクトリをZIPアーカイブに圧縮する関数 ##
############################################

def zip_directory(directory_path, zip_filename):
    # ZIPファイルを新規作成または上書きモードで開く
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # ディレクトリ内のファイルとサブディレクトリを再帰的に走査
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                # ファイルのフルパスを取得
                file_path = os.path.join(root, file)
                # ファイルをZIPアーカイブに追加
                zipf.write(file_path, os.path.relpath(file_path, directory_path))

# 指定されたディレクトリのパス
directory_path = "/src/llama_oecu"
zip_file = "./tmp_1/compressed_directory.zip"

# ディレクトリ内のすべてのJSONファイルのパスを取得
zip_directory(directory_path, zip_file)

