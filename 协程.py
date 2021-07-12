from time import sleep

from flask import Flask, jsonify, has_request_context, copy_current_request_context
from functools import wraps
from concurrent.futures import Future, ThreadPoolExecutor
import asyncio


def run_async(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        call_result = Future()

        def _run():
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(func(*args, **kwargs))
            except Exception as error:
                call_result.set_exception(error)
            else:
                call_result.set_result(result)
            finally:
                loop.close()

        loop_executor = ThreadPoolExecutor(max_workers=10)
        if has_request_context():
            _run = copy_current_request_context(_run)
        loop_future = loop_executor.submit(_run)
        loop_future.result()
        return call_result.result()

    return _wrapper


app = Flask(__name__)



async def slp(n):
    sleep(n)
    return "r"

@app.route('/async')
@run_async
async def index():
    n=10
    r = await slp(n)
    return jsonify('hello,async')


@app.route('/sync')
def aindex():
    sleep(1)
    return jsonify('hello,sync')


import logging

# logging.getLogger('werkzeug').setLevel(logging.ERROR)
app.run(port=8000)