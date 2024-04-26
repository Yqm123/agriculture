from Model.pre_load import neo_con
from django.http import HttpResponse
import json


def getDataByLabel(request):
    db = neo_con
    name = request.GET['name']
    data = db.getDataByLabel(name)
    return HttpResponse(json.dumps(data, ensure_ascii = False))


def getOtherNodes(request):
    db = neo_con
    name = request.GET['name']
    data = db.getOtherNodes(name)
    return HttpResponse(json.dumps(data, ensure_ascii = False))
