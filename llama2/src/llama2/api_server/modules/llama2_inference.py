import requests
from fastapi import status
import re
from datetime import datetime,timedelta
from llama_index import StorageContext, load_index_from_storage
from llama_index import PromptTemplate

class MainProcess:
    def __init__(self,expiration_time,path,service_context):
        print("##### new process created #####")
        self.path = path
        self.expiration_time = expiration_time

        # storage contextの再構築
        self.storage_context = StorageContext.from_defaults(persist_dir=self.path)
        # service contextの再構築
        self.service_context = service_context

        # 保存したindexの読み込み
        self.index = load_index_from_storage(self.storage_context,  self.service_context)

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
        #event_pairs = llama_debug.get_llm_inputs_outputs()
        print("\n## Answer: \n", str(res_msg).strip())
        return str(res_msg).strip()
    


async def create_async_process(path,service_context):
    expiration_time = datetime.now() + timedelta(minutes=1440)  # 10分後に有効期限切れ
    return MainProcess(expiration_time,path,service_context)
    


async def nllb_post(text,input_code,output_code,max_length):
    # 翻訳APIのURL
    url = "http://133.89.44.20:49153/text/"

    # アルファベット、数字、ピリオド、カンマ、日本語、空白以外の文字を削除する正規表現パターン
    clean_text = re.sub(r'[^\w.,\u3000-\u30FF\u3040-\u309F\u4E00-\u9FFF\s]', '', text)
    response = requests.get(url + f"?text={clean_text}&input_code={input_code}&output_code={output_code}&max_length={max_length}")
    clean_text = re.sub("\"", "", response.text)
    return clean_text



async def normal(llm,prompt,key,access_token,response):
    if key != access_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "アクセスキーが不正です。"
    result = llm.complete("貴方は日本語で話す優秀なチャットボットです。次の質問に答えなさい。" + prompt)
    #即興で翻訳APIへのリクエストeng_Latn
    result = await nllb_post(result.text,"eng_Latn","jpn_Jpan",1000)
    result = re.sub("\"", "", result)

    return result



async def rag(prompt,key,access_token,response,sessions,session_id):
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