import logging
import os
import sys
import uvicorn
import fastapi
import requests
import re
import json

from llama_index import (
    LLMPredictor,
    PromptTemplate,
    ServiceContext,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from fastapi.responses import JSONResponse
from llama_index.llms import LlamaCPP
from llama_index.text_splitter import SentenceSplitter
from llama_index import StorageContext, load_index_from_storage
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.llms.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
from typing import List
import uvicorn
import asyncio
from fastapi import FastAPI,UploadFile, File,status,Response 
from datetime import datetime, timedelta
from jsonschema import validate, ValidationError
import random
import string

#日本語入力用モジュール
import readline


#FastAPIのインスタンス化
app = FastAPI()


class MainProcess:
    def __init__(self,expiration_time,path):
        print("##### new process created #####")
        self.path = path
        self.expiration_time = expiration_time
        # storage contextの再構築
        self.storage_context = StorageContext.from_defaults(persist_dir=self.path)

        # 保存したindexの読み込み
        self.index = load_index_from_storage(self.storage_context,  service_context=service_context)

    async def process(self, prompt):
        req_msg = ("\n## Question: " + prompt)
        temp = """
        [INST]
        <<SYS>>
        貴方は日本語で話す優秀なチャットボットです。
        以下の「コンテキスト情報」を元に正確に「質問」に回答してください。
        なお、コンテキスト情報に無い情報は回答に含めないでください。
        また、コンテキスト情報から回答が導けない場合は「分かりません」と回答してください。
        更に、「.txt」ファイルに関する情報は回答に含めないでください。
        <</SYS>>
        # コンテキスト情報
        ---------------------
        {context_str}
        ---------------------

        # 質問
        {query_str}

        [/INST]
        """
        query_engine = self.index.as_query_engine(similarity_top_k=5, text_qa_template=PromptTemplate(temp))
        res_msg = query_engine.query(req_msg)
        res_msg.source_nodes[0].text
        event_pairs = llama_debug.get_llm_inputs_outputs()
        print("\n## Answer: \n", str(res_msg).strip())
        return str(res_msg).strip()



async def create_async_process(path):
    expiration_time = datetime.now() + timedelta(minutes=1440)  # 10分後に有効期限切れ
    return MainProcess(expiration_time,path)



############################################
############### セッション廃棄 ##############
############################################
async def cleanup_expired_processes():
    print("##### start cleanup_expired_processes #####")
    while True:
        await asyncio.sleep(60)  # 60秒ごとに実行

        current_time = datetime.now()
        expired_sessions = []

        for session_id, process_info in sessions.items():
            if process_info["expiration_time"] <= current_time:
                # 有効期限が切れたプロセスをリストに追加
                expired_sessions.append(session_id)

        # 有効期限が切れたプロセスを削除
        for session_id in expired_sessions:
            del sessions[session_id]
            print(f"##### delete process {session_id} #####")



async def nllb_post(text,input_code,output_code,max_length):
    url = "http://133.89.6.54:49153/text/"
    # アルファベット、数字、ピリオド、カンマ、日本語、空白以外の文字を削除する正規表現パターン
    clean_text = re.sub(r'[^\w.,\u3000-\u30FF\u3040-\u309F\u4E00-\u9FFF\s]', '', text)
    response = requests.get(url + f"?text={clean_text}&input_code={input_code}&output_code={output_code}&max_length={max_length}")
    return response.text



############################################
############### RAG有り推論 ################
############################################
@app.get("/RAG_inference/")
async def RAG_inference(response: Response,session_id: str , prompt: str , key: str):
    print(f"##### process id: {session_id}, prompt: {prompt} #####")
    if key != access_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "アクセスキーが不正です。"
    elif session_id not in sessions or sessions[session_id]["expiration_time"] < datetime.now():
        print("##### not found process #####")
        response.status_code = status.HTTP_404_NOT_FOUND
        return "セッションが見つかりません。有効期限が切れている可能性があります。"


    print("##### found process #####")

    async_process = sessions[session_id]["async_process"]
    result = await async_process.process(prompt)

    #即興で翻訳APIへのリクエスト 
    result = await nllb_post(result,"eng_Latn","jpn_Jpan",1000)
    result = re.sub("\"", "", result)

    return result



############################################
############### RAG無し推論 ################
############################################
@app.get("/Normal_inference/")
async def Normal_inference(response: Response , prompt: str , key: str):
    if key != access_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "アクセスキーが不正です。"
    result = llm.complete("貴方は日本語で話す優秀なチャットボットです。次の質問に答えなさい。" + prompt)
    #即興で翻訳APIへのリクエストeng_Latn
    result = await nllb_post(result.text,"eng_Latn","jpn_Jpan",1000)
    result = re.sub("\"", "", result)
    return result



############################################
######### ベクトルデータベース登録 ###########
############################################
@app.post("/vector_database_upload/")
async def vector_database_upload(response: Response,file: UploadFile = File(...)):
    #保存先ディレクトリの指定
    Uploaddir = "/src/data/vector_database_upload/"
    #セッションIDの生成
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    #セッションIDのディレクトリを作成
    os.mkdir(os.path.join(Uploaddir,session_id))
    #セッションIDのディレクトリのパス
    session_dir = os.path.join(Uploaddir,session_id)

    #本関数で使用するjsonスキーマーのロード
    with open('/src/json_schema/vector_database_upload.json') as file_obj:
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

    # 新しい非同期プロセスを作成し、セッションに関連付ける
    async_process = await create_async_process(session_dir)
    sessions[session_id] = {"async_process": async_process, "expiration_time": async_process.expiration_time}

    return f"セッションID「{session_id}」が発行されました。有効期限は {async_process.expiration_time} (UTC)です。"


############################################
########## ベクトルデータベース作成 ##########
############################################
@app.post("/vector_database_create/")
async def vector_database_create(response: Response,file: UploadFile = File(...)):
    #保存先ディレクトリの指定
    Uploaddir = "/src/data/vector_database_create/"
    #セッションIDの生成
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    #セッションIDのディレクトリを作成
    os.mkdir(os.path.join(Uploaddir,session_id))
    #セッションIDのディレクトリのパス
    session_dir = os.path.join(Uploaddir,session_id)

    #本関数で使用するjsonスキーマーのロード
    with open('/src/json_schema/vector_database_create.json') as file_obj:
        json_schema = json.load(file_obj)

    #アップロードされたファイルの形式チェック及び保存
    try:
        contents = await file.read()
        #ファイルサイズのチェック(KB)
        if (len(contents) / 1024) >= 50:
            return "ファイルサイズが大きすぎます。対応するファイルサイズは100KB以下です。"
        #アップロードされたjsonを変数に格納
        uploaded_json = json.loads(contents)
        if uploaded_json["key"] != access_token:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return "アクセスキーが不正です。"
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

    # 辞書を初期化
    combined_data = {}

    # ディレクトリ内のすべてのJSONファイルに対して処理を行う
    for filename in os.listdir(os.path.join(Uploaddir,session_id)):
        if filename.endswith('.json'):
            # JSONファイルのパス
            file_path = os.path.join(os.path.join(Uploaddir,session_id), filename)
            # JSONファイルを読み込んで辞書に追加
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                combined_data[filename] = json_data

    return combined_data


###########################################
################# 旧関数 ##################
###########################################
@app.get("/database_to_create/")
async def database_to_create(text: str):
    Uploaddir = "/src/data/create_database/"
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    os.mkdir(os.path.join(Uploaddir,session_id))
    session_dir = os.path.join(Uploaddir,session_id)

    with open(os.path.join(session_dir,"text.txt"), "w") as f:
        f.write(text)

    # ドキュメントの読み込み
    documents = SimpleDirectoryReader(session_dir).load_data()

    # ServiceContextのセットアップ
    ## debug用 Callback Managerのセットアップ
    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug])

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

    # 辞書を初期化
    combined_data = {}

    # ディレクトリ内のすべてのJSONファイルに対して処理を行う
    for filename in os.listdir(os.path.join(Uploaddir,session_id)):
        if filename.endswith('.json'):
            # JSONファイルのパス
            file_path = os.path.join(os.path.join(Uploaddir,session_id), filename)
            # JSONファイルを読み込んで辞書に追加
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                combined_data[filename] = json_data

    return combined_data


###########################################
############### 初期イベント ###############
###########################################
@app.on_event("startup")
async def startup_event():  
    asyncio.create_task(cleanup_expired_processes())


###########################################
############### メイン処理 #################
###########################################
if __name__ == "__main__":
    # LLMのパス
    #LLM_path = "/src/models/Llama-2-70B-chat-GGUF/llama-2-70b-chat.Q8_0.gguf"
    LLM_path = "/src/models/Llama-2-13B-chat-GGUF/llama-2-13b-chat.Q4_K_S"

    # LLMのセットアップ(旧)
    #llm = LlamaCPP(model_path=LLM_path, model_kwargs={"n_ctx": 4096, "n_gpu_layers": 83})

    # LLMのセットアップ
    llm = LlamaCPP(model_path=LLM_path, model_kwargs={"n_ctx": 8192, "n_gpu_layers": 83})
    llm_predictor = LLMPredictor(llm=llm)

    #キャッシュフォルダの指定
    cache_folder = "./sentence_transformers"

    # 埋め込みモデルの作成
    embed_model = HuggingFaceEmbedding(
        model_name="/src/models/multilingual-e5-large",
        cache_folder=cache_folder,
        device="cpu"
    )

    ## debug用 Callback Managerのセットアップ
    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug])

    # ServiceContextの作成(旧)
    #text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)

    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        embed_model=embed_model,
        chunk_size=300,
        chunk_overlap=20,
        callback_manager=callback_manager,
    )

    # ServiceContextの作成(旧)
    #service_context = ServiceContext.from_defaults(text_splitter=text_splitter, embed_model="local", llm=llm)

    # セッションIDと非同期プロセスを管理するための辞書
    sessions = {}

    #アクセストークンの読み込み
    with open("/src/access_token/token" , "r") as f :
        access_token = f.read()

    # サーバーの起動
    uvicorn.run(app, host="0.0.0.0", port=49152)
