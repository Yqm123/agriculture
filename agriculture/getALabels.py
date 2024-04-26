from Model.pre_load import neo_con
from django.http import HttpResponse
import json


def getALabels(request):
    db = neo_con
    data = db.getALabels()
    return HttpResponse(json.dumps(data, ensure_ascii=False))