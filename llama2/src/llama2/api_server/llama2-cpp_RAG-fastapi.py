import uvicorn
import uvicorn
import asyncio
from fastapi import FastAPI,UploadFile, File,Response 
from datetime import datetime

from llama_index.llms import LlamaCPP
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index import (
    LLMPredictor,
    ServiceContext,
)
from llama_index.callbacks import (
    CallbackManager,
    LlamaDebugHandler
)

from modules.vector_database_create import create
from modules.vector_database_upload import upload
from modules.llama2_inference import create_async_process,normal,rag

#FastAPIのインスタンス化
app = FastAPI()



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



############################################
############### RAG有り推論 ################
############################################
@app.get("/RAG_inference/")
async def RAG_inference(response: Response,session_id: str , prompt: str , key: str):
    result = await rag(prompt,key,access_token,response,sessions,session_id)
    return result



############################################
############### RAG無し推論 ################
############################################
@app.get("/Normal_inference/")
async def Normal_inference(response: Response , prompt: str , key: str):
    result = await normal(llm,prompt,key,access_token,response)
    return result



############################################
######### ベクトルデータベース登録 ###########
############################################
@app.post("/vector_database_upload/")
async def upload_route(response: Response,file: UploadFile = File(...)):
    save_dir = "/src/data/vector_database_upload/"
    schema = "/src/json_schema/vector_database_upload.json"

    session_id,session_dir = await upload(response,file,save_dir,access_token,schema)

   # 新しい非同期プロセスを作成し、セッションに関連付ける
    async_process = await create_async_process(session_dir,service_context)
    sessions[session_id] = {"async_process": async_process, "expiration_time": async_process.expiration_time}

    return f"セッションID「{session_id}」が発行されました。有効期限は {async_process.expiration_time} (UTC)です。"



############################################
########## ベクトルデータベース作成 ##########
############################################
@app.post("/vector_database_create/")
async def create_route(response: Response,file: UploadFile = File(...)):
    save_dir = "/src/data/vector_database_create/"
    schema = "/src/json_schema/vector_database_create.json"

    combined_data = await create(response,file,save_dir,access_token,schema,llm_predictor,embed_model)

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
    LLM_path = "/src/models/Llama-2-70B-chat-GGUF/llama-2-70b-chat.Q5_K_M.gguf"

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

    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        embed_model=embed_model,
        chunk_size=300,
        chunk_overlap=20,
        callback_manager=callback_manager,
    )

    # セッションIDと非同期プロセスを管理するための辞書
    sessions = {}

    #アクセストークンの読み込み
    with open("/src/access_token/token" , "r") as f :
        access_token = f.read()

    # サーバーの起動
    uvicorn.run(app, host="0.0.0.0", port=49152)
