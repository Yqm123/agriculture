from Model.pre_load import neo_con

from django.http import HttpResponse
import json


def get(request):
    db = neo_con
    name = request.GET['name']
    data = db.matchItemByName(name)
    return HttpResponse(json.dumps(data, ensure_ascii = False))
