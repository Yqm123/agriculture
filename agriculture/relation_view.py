# -*- coding: utf-8 -*-
from django.http import HttpResponse
from Model.pre_load import neo_con

import json

def search_relation(request):
    ctx = {}
    if request.GET:
        db = neo_con
        entity1 = request.GET['entity1']
        relation = request.GET['relation']
        entity2 = request.GET['entity2']
        relation = relation.lower()
        searchResult = {}

        # 若只输入entity1,则输出与entity1有直接关系的实体和关系
        if len(entity1) != 0 and len(relation) == 0 and len(entity2) == 0:
            searchResult = db.findRelationByEntity1(entity1)
            if len(searchResult) > 0:
                return HttpResponse(json.dumps(searchResult, ensure_ascii = False))
        # 若只输入entity2则,则输出与entity2有直接关系的实体和关系
        if len(entity2) != 0 and len(relation) == 0 and len(entity1) == 0:
            searchResult = db.findRelationByEntity2(entity2)
            if len(searchResult) > 0:
                return HttpResponse(json.dumps(searchResult, ensure_ascii = False))
        # 若输入entity1和relation，则输出与entity1具有relation关系的其他实体
        if len(entity1) != 0 and len(relation) != 0 and len(entity2) == 0:
            searchResult = db.findOtherEntities(entity1, relation)
            # searchResult = sortDict(searchResult)
            if len(searchResult) > 0:
                return HttpResponse(json.dumps(searchResult, ensure_ascii = False))
        # 若输入entity2和relation，则输出与entity2具有relation关系的其他实体
        if len(entity2) != 0 and len(relation) != 0 and len(entity1) == 0:
            searchResult = db.findOtherEntities2(entity2, relation)
            # searchResult = sortDict(searchResult)
            if len(searchResult) > 0:
                return HttpResponse(json.dumps(searchResult, ensure_ascii = False))

        # 若输入entity1和entity2,则输出entity1和entity2之间的最短路径
        if len(entity1) != 0 and len(relation) == 0 and len(entity2) != 0:
            searchResult = db.findRelationByEntities(entity1, entity2)
            if len(searchResult) > 0:
                # searchResult = sortDict(searchResult)
                return HttpResponse(json.dumps(searchResult, ensure_ascii = False))
        # 若输入entity1,entity2和relation,则输出entity1、entity2是否具有相应的关系
        if len(entity1) != 0 and len(entity2) != 0 and len(relation) != 0:
            searchResult = db.findEntityRelation(entity1, relation, entity2)
            if len(searchResult) > 0:
                return HttpResponse(json.dumps(searchResult, ensure_ascii = False))
        # 全为空
        if len(entity1) == 0 and len(relation) == 0 and len(entity2) == 0:
            searchResult = db.zhishitupu()
        return HttpResponse(json.dumps(searchResult, ensure_ascii = False))

    return HttpResponse({ctx: 'ctx'})
