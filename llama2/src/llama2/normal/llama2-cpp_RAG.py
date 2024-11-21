import logging
import os
import sys

from llama_index import (
    LLMPredictor,
    PromptTemplate,
    ServiceContext,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import LlamaCPP

#日本語入力用モジュール
import readline


# ログレベルの設定
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, force=True)

# ドキュメントの読み込み
documents = SimpleDirectoryReader("/src/text_data").load_data()


# LLMのセットアップ
model_path = "/src/models/Llama-2-70B-chat-GGUF/llama-2-70b-chat.Q5_K_M.gguf"
llm = LlamaCPP(model_path=model_path, model_kwargs={"n_ctx": 4096, "n_gpu_layers": 83})
llm_predictor = LLMPredictor(llm=llm)
    

# 実行するモデルの指定とキャッシュフォルダの指定
embed_model_name = ("/src/models/multilingual-e5-large")
cache_folder = "./sentence_transformers"

# 埋め込みモデルの作成
embed_model = HuggingFaceEmbedding(
    model_name="/src/models/multilingual-e5-large",
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

temp = """
[INST]
<<SYS>>
以下の「コンテキスト情報」を元にできるだけ正確に「質問」に回答してください。絶対に日本語で答える事。
なお、コンテキスト情報に無い情報は回答に含めないでください。
また、コンテキスト情報から回答が導けない場合は「分かりません」と回答してください。
<</SYS>>
# コンテキスト情報
---------------------
{context_str}
---------------------

# 質問
{query_str}

[/INST]
"""

query_engine = index.as_query_engine(
    similarity_top_k=5, text_qa_template=PromptTemplate(temp)
)

while True:
    req_msg = input("\n## Question: ")
    if req_msg == "":
        continue
    res_msg = query_engine.query(req_msg)
    res_msg.source_nodes[0].text
    event_pairs = llama_debug.get_llm_inputs_outputs()
    print("\n## Answer: \n", str(res_msg).strip())