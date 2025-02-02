import time
import json
from datetime import datetime, UTC
from fastapi import Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.concurrency import iterate_in_threadpool
from util.filesupport import save_log_file


async def save_log(request: Request, response: StreamingResponse, process_time: float, response_body: str):

    line = {
                "created": datetime.now(tz=UTC).strftime("%Y-%m-%d, %H:%M:%S"),
                "ip_address": request.client.host,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "query_params": json.dumps(dict(request.query_params)),
                "path_params": json.dumps(request.path_params),
                "process_time": process_time}

    if response_body is None:
        prefix="api"
    else:
        prefix="exception"
        line.update({"response_body": response_body})

    data = f"{json.dumps(line)}\n"
    await save_log_file(prefix=prefix, line_context=data)


class MonitoringAPIMiddleware:

    def __init__(self):
        self.success_status_codes = [200, 201]


    async def convert_response_body(self, response: StreamingResponse) -> str:
        response_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))
        return response_body[0].decode()


    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = round(time.time() - start_time, 4)
        response_body = None
        if response.status_code not in self.success_status_codes:
            response_body = await self.convert_response_body(response=response)
        background_task = BackgroundTasks()
        background_task.add_task(save_log, request, response, process_time, response_body)
        response.background = background_task
        return response
