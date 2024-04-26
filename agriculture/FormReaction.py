from Model.pre_load import neo_con
from django.http import HttpResponse
import json


def create(request):
    db = neo_con
    node1 = request.GET['node1']
    node2 = request.GET['node2']
    relation = request.GET['relation']
    label = request.GET['label']
    data = db.createNode_Rel(node1, relation, node2, label)
    return HttpResponse(json.dumps(data, ensure_ascii = False))


def deleteNode(request):
    db = neo_con
    node = request.GET['node']
    label = request.GET['label']
    data = db.deleteNode(node, label)
    return HttpResponse(json.dumps(data, ensure_ascii = False))


def deleteRel(request):
    db = neo_con
    node1 = request.GET['node1']
    node2 = request.GET['node2']
    label = request.GET['label']
    data = db.deleteRel(node1, node2, label)
    return HttpResponse(json.dumps(data, ensure_ascii = False))


def deleteGraph(request):
    db = neo_con
    label = request.GET['label']
    data = db.deleteGraph(label)
    return HttpResponse(json.dumps(data, ensure_ascii = False))
