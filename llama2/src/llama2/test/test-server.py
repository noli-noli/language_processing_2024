import asyncio
from fastapi import FastAPI
from datetime import datetime, timedelta
from fastapi import FastAPI, UploadFile, File
from typing import List
from jsonschema import validate, ValidationError
import random
import string
import json
import os
import uvicorn
#日本語入力用モジュール
import readline

app = FastAPI()

"""
@app.get("/database_to_create")
async def database_to_create(text: str):
    Uploaddir = "/src/llama_tmp"
    save_file = "/src/llama2/test/tmp_1/combined-1.json"
    # 辞書を初期化
    combined_data = {}
    for filename in os.listdir(os.path.join(Uploaddir)):
        if filename.endswith('.json'):
            # JSONファイルのパス
            file_path = os.path.join(os.path.join(Uploaddir), filename)
            # JSONファイルを読み込んで辞書に追加
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                combined_data[filename] = json_data

    return combined_data
"""

    

@app.post("/vector_database_upload/")
async def vector_database_upload(file: UploadFile = File(...)):
    Uploaddir = "/src/llama2/test/tmp_1/"

    try:
        contents = await file.read()
        with open(os.path.join(Uploaddir,file.filename), "wb") as f:
            f.write(contents)
    except Exception as e:
        return "error"

    return "success"
    


@app.post("/vector_database_create/")
async def vector_database_create(file: UploadFile = File(...)):
    Uploaddir = "/src/llama2/test/tmp_1/"

    try:
        contents = await file.read()
        with open(os.path.join(Uploaddir,file.filename), "wb") as f:
            f.write(contents)
    except Exception as e:
        return "error"
    
    return "success"



@app.post("/schema_check/")
async def context(file: UploadFile = File(...)):
    Uploaddir = "/src/llama2/test/tmp_1/"
    access_token = "qjEjdLSBKdmCBrbg44iWFKia23cQYvJL"

    with open('/src/json_schema/schema_check.json') as file_obj:
        json_schema = json.load(file_obj)

    contents = await file.read()
    json_data = json.loads(contents)
    file_size = len(contents) / 1024


    if json_data["key"] != access_token:
        return "key doesn't match"
    
    try:
        validate(json_data, json_schema)
        return "success"
    except ValidationError as e:
        return "json schema error"


    try:
        contents = await file.read()
        for key, value in json_data.items():
            with open(os.path.join(Uploaddir,key), "w") as f:
                pass  
    except Exception as e:
        return "error"

    return "success"



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=49152)