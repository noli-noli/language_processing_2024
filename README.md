# Collaborative_classes_2024
本リポジトリは、2024年度社会人講座向けの教材として作成されたものである。
その内容としては、Meta社が公開しているLLaMA2とLLaMA-Indexを使用してRetrieval Augmented Generation(RAG)を構築し、それをAPI経由で利用すると言ったものである。

## 具体的な機能
以下にリストアップする全ての機能をWeb-APIで使用する事が可能。
1. コンテキストを基づくベクトルデータベースの作成及びダウンロード
2. 作成したベクトルデータベースをアップロードする事で個別にRAGサービスを立ち上げることが可能
3. RAG有り・無しで推論結果を比較する事が可能
4. LLMによる推論結果の自動和訳

## ディレクトリ構成
<pre>
.
├── README.md  
├── docker-compose.yml   
├── llama2
│   └── src
│       ├── data
│       │   ├── vector_database_create
│       │   └── vector_database_upload
│       ├── llama2
│       │   ├── api_server
│       │   │   ├── access_token
│       │   │   │   └── token
│       │   │   ├── json_schema
│       │   │   │   ├── vector_database_create.json
│       │   │   │   └── vector_database_upload.json
│       │   │   ├── llama2-cpp_RAG-fastapi-standalone.py
│       │   │   ├── llama2-cpp_RAG-fastapi.py
│       │   │   └── modules
│       │   │       ├── llama2_inference.py
│       │   │       ├── vector_database_create.py
│       │   │       └── vector_database_upload.py
│       │   ├── embedding
│       │   │   ├── Easy_index_storage.py
│       │   │   ├── emb-sub.py
│       │   │   ├── embedding_langchain.py
│       │   │   └── embedding_llamaindex.py
│       │   ├── normal
│       │   │   ├── llama2-RAG.py
│       │   │   ├── llama2-cpp.py
│       │   │   ├── llama2-cpp_RAG.py
│       │   │   └── llama2.py
│       │   └── test
│       │       ├── json_to_zip.py
│       │       ├── json_upload.py
│       │       ├── jsons_json.py
│       │       ├── normal.py
│       │       ├── old__llama2-cpp_RAG-fastapi.py
│       │       ├── post.py
│       │       ├── rag.py
│       │       ├── session.py
│       │       ├── test-server.py
│       │       ├── text_file_upload.py
│       │       ├── text_to_json_upload.py
│       │       └── text_upload.py
│       ├── models
│       ├── requirements.txt
│       ├── text_data
│       │   └── sample
│       │       └── sample.txt
│       └── web_crawler
│           ├── generate_web_to_text.py
│           └── modules
│               ├── url_crawl.py
│               └── url_to_text.py
├── nllb-200
│   └── src
│       ├── models
│       ├── nllb-fastapi.py
│       ├── post.py
│       └── requirements.txt
└── proxy.env
</pre>