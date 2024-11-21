import os
import random
import string
import json
from fastapi import status
from jsonschema import (
    validate, 
    ValidationError,
)

async def upload(response ,file,save_dir,access_token,schema):
    #セッションIDの生成
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    #セッションIDのディレクトリを作成
    os.mkdir(os.path.join(save_dir,session_id))
    #セッションIDのディレクトリのパス
    session_dir = os.path.join(save_dir,session_id)

    #本関数で使用するjsonスキーマーのロード
    with open(schema) as file_obj:
        json_schema = json.load(file_obj)
    
    #アップロードされたファイルの形式チェック及び保存
    try:
        contents = await file.read()
        #ファイルサイズのチェック(MB)
        if (len(contents) / 1024000) >= 100:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return "異常なファイルサイズを検知しました。"
        #アップロードされたjsonを変数に格納
        uploaded_json = json.loads(contents)
        #accsess_tokenのチェック
        if uploaded_json["key"] != access_token:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return "アクセスキーが不正です。"
        #jsonスキーマーによる形式チェック
        #validate(uploaded_json, json_schema) #形式が良く分からないので一旦コメントアウト
        #uploaded_jsonをjsonファイルに保存
        with open(os.path.join(session_dir,"combined.json"), "w") as f:
            json.dump(uploaded_json, f, indent=4)
    except ValidationError as e:
        #スキーマーによる形式チェックエラー
        print(e)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "jsonファイルの形式が不正です。"
    except Exception as e:
        #その他のエラー
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return "Error"
    
    # 読み込んだJSONデータを元の複数のJSONファイルに展開する
    for key, value in uploaded_json.items():
        print(key)
        with open(os.path.join(session_dir,key), 'w') as f:
            json.dump(value, f, indent=4)
    os.remove(os.path.join(session_dir,"combined.json"))

    return session_id,session_dir
