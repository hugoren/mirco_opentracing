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


@bp_micro.exception(NotFound)
def ignore_404s(request, exception):
    return json("404, {} not found ".format(request.url))



@bp_micro.exception(RequestTimeout)
def timeout(request, exception):
    return json({'message': 'Request Timeout'}, 408)