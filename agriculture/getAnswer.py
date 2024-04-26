import json
import requests
from django.http import HttpResponse


def get(request):
    res = list()
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=2KM5SrFfjntHsnF88masf1a7' \
           '&client_secret=7yQxAgGufWTYaHhkVqIFhrDVa2pCrHbH'
    response = requests.get(host)
    if response:
        token = response.json()['access_token']
        host = 'https://aip.baidubce.com/rpc/2.0/ai_custom_bml/v1/sequence_label/nerForJujube' + '?access_token=' + token
        params = {
            'text': request.GET['text']
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url=host, headers=headers, json=params)
        res.append(response.json()['label'])
        res.append(response.json()['raw_text'])
        return HttpResponse(json.dumps(res, ensure_ascii=False))
