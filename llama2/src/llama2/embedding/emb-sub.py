import logging
import os
import sys
import uvicorn
import fastapi
import base64

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
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index import StorageContext, load_index_from_storage
from llama_index.llms.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)



# ログレベルの設定
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, force=True)

# ドキュメントの読み込み
documents = SimpleDirectoryReader("/src/text_data/oecu").load_data()


# LLMのセットアップ
LLM_path = "/src/models/llama-2-13b-chat.Q4_K_S"
llm = LlamaCPP(model_path=LLM_path, model_kwargs={"n_ctx": 8192, "n_gpu_layers": 83})
llm_predictor = LLMPredictor(llm=llm)

# 実行するモデルの指定とキャッシュフォルダの指定
embed_model_name = ("/src/models/multilingual-e5-small")
cache_folder = "./sentence_transformers"

# 埋め込みモデルの作成
embed_model = HuggingFaceEmbedding(
    model_name=embed_model_name,
    cache_folder=cache_folder,
    device="cpu"
)

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
index.storage_context.persist(persist_dir="/src/llama_oecu")