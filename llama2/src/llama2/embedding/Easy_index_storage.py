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
from llama_index import StorageContext, load_index_from_storage
from llama_index.llms.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)

# LLMのパス
LLM_path = "/src/models/Llama-2-70B-chat-GGUF/llama-2-70b-chat.Q8_0.gguf"

# llama2のセットアップ
llm = LlamaCPP(model_path=LLM_path, model_kwargs={"n_ctx": 4096, "n_gpu_layers": 83},messages_to_prompt=messages_to_prompt,completion_to_prompt=completion_to_prompt)

# text_splitterの設定
text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)

# ServiceContextの作成
service_context = ServiceContext.from_defaults(text_splitter=text_splitter, embed_model="local", llm=llm)

# ドキュメントの読み込み
documents = SimpleDirectoryReader("/src/text_data").load_data()

# indexの作成
index = VectorStoreIndex.from_documents(
    documents, service_context=service_context
)

# Indexを保存
index.storage_context.persist(persist_dir="/src/llama_index_2")