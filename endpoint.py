from sanic.response import json
from sanic import Blueprint
from utils import auth
from service import service_test


bp_micro = Blueprint('micro')


@bp_micro.route('/micro/test/', methods=['GET', 'POST'])
@auth('token')
async def test(req):
    print(req)
    app_name = req.json.get('app_name')
    keywords = req.json.get('keywords')
    start_date = req.json.get('start_date')
    end_date = req.json.get('end_date')
    r = await service_test(app_name)
    return json("success")

