from fastapi import FastAPI, HTTPException
from typing import Optional
import asyncio
import uuid
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# セッションIDと非同期プロセスを管理するための辞書
sessions = {}


class AsyncProcess:
    def __init__(self, expiration_time):
        self.expiration_time = expiration_time

    async def process(self, data):
        await asyncio.sleep(1)  # 仮の非同期処理
        return f"Processed data: {data}. Expiration time: {self.expiration_time}"


async def create_async_process():
    expiration_time = datetime.now() + timedelta(minutes=10)  # 10分後に有効期限切れ
    return AsyncProcess(expiration_time)


@app.get("/process/")
async def process_data(session_id: str, data: int):
    if session_id not in sessions or sessions[session_id]["expiration_time"] < datetime.now():
        # 新しい非同期プロセスを作成し、セッションに関連付ける
        async_process = await create_async_process()
        sessions[session_id] = {"async_process": async_process, "expiration_time": async_process.expiration_time}

    async_process = sessions[session_id]["async_process"]
    result = await async_process.process(data)
    return JSONResponse(content=result, headers={"Access-Control-Allow-Origin": "*"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=49152)