import os
import random
import string
import json

from llama_index import (
    ServiceContext,
    SimpleDirectoryReader,
    VectorStoreIndex,
)

from llama_index.callbacks import (
    CallbackManager,
    LlamaDebugHandler,
)

from fastapi import status

from jsonschema import (
    validate, 
    ValidationError,
)



async def create(response,file,save_dir,access_token,schema,llm_predictor,embed_model):
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
        #ファイルサイズのチェック(KB)
        if (len(contents) / 1024) >= 50:
            return "ファイルサイズが大きすぎます。対応するファイルサイズは50KB以下です。"
        #アップロードされたjsonを変数に格納
        uploaded_json = json.loads(contents)
        #アクセストークンのチェック
        if uploaded_json["key"] != access_token:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return "アクセストークンが不正です。"
        #jsonスキーマーによる形式チェック
        validate(uploaded_json, json_schema)
        #uploaded_json内の"context"をjsonファイルに保存
        with open(os.path.join(session_dir,"context.txt"), "wb") as f:
            f.write(uploaded_json["context"].encode('utf-8'))
    except ValidationError as e:
        #スキーマーによる形式チェックエラー
        print(e)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "jsonファイルの形式が不正です。"
    except Exception as e:
        #その他のエラー
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(e)
        return "Error"
    # ドキュメントの読み込み
    documents = SimpleDirectoryReader(session_dir).load_data()
    # ServiceContextとdebug用 Callback Managerのセットアップ
    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug])
    #コンテキストサービスの設定
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        embed_model=embed_model,
        chunk_size=300,
        chunk_overlap=20,
        callback_manager=callback_manager,
    )
    # インデックスの生成
    index = VectorStoreIndex.from_documents(
        documents,
        service_context=service_context,
    )
    # Indexを保存
    index.storage_context.persist(persist_dir=session_dir)
    # ディレクトリ内のすべてのJSONファイルに対して処理を行う
    # 辞書を初期化
    combined_data = {}
    for filename in os.listdir(os.path.join(save_dir,session_id)):
        if filename.endswith('.json'):
            # JSONファイルのパス
            file_path = os.path.join(os.path.join(save_dir,session_id), filename)
            # JSONファイルを読み込んで辞書に追加
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                combined_data[filename] = json_data

    return combined_data

