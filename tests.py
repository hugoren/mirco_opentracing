import json
import requests

def test_micro_opentracing():
    url = "http://localhost:10020/micro/test/"
    token = "b0350c8c75ddcd99738df4c9346bec48dc9c4914"
    r = requests.get(url, data=json.dumps({"app_name": "test"}), headers={'Content-Type': 'application/json', 'token': token}).json()
    print(r)

test_micro_opentracing()