from py2neo import Graph
from . import constants

class Neo4j:
    # graph = None
    def __init__(self):
        print("create neo4j class ...")

    def connectDB(self):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        return self

    def createNode_Rel(self, n1, relation, n2, label):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))

        if n1 != "":
            node1 = n1.split(",")
            for node in node1:
                res = self.run("MATCH (n:`" + str(label) + "` {name:'" + str(node) + "'}) return count(n)").data()
                if res[0]["count(n)"] == 0:
                    self.run("CREATE (n:`" + str(label) + "` {name:'" + str(node) + "'}) return n").data()
        if n2 != "":
            node2 = n2.split(",")
            for node in node2:
                res = self.run("MATCH (n:`" + str(label) + "`{name:'" + str(node) + "'}) return count(n)").data()
                if res[0]["count(n)"] == 0:
                    self.run("CREATE (n:`" + str(label) + "`{name:'" + str(node) + "'})").data()
        if n1 != "" and n2 != "" and relation != "":
            for n1 in node1:
                for n2 in node2:
                    self.run("MATCH (a:`" + str(label) + "`),(b:`" + str(label) + "`)" +
                             " WHERE a.name= '" + str(n1) + "' AND b.name= '" + str(n2) +
                             "' CREATE (a)-[r:`" + str(relation) + "` {name: '" + str(
                        relation) + "'}] -> (b) return r")
        return "创建成功"

    def deleteNode(self, node, label):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        if node != "":
            nodes = node.split(",")
            for n in nodes:
                self.run("MATCH (n:`" + str(label) + "` {name:'" + n + "'}) DETACH DELETE n")
            return "删除节点成功"

    def deleteRel(self, n1, n2, label):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))

        if n1 != "":
            node1 = n1.split(",")
        if n2 != "":
            node2 = n2.split(",")
        if n1 != "" and n2 != "":
            for n1 in node1:
                for n2 in node2:
                    self.run("MATCH (n1:`" + str(label) + "` {name:'" + n1 + "'})-[r]->(n2:`" + str(
                        label) + "` {name:'" + n2 + "'}) DELETE r")
        return "删除关系成功"

    def deleteGraph(self, label):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        self.run("MATCH (n:`" + label + "`) DETACH DELETE n")
        return "删除图谱成功"

    def getDataByLabel(self, name):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        answer = self.run(
            "MATCH (n1:`" + str(name) + "`)- [rel] -> (n2:`" + str(name) + "`) return n1,rel,n2").data()
        return answer

    def getOtherNodes(self, name):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        answer = self.run("match (n:`" + str(name) + "`) where not(n)-[]-() return n ").data()
        return answer

    def getALabels(self):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        answer = self.run(
            "MATCH (n) RETURN distinct labels(n)").data()
        return answer

    def matchNodes(self):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        answer = self.run(
            "MATCH (n) RETURN count(n),labels(n)").data()
        return answer

    def matchRelation(self):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        answer = self.run(
            "MATCH ()-[rel]-() RETURN count(rel)").data()
        return answer

    def matchItemByName(self, name):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        if len(name) != 0:
            answer = self.run(
                "MATCH (n1:`" + str(name) + "`)- [rel] -> (n2)  RETURN n1,rel,n2,labels(n1),labels(n2)").data()
        elif len(name) == 0:
            answer = self.run(
                "MATCH (n1)- [rel] -> (n2) WHERE labels(n1) in [['品种选择'],['枣果加工'],['枣果采收与贮藏'],['枣树建园'],['枣树种植基础知识'],"
                "['枣树管理'],['枣树育苗'] ] RETURN n1,rel,n2,labels(n1),labels(n2)").data()
        return answer

    def matchHudongItembyTitle(self, value):
        sql = "MATCH (n:HudongItem { title: '" + str(value) + "' }) return n;"
        try:
            answer = self.run(sql).data()
        except:
            print(sql)
        return answer

    # 关系查询:实体1
    def findRelationByEntity1(self, entity1):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))

        answer = self.run(
            "MATCH (n1 {name:\"" + entity1 + "\"})- [rel] -> (n2)  RETURN n1,rel,n2,labels(n1),labels(n2)").data()
        return answer

    # 关系查询：实体1+关系
    def findOtherEntities(self, entity, relation):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        answer = self.run(
            "MATCH (n1 {name:\"" + entity + "\"})-[rel {name:\"" + relation + "\"}]-> (n2) RETURN n1,rel,n2,labels(n1),labels(n2)").data()
        return answer

        # 关系查询：实体2+关系

    def findOtherEntities2(self, entity, relation):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        answer = self.run(
            "MATCH (n1)-[rel {name:\"" + relation + "\"}]-> (n2 {name:\"" + entity + "\"}) RETURN n1,rel,n2,labels(n1),labels(n2)").data()
        return answer

    # 关系查询 整个知识图谱体系

    def zhishitupu(self):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        answer = self.run("MATCH (n1)- [rel] -> (n2) RETURN n1,rel,n2,labels(n1),labels(n2) ").data()

        return answer

    # 关系查询：实体2

    def findRelationByEntity2(self, entity1):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))

        answer = self.run(
            "MATCH (n1)- [rel] -> (n2{name:\"" + entity1 + "\"})  RETURN n1,rel,n2,labels(n1),labels(n2)").data()
        return answer

    def findEntityRelation(self, entity1, relation, entity2):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        answer = self.run(
            "MATCH (n1 {name:\"" + entity1 + "\"})- [rel {name:\"" + relation + "\"}] -> (n2{name:\"" + entity2 + "\"}) RETURN n1,rel,n2,labels(n1),labels(n2)").data()
        return answer

    def findRelationByEntities(self, entity1, entity2):
        self = Graph(constants.BASE_URL, auth = ("neo4j", constants.password))
        answer = self.run(
            "MATCH (n1 {name:\"" + entity1 + "\"})- [rel] -> (n2{name:\"" + entity2 + "\"}) RETURN n1,rel,n2,labels(n1),labels(n2)").data()
        return answer
