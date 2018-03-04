from sanic.response import json, HTTPResponse
from sanic import Blueprint
from sanic.exceptions import NotFound, RequestTimeout
from utils import auth
from service import service_test
from utils import before_request


bp_micro = Blueprint('micro')


@bp_micro.route('/micro/test/', methods=['GET', 'POST'])
@auth('token')
async def test(req):
        app_name = req.json.get('app_name')
        keywords = req.json.get('keywords')
        start_date = req.json.get('start_date')
        end_date = req.json.get('end_date')
        r = await service_test(app_name)
        return r


@bp_micro.middleware('request')
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


@bp_micro.middleware('response')
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


@bp_micro.exception(NotFound)
def ignore_404s(request, exception):
    return json("404, {} not found ".format(request.url))



@bp_micro.exception(RequestTimeout)
def timeout(request, exception):
    return json({'message': 'Request Timeout'}, 408)