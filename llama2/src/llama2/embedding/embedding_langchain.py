from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader

target_file_path = "test.txt"
model_path = "/src/models/multilingual-e5-large"
outpub_path = "faiss_chunk"

loader = TextLoader(target_file_path, encoding='utf-8')
documents = loader.load()

text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    separator = "\n",
    chunk_size=300,
    chunk_overlap=20,
)

texts = text_splitter.split_documents(documents)
print(len(texts))
print(texts)

embeddings = HuggingFaceEmbeddings(model_name=model_path)
db = FAISS.from_documents(texts, embeddings)
db.save_local(outpub_path)