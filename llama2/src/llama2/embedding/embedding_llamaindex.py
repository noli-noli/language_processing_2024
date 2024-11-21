from llama_index.llms import LlamaCPP
from llama_index import VectorStoreIndex, ServiceContext, download_loader
from llama_index.text_splitter import SentenceSplitter
from llama_index.llms.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
from llama_index import (
    LLMPredictor,
    PromptTemplate,
    ServiceContext,
    SimpleDirectoryReader,
    VectorStoreIndex,
)

# LLMのパス
LLM_path = "/src/models/llama-2-13b-chat.Q4_K_S"

# Embeddingモデルのパス
Embedding_path = "/src/models/multilingual-e5-small"

#ドキュメントのパス
Document_path = "/src/text_data/oecu"

# インデックスの保存先  
save_index_path = "/src/llama_oecu"

# LLMのセットアップ
llm = LlamaCPP(model_path=LLM_path, model_kwargs={"n_ctx": 4096, "n_gpu_layers": 83},messages_to_prompt=messages_to_prompt,completion_to_prompt=completion_to_prompt)



# ドキュメントの読み込み
documents = SimpleDirectoryReader(Document_path).load_data()
# Nodeの作成
text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
# ServiceContextの作成
service_context = ServiceContext.from_defaults(text_splitter=text_splitter, embed_model="local", llm=llm)

# indexの作成
index = VectorStoreIndex.from_documents(
    documents, service_context=service_context
)

# Indexを保存
index.storage_context.persist(persist_dir=save_index_path)
