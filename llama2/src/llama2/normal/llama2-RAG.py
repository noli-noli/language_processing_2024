from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline,BitsAndBytesConfig
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from langchain import PromptTemplate
import torch

#日本語入力用モジュール
import readline

model_id = "/src/models/Llama-2-13b-chat-hf"
faiss_index = "/src/faiss_index"
embeddings = HuggingFaceEmbeddings(model_name="/src/models/multilingual-e5-large")
db = FAISS.load_local(faiss_index, embeddings)
retriever = db.as_retriever(search_kwargs={"k": 3})

quantization_config = BitsAndBytesConfig(
    load_in_4bit=False,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    quantization_config=quantization_config,
).eval()

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = "参考情報を元に、ユーザーからの質問にできるだけ正確に答えてください。"
text = "{context}\nユーザからの質問は次のとおりです。{question}"
template = "{bos_token}{b_inst} {system}{prompt} {e_inst} ".format(
    bos_token=tokenizer.bos_token,
    b_inst=B_INST,
    system=f"{B_SYS}{DEFAULT_SYSTEM_PROMPT}{E_SYS}",
    prompt=text,
    e_inst=E_INST,
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
)
PROMPT = PromptTemplate(
    template=template,
    input_variables=["context", "question"],
    template_format="f-string"
)

chain_type_kwargs = {"prompt": PROMPT}

qa = RetrievalQA.from_chain_type(
    llm=HuggingFacePipeline(
        pipeline=pipe,
        # model_kwargs=dict(temperature=0.1, do_sample=True, repetition_penalty=1.1)
    ),
    retriever=retriever,
    chain_type="stuff",
    return_source_documents=True,
    chain_type_kwargs=chain_type_kwargs,
    verbose=True,
)

while True:
    query = input("質問を入力してください: ")
    result = qa(query)
    print('回答:', result['result'])
    print('='*10)
    print('ソース:', result['source_documents'])