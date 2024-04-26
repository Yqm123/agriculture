from Model.pre_load import neo_con
from django.http import HttpResponse
import json


def getNodesNum(request):
    db = neo_con
    data = db.matchNodes()
    return HttpResponse(json.dumps(data, ensure_ascii = False))


def getRelationNum(request):
    db = neo_con
    data = db.matchRelation()
    return HttpResponse(json.dumps(data, ensure_ascii = False))
