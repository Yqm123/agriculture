# -*- coding:utf-8 -*-
import json
from django.http import HttpResponse
import os
from py2neo import Graph
import ahocorasick
from Model import constants


class QuestionClassifier:
    def __init__(self):

        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        # 　特征词路径
        self.concept_path = os.path.join(cur_dir, 'agriculture/dict/concept.txt')
        self.knowledge_path = os.path.join(cur_dir, 'agriculture/dict/knowledge.txt')
        self.build_path = os.path.join(cur_dir, 'agriculture/dict/build.txt')
        self.harveststore_path = os.path.join(
            cur_dir, 'agriculture/dict/harveststore.txt')
        self.management_path = os.path.join(
            cur_dir, 'agriculture/dict/management.txt')
        self.planting_path = os.path.join(cur_dir, 'agriculture/dict/planting.txt')
        self.process_path = os.path.join(cur_dir, 'agriculture/dict/process.txt')
        self.species_path = os.path.join(cur_dir, 'agriculture/dict/species.txt')
        # 加载特征词
        self.concept_wds = [i.strip() for i in open(
            self.concept_path, encoding='utf-8') if i.strip()]
        self.knowledge_wds = [i.strip() for i in open(
            self.knowledge_path, encoding='utf-8') if i.strip()]
        self.build_wds = [i.strip() for i in open(
            self.build_path, encoding='utf-8') if i.strip()]
        self.harveststore_wds = [i.strip() for i in open(
            self.harveststore_path, encoding='utf-8') if i.strip()]
        self.management_wds = [i.strip() for i in open(
            self.management_path, encoding='utf-8') if i.strip()]
        self.planting_wds = [i.strip() for i in open(
            self.planting_path, encoding='utf-8') if i.strip()]
        self.process_wds = [i.strip() for i in open(
            self.process_path, encoding='utf-8') if i.strip()]
        self.species_wds = [i.strip() for i in open(
            self.species_path, encoding='utf-8') if i.strip()]
        self.region_words = set(self.concept_wds + self.knowledge_wds + self.build_wds + self.harveststore_wds
                                + self.management_wds + self.planting_wds + self.process_wds + self.species_wds)
        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))

        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()

        # 问句疑问词
        self.character_qwds = ['特征', '表征', '特点', '表现', '什么是', '是什么', '是啥']
        self.function_qwds = ['功能', '特效', '有啥用', '能干什么', '有什么作用']
        self.rule_qwds = ['要怎么做', '如何实现', '注意事项']
        self.docu_qwds = ['文献', '文章', '资料', '参考资料', '更多信息']

        print('model init finished ......')
        return

    '''分类主函数'''

    def classify(self, question):
        data = {}
        medical_dict = self.check_medical(question)
        print("medical_dict: ", medical_dict)
        if not medical_dict:
            return {}
        data['args'] = medical_dict
        # 收集问句当中所涉及到的实体类型
        types = []
        for type_ in medical_dict.values():
            types += type_
        question_type = 'others'

        question_types = []

        # 特征
        if self.check_words(self.character_qwds, question) and ('concept' in types):
            question_type = 'concept_character'
            question_types.append(question_type)

        if self.check_words(self.character_qwds, question) and ('knowledge' in types):
            question_type = 'knowledge_character'
            question_types.append(question_type)

        if self.check_words(self.character_qwds, question) and ('build' in types):
            question_type = 'build_character'
            question_types.append(question_type)

        if self.check_words(self.character_qwds, question) and ('harveststore' in types):
            question_type = 'harveststore_character'
            question_types.append(question_type)

        if self.check_words(self.character_qwds, question) and ('management' in types):
            question_type = 'management_character'
            question_types.append(question_type)

        if self.check_words(self.character_qwds, question) and ('planting' in types):
            question_type = 'planting_character'
            question_types.append(question_type)

        if self.check_words(self.character_qwds, question) and ('process' in types):
            question_type = 'process_character'
            question_types.append(question_type)

        if self.check_words(self.character_qwds, question) and ('species' in types):
            question_type = 'species_character'
            question_types.append(question_type)

        # 功能
        if self.check_words(self.function_qwds, question) and ('concept' in types):
            question_type = 'concept_function'
            question_types.append(question_type)

        if self.check_words(self.function_qwds, question) and ('knowledge' in types):
            question_type = 'knowledge_function'
            question_types.append(question_type)

        if self.check_words(self.function_qwds, question) and ('build' in types):
            question_type = 'build_function'
            question_types.append(question_type)

        if self.check_words(self.function_qwds, question) and ('harveststore' in types):
            question_type = 'harveststore_function'
            question_types.append(question_type)

        if self.check_words(self.function_qwds, question) and ('management' in types):
            question_type = 'management_function'
            question_types.append(question_type)

        if self.check_words(self.function_qwds, question) and ('planting' in types):
            question_type = 'planting_function'
            question_types.append(question_type)

        if self.check_words(self.function_qwds, question) and ('process' in types):
            question_type = 'process_function'
            question_types.append(question_type)

        if self.check_words(self.function_qwds, question) and ('species' in types):
            question_type = 'species_function'
            question_types.append(question_type)

        # 措施
        if self.check_words(self.rule_qwds, question) and ('concept' in types):
            question_type = 'concept_rule'
            question_types.append(question_type)

        if self.check_words(self.rule_qwds, question) and ('knowledge' in types):
            question_type = 'knowledge_rule'
            question_types.append(question_type)

        if self.check_words(self.rule_qwds, question) and ('build' in types):
            question_type = 'build_rule'
            question_types.append(question_type)

        if self.check_words(self.rule_qwds, question) and ('harveststore' in types):
            question_type = 'harveststore_rule'
            question_types.append(question_type)

        if self.check_words(self.rule_qwds, question) and ('management' in types):
            question_type = 'management_rule'
            question_types.append(question_type)

        if self.check_words(self.rule_qwds, question) and ('planting' in types):
            question_type = 'planting_rule'
            question_types.append(question_type)

        if self.check_words(self.rule_qwds, question) and ('process' in types):
            question_type = 'process_rule'
            question_types.append(question_type)

        if self.check_words(self.rule_qwds, question) and ('species' in types):
            question_type = 'species_rule'
            question_types.append(question_type)
        # 相关文献
        if self.check_words(self.docu_qwds, question) and ('knowledge' in types):
            question_type = 'knowledge_docu'
            question_types.append(question_type)

        if self.check_words(self.docu_qwds, question) and ('build' in types):
            question_type = 'build_docu'
            question_types.append(question_type)

        if self.check_words(self.docu_qwds, question) and ('harveststore' in types):
            question_type = 'harveststore_docu'
            question_types.append(question_type)

        if self.check_words(self.docu_qwds, question) and ('management' in types):
            question_type = 'management_docu'
            question_types.append(question_type)

        if self.check_words(self.docu_qwds, question) and ('planting' in types):
            question_type = 'planting_docu'
            question_types.append(question_type)

        if self.check_words(self.docu_qwds, question) and ('process' in types):
            question_type = 'process_docu'
            question_types.append(question_type)

        if self.check_words(self.docu_qwds, question) and ('species' in types):
            question_type = 'species_docu'
            question_types.append(question_type)

        # 若没有查到相关的外部查询信息，那么则将该实体的描述信息返回
        if question_types == [] and 'knowledge' in types:
            question_types = ['concept_character']

        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types

        return data

    '''构造词对应的类型'''

    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.concept_wds:
                wd_dict[wd].append('concept')
            if wd in self.knowledge_wds:
                wd_dict[wd].append('knowledge')
            if wd in self.build_wds:
                wd_dict[wd].append('build')
            if wd in self.harveststore_wds:
                wd_dict[wd].append('harveststore')
            if wd in self.management_wds:
                wd_dict[wd].append('management')
            if wd in self.planting_wds:
                wd_dict[wd].append('planting')
            if wd in self.process_wds:
                wd_dict[wd].append('process')
            if wd in self.species_wds:
                wd_dict[wd].append('species')
        return wd_dict

    '''构造actree，加速过滤'''

    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''问句过滤'''

    def check_medical(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i: self.wdtype_dict.get(i) for i in final_wds}
        print("region_word: ", region_wds)
        print("question: ", question)
        return final_dict

    '''基于特征词进行分类'''

    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False


class QuestionPaser:
    # 转化成neo4j的查询语句
    '''构建实体节点'''

    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)
        print("entity_dict: ", entity_dict)
        return entity_dict

    '''解析主函数'''

    def parser_main(self, res_classify):

        args = res_classify['args']

        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            if question_type == 'concept_character':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('concept'))

            elif question_type == 'knowledge_character':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('knowledge'))

            elif question_type == 'build_character':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('build'))

            elif question_type == 'harveststore_character':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('harveststore'))

            elif question_type == 'management_character':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('management'))

            elif question_type == 'planting_character':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('planting'))

            elif question_type == 'process_character':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('process'))

            elif question_type == 'species_character':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('species'))

            elif question_type == 'concept_function':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('concept'))

            elif question_type == 'knowledge_function':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('knowledge'))

            elif question_type == 'build_function':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('build'))

            elif question_type == 'harveststore_function':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('harveststore'))

            elif question_type == 'management_function':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('management'))

            elif question_type == 'planting_function':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('planting'))

            elif question_type == 'process_function':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('process'))

            elif question_type == 'concept_rule':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('concept'))

            elif question_type == 'knowledge_rule':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('knowledge'))

            elif question_type == 'build_rule':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('build'))

            elif question_type == 'harveststore_rule':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('harveststore'))

            elif question_type == 'management_rule':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('management'))

            elif question_type == 'planting_rule':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('planting'))

            elif question_type == 'process_rule':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('process'))

            elif question_type == 'species_rule':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('process'))

            elif question_type == 'knowledge_docu':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('knowledge'))

            elif question_type == 'build_docu':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('build'))

            elif question_type == 'harveststore_docu':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('harveststore'))

            elif question_type == 'management_docu':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('management'))

            elif question_type == 'planting_docu':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('planting'))

            elif question_type == 'process_docu':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('process'))

            elif question_type == 'species_docu':
                sql = self.sql_transfer(
                    question_type, entity_dict.get('process'))
            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls

    '''针对不同的问题，分开进行处理'''

    def sql_transfer(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sql = []
        # 查询特征
        if question_type == 'concept_character':
            sql = ["MATCH (m:concept) where m.name = '{0}' return m.name, m.character".format(
                i) for i in entities]

        elif question_type == 'knowledge_character':
            sql = ["MATCH (m:枣树种植基础知识) where m.name = '{0}' return m.name, m.character".format(
                i) for i in entities]

        elif question_type == 'build_character':
            sql = ["MATCH (m:枣树建园) where m.name = '{0}' return m.name, m.character".format(
                i) for i in entities]

        elif question_type == 'harveststore_character':
            sql = ["MATCH (m:枣果采收与贮藏) where m.name = '{0}' return m.name, m.character".format(
                i) for i in entities]

        elif question_type == 'management_character':
            sql = ["MATCH (m:枣树管理) where m.name = '{0}' return m.name, m.character".format(
                i) for i in entities]

        elif question_type == 'planting_character':
            sql = ["MATCH (m:枣树育苗) where m.name = '{0}' return m.name, m.character".format(
                i) for i in entities]

        elif question_type == 'process_character':
            sql = ["MATCH (m:枣果加工) where m.name = '{0}' return m.name, m.character".format(
                i) for i in entities]

        elif question_type == 'species_character':
            sql = ["MATCH (m:品种选择) where m.name = '{0}' return m.name, m.character".format(
                i) for i in entities]
        # 查询作用
        elif question_type == 'knowledge_function':
            sql = ["MATCH (m:枣树种植基础知识) where m.name = '{0}' return m.name, m.function".format(
                i) for i in entities]

        elif question_type == 'build_function':
            sql = ["MATCH (m:枣树建园) where m.name = '{0}' return m.name, m.function".format(
                i) for i in entities]

        elif question_type == 'harveststore_function':
            sql = ["MATCH (m:枣果采收与贮藏) where m.name = '{0}' return m.name, m.function".format(
                i) for i in entities]

        elif question_type == 'management_function':
            sql = ["MATCH (m:枣树管理) where m.name = '{0}' return m.name, m.function".format(
                i) for i in entities]

        elif question_type == 'planting_function':
            sql = ["MATCH (m:枣树育苗) where m.name = '{0}' return m.name, m.function".format(
                i) for i in entities]

        elif question_type == 'process_function':
            sql = ["MATCH (m:枣果加工) where m.name = '{0}' return m.name, m.function".format(
                i) for i in entities]

        elif question_type == 'species_function':
            sql = ["MATCH (m:品种选择) where m.name = '{0}' return m.name, m.function".format(
                i) for i in entities]
        # 查询措施
        elif question_type == 'knowledge_rule':
            sql = ["MATCH (m:枣树种植基础知识) where m.name = '{0}' return m.name, m.rule".format(
                i) for i in entities]

        elif question_type == 'build_rule':
            sql = ["MATCH (m:枣树建园) where m.name = '{0}' return m.name, m.rule".format(
                i) for i in entities]

        elif question_type == 'harveststore_rule':
            sql = ["MATCH (m:枣果采收与贮藏) where m.name = '{0}' return m.name, m.rule".format(
                i) for i in entities]

        elif question_type == 'management_rule':
            sql = ["MATCH (m:枣树管理) where m.name = '{0}' return m.name, m.rule".format(
                i) for i in entities]

        elif question_type == 'planting_rule':
            sql = ["MATCH (m:枣树育苗) where m.name = '{0}' return m.name, m.rule".format(
                i) for i in entities]

        elif question_type == 'process_rule':
            sql = ["MATCH (m:枣果加工) where m.name = '{0}' return m.name, m.rule".format(
                i) for i in entities]

        elif question_type == 'species_rule':
            sql = ["MATCH (m:品种选择) where m.name = '{0}' return m.name, m.rule".format(
                i) for i in entities]
        # 查询相关文献
        elif question_type == 'knowledge_docu':
            sql = ["MATCH (m:枣树种植基础知识)-[文献]-(n:枣树种植基础知识) where n.name='{0}' \
                    return m.name, m.`i s s n`,m.`摘   要`".format(i) for i in entities]

        elif question_type == 'build_docu':
            sql = ["MATCH (m:枣树建园)-[文献]-(n:枣树建园) where n.name='{0}' \
                    return m.name, m.`i s s n`,m.`摘   要`".format(i) for i in entities]

        elif question_type == 'harveststore_docu':
            sql = ["MATCH (m:枣果采收与贮藏)-[文献]-(n:枣果采收与贮藏) where n.name='{0}' \
                    return m.name, m.`i s s n`,m.`摘   要`".format(i) for i in entities]

        elif question_type == 'management_docu':
            sql = ["MATCH (m:枣树管理)-[文献]-(n:枣树管理) where n.name='{0}' \
                    return m.name, m.`i s s n`,m.`摘   要`".format(i) for i in entities]

        elif question_type == 'planting_docu':
            sql = ["MATCH (m:枣树育苗)-[文献]-(n:枣树育苗) where n.name='{0}' \
                    return m.name, m.`i s s n`,m.`摘   要`".format(i) for i in entities]

        elif question_type == 'process_docu':
            sql = ["MATCH (m:枣果加工)-[文献]-(n:枣果加工) where n.name='{0}' \
                    return m.name, m.`i s s n`,m.`摘   要`".format(i) for i in entities]

        elif question_type == 'species_docu':
            sql = ["MATCH (m:品种选择)-[文献]-(n:品种选择) where n.name='{0}' \
                    return m.name, m.`i s s n`,m.`摘   要`".format(i) for i in entities]

        return sql

    '''解析主函数2'''

    def parser_main2(self, res_classify):
        args = res_classify['args']
        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            if question_type == 'concept_character':
                sql = self.sqll_tupu(question_type, entity_dict.get('concept'))

            elif question_type == 'knowledge_character':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('knowledge'))

            elif question_type == 'build_character':
                sql = self.sqll_tupu(question_type, entity_dict.get('build'))

            elif question_type == 'harveststore_character':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('harveststore'))

            elif question_type == 'management_character':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('management'))

            elif question_type == 'planting_character':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('planting'))

            elif question_type == 'process_character':
                sql = self.sqll_tupu(question_type, entity_dict.get('process'))

            elif question_type == 'species_character':
                sql = self.sqll_tupu(question_type, entity_dict.get('species'))

            elif question_type == 'concept_function':
                sql = self.sqll_tupu(question_type, entity_dict.get('concept'))

            elif question_type == 'knowledge_function':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('knowledge'))

            elif question_type == 'build_function':
                sql = self.sqll_tupu(question_type, entity_dict.get('build'))

            elif question_type == 'harveststore_function':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('harveststore'))

            elif question_type == 'management_function':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('management'))

            elif question_type == 'planting_function':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('planting'))

            elif question_type == 'process_function':
                sql = self.sqll_tupu(question_type, entity_dict.get('process'))

            elif question_type == 'concept_rule':
                sql = self.sqll_tupu(question_type, entity_dict.get('concept'))

            elif question_type == 'knowledge_rule':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('knowledge'))

            elif question_type == 'build_rule':
                sql = self.sqll_tupu(question_type, entity_dict.get('build'))

            elif question_type == 'harveststore_rule':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('harveststore'))

            elif question_type == 'management_rule':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('management'))

            elif question_type == 'planting_rule':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('planting'))

            elif question_type == 'process_rule':
                sql = self.sqll_tupu(question_type, entity_dict.get('process'))

            elif question_type == 'species_rule':
                sql = self.sqll_tupu(question_type, entity_dict.get('process'))

            elif question_type == 'knowledge_docu':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('knowledge'))

            elif question_type == 'build_docu':
                sql = self.sqll_tupu(question_type, entity_dict.get('build'))

            elif question_type == 'harveststore_docu':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('harveststore'))

            elif question_type == 'management_docu':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('management'))

            elif question_type == 'planting_docu':
                sql = self.sqll_tupu(
                    question_type, entity_dict.get('planting'))

            elif question_type == 'process_docu':
                sql = self.sqll_tupu(question_type, entity_dict.get('process'))

            elif question_type == 'species_docu':
                sql = self.sqll_tupu(question_type, entity_dict.get('process'))
            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls

    '''返回特定格式，用于展示图谱'''

    def sqll_tupu(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sqll = ["MATCH (n1)- [rel] -> (n2) where n1.name = '{0}' \
            return n1, rel, n2, labels(n1), labels(n2)".format(i) for i in entities]
        return sqll


class AnswerSearcher:
    def __init__(self):
        self.g = Graph(constants.BASE_URL, auth=("neo4j", constants.password))
        self.num_limit = 30

    '''执行cypher查询，并返回相应结果'''

    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                ress = self.g.run(query).data()
                answers += ress
                print(answers)
            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers

    '''不改格式，得到原始答案'''

    def search_main2(self, sqls):

        final_answers = []
        for sql_ in sqls:
            queries = sql_['sql']
            answers = []
            for query in queries:
                ress = self.g.run(query).data()
                answers += ress
            final_answer = answers
            if final_answer:
                final_answers.append(final_answer)
        print(final_answers)
        return final_answers

    '''根据对应的qustion_type，调用相应的回复模板'''

    def answer_prettify(self, question_type, answers):
        final_answer = []
        answer = ''
        if not answers:
            return ['没有相关信息']
        if question_type == 'concept_character':
            final_answer = answers
        elif question_type == 'knowledge_character':
            desc = [i['m.character'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的特点有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'knowledge_function':
            desc = [i['m.function'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的功能有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'knowledge_rule':
            desc = [i['m.rule'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的注意事项有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'build_character':
            desc = [i['m.character'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的特点有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'build_function':
            desc = [i['m.function'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的功能有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'build_rule':
            desc = [i['m.rule'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的注意事项有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'process_character':
            desc = [i['m.character'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的特点有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'process_function':
            desc = [i['m.function'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的功能有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'process_rule':
            desc = [i['m.rule'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的注意事项有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'species_character':
            desc = [i['m.character'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的特点有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'species_function':
            desc = [i['m.function'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的功能有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'species_rule':
            desc = [i['m.rule'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的注意事项有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'harveststore_character':
            desc = [i['m.character'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的特点有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'harveststore_function':
            desc = [i['m.function'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的功能有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'harveststore_rule':
            desc = [i['m.rule'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的注意事项有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'management_character':
            desc = [i['m.character'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的特点有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'management_function':
            desc = [i['m.function'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的功能有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'management_rule':
            desc = [i['m.rule'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的注意事项有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'planting_character':
            desc = [i['m.character'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的特点有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'planting_function':
            desc = [i['m.function'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的功能有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'planting_rule':
            desc = [i['m.rule'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的注意事项有：{1}'.format(
                subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'knowledge_docu':
            nn = [i['m.name'] for i in answers]
            issn = [j['m.`i s s n`'] for j in answers]
            digest = [i['m.`摘   要`'] for i in answers]
            for i in range(5):
                answer += '标题：'
                answer += str(nn[i])
                answer += ',摘要：'
                answer += str(digest[i] + '\n')
            final_answer = answer
        elif question_type == 'build_docu':
            nn = [i['m.name'] for i in answers]
            issn = [j['m.`i s s n`'] for j in answers]
            digest = [i['m.`摘   要`'] for i in answers]
            # final_answer = '相关资料有：{0}'.format(list(it.chain(*zip(nn,digest))))
            for i in range(5):
                answer += '标题：'
                answer += str(nn[i])
                answer += ',摘要：'
                answer += str(digest[i])
                answer += '\n'

        elif question_type == 'harveststore_docu':
            nn = [i['m.name'] for i in answers]
            issn = [j['m.`i s s n`'] for j in answers]
            digest = [i['m.`摘   要`'] for i in answers]
            for i in range(len(nn)):
                answer += '标题：'
                answer += str(nn[i])
                answer += ',摘要：'
                answer += str(digest[i])
                answer += '\n'

        elif question_type == 'management_docu':
            nn = [i['m.name'] for i in answers]
            issn = [j['m.`i s s n`'] for j in answers]
            digest = [i['m.`摘   要`'] for i in answers]
            # final_answer = '相关资料有：{0}'.format(list(it.chain(*zip(nn,digest))))
            for i in range(5):
                answer += '标题：'
                answer += str(nn[i])
                answer += ',摘要：'
                answer += str(digest[i])
                answer += '\n'

        elif question_type == 'planting_docu':
            nn = [i['m.name'] for i in answers]
            issn = [j['m.`i s s n`'] for j in answers]
            digest = [i['m.`摘   要`'] for i in answers]
            # final_answer = '相关资料有：{0}'.format(list(it.chain(*zip(nn,digest))))
            for i in range(5):
                answer += '标题：'
                answer += str(nn[i])
                answer += ',摘要：'
                answer += str(digest[i])
                answer += '\n'

        elif question_type == 'process_docu':
            nn = [i['m.name'] for i in answers]
            issn = [j['m.`i s s n`'] for j in answers]
            digest = [i['m.`摘   要`'] for i in answers]
            # final_answer = '相关资料有：{0}'.format(list(it.chain(*zip(nn,digest))))
            for i in range(5):
                answer += '标题：'
                answer += str(nn[i])
                answer += ',摘要：'
                answer += str(digest[i])
                answer += '\n'

        elif question_type == 'species_docu':
            nn = [i['m.name'] for i in answers]
            issn = [j['m.`i s s n`'] for j in answers]
            digest = [i['m.`摘   要`'] for i in answers]
            # final_answer = '相关资料有：{0}'.format(list(it.chain(*zip(nn,digest))))
            for i in range(5):
                answer += '标题：'
                answer += str(nn[i])
                answer += ',摘要：'
                answer += str(digest[i])
                answer += '\n'
            final_answer = answer
        print(final_answer)
        return final_answer


class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        res_classify = self.classifier.classify(sent)
        print("res_classify: ", res_classify)
        if not res_classify:
            return -1, -1
        res_sql = self.parser.parser_main(res_classify)
        print("res_sql: ", res_sql)
        final_answers = self.searcher.search_main(res_sql)
        sql_tupu = self.parser.parser_main2(res_classify)
        tupu_answers = self.searcher.search_main2(sql_tupu)
        # if len(tupu_answers)==0:
        #     entity_dict = self.parser.build_entitydict('knowledge')
        #     tupu_answers = self.searcher.g.run("MATCH (entity1)- [rel] -> (entity2) where entity2.name = '{0}' \
        #         return entity1, rel, entity2".format(i) for i in entity_dict.get('knowledge')).data()
        return final_answers, tupu_answers


def question_answering(request):  # index页面需要一开始就加载的内容写在这里
    answer = '您好，我是你的种植助理，希望可以帮到您。如果没答上来，可以搜索：www.baidu.com,祝您的枣树棒棒！'
    try:
        if request.GET:
            question = request.GET['question']
            handler = ChatBotGraph()
            print(question)
            ret_dict, ret_tupu = handler.chat_main(question)
            res = list()
            if ret_dict == -1:
                res.append([answer])
            elif len(ret_dict) != 0 and ret_dict != 0 and len(ret_tupu) != 0:
                res.append(ret_dict)
                res.append(ret_tupu)
            elif len(ret_dict) != 0 and ret_dict != 0 and len(ret_tupu) == 0:
                res.append(ret_dict)
            return HttpResponse(json.dumps(res, ensure_ascii=False))
    except Exception as e:
        return HttpResponse(json.dumps(-1, ensure_ascii=False))