import asyncio
import opentracing
from sanic.response import json, HTTPResponse
from sanic.exceptions import RequestTimeout, NotFound
from sanic import Sanic
from basictracer import BasicTracer
from utils import consume, before_request
from logger import AioReporter
from db import ConnectionPool
from endpoint import bp_micro
from loadConfig import load_config

app = Sanic(__name__)
app.config = load_config()
app.blueprint(bp_micro)


@app.listener('before_server_start')
async def before_srver_start(app, loop):
    queue = asyncio.Queue()
    app.queue = queue
    loop.create_task(consume(queue, app.config.get("ZIPKIN_SERVER")))
    reporter = AioReporter(queue=queue)
    tracer = BasicTracer(recorder=reporter)
    tracer.register_required_propagators()
    opentracing.tracer = tracer
    config = app.config.get("DB_CONFIG")
    app.db = await ConnectionPool(loop=loop).init(config)


@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    app.queue.join()


@app.middleware('request')
async def cros(request):
    config = request.app.config
    if request.method == 'OPTIONS':
        headers = {'Access-Control-Allow-Origin': config['ACCESS_CONTROL_ALLOW_ORIGIN'],
                   'Access-Control-Allow-Headers': config['ACCESS_CONTROL_ALLOW_HEADERS'],
                   'Access-Control-Allow-Methods': config['ACCESS_CONTROL_ALLOW_METHODS']}
        return json({'code': 0}, headers=headers)
    if request.method == 'POST' or request.method == 'PUT':
        request['data'] = request.json
    span = before_request(request)
    request['span'] = span


@app.middleware('response')
async def cors_res(request, response):
    config = request.app.config
    span = request['span'] if 'span' in request else None
    if response is None:
        return response
    result = {'code': 0}
    if not isinstance(response, HTTPResponse):
        if isinstance(response, tuple) and len(response) == 2:
            result.update({
                'data': response[0],
                'pagination': response[1]
            })
        else:
            result.update({'data': response})
        response = json(result)
        if span:
            span.set_tag('http.status_code', "200")
    if span:
        span.set_tag('component', request.app.name)
        span.finish()
    response.headers["Access-Control-Allow-Origin"] = config['ACCESS_CONTROL_ALLOW_ORIGIN']
    response.headers["Access-Control-Allow-Headers"] = config['ACCESS_CONTROL_ALLOW_HEADERS']
    response.headers["Access-Control-Allow-Methods"] = config['ACCESS_CONTROL_ALLOW_METHODS']
    return response


@app.exception(RequestTimeout)
def timeout(request, exception):
    return json({'message': 'Request Timeout'}, 408)


@app.exception(NotFound)
def notfound(request, exception):
    return json(
        {'message': 'Requested URL {} not found'.format(request.url)}, 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', workers=2, port=10020, debug=True)