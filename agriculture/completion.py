import json
import pandas as pd
from django.http import HttpResponse

# 重新加载数据集
data_path = 'agriculture/ltest/data_raw_guanxi.xlsx'
data = pd.read_excel(data_path)

# 预处理数据：将文本转换为数值ID
entity_set = set(data.iloc[:, 0]).union(set(data.iloc[:, 2]))
relation_set = set(data.iloc[:, 1])

entity_to_id = {entity: id for id, entity in enumerate(entity_set)}
relation_to_id = {relation: id for id, relation in enumerate(relation_set)}

# 转换数据集
data['head_id'] = data.iloc[:, 0].map(entity_to_id)
data['relation_id'] = data.iloc[:, 1].map(relation_to_id)
data['tail_id'] = data.iloc[:, 2].map(entity_to_id)

# 分割数据集为训练集和验证集
valid_size = int(len(data) * 0.2)
train_data = data[:-valid_size]
valid_data = data[-valid_size:]

# 更新实体和关系的数量
num_entities = len(entity_to_id)
num_relations = len(relation_to_id)

# 显示预处理后的一些基本信息
train_data.head(), valid_data.head(), len(train_data), len(valid_data), num_entities, num_relations


import torch
import torch.nn as nn
import torch.optim as optim

class ConvE(nn.Module):
    def __init__(self, num_entities, num_relations, embedding_dim):
        super(ConvE, self).__init__()
        self.entity_embeddings = nn.Embedding(num_entities, embedding_dim)
        self.relation_embeddings = nn.Embedding(num_relations, embedding_dim)
        # 初始化
        nn.init.xavier_uniform_(self.entity_embeddings.weight.data)
        nn.init.xavier_uniform_(self.relation_embeddings.weight.data)

    def forward(self, head, relation, tail):
        # 获取嵌入
        head_emb = self.entity_embeddings(head)
        relation_emb = self.relation_embeddings(relation)
        tail_emb = self.entity_embeddings(tail)

        # 计算头实体+关系与尾实体之间的距离
        distance = head_emb + relation_emb - tail_emb
        return torch.norm(distance, p=1, dim=1)  # 使用L1范数


# 设定模型参数
num_entities = len(entity_to_id)
num_relations = len(relation_to_id)
embedding_dim = 100  # 嵌入维度可以根据需要进行调整


from torch.utils.data import Dataset, DataLoader
import random


# 定义数据集
class KnowledgeGraphDataset(Dataset):
    def __init__(self, data_frame, num_entities):
        self.heads = torch.LongTensor(data_frame['head_id'].values)
        self.relations = torch.LongTensor(data_frame['relation_id'].values)
        self.tails = torch.LongTensor(data_frame['tail_id'].values)
        self.num_entities = num_entities

    def __len__(self):
        return len(self.heads)

    def __getitem__(self, idx):
        head = self.heads[idx]
        relation = self.relations[idx]
        tail = self.tails[idx]

        # 随机生成负例
        if random.random() < 0.5:  # 替换头实体
            head_neg = torch.randint(0, self.num_entities, (1,)).item()
            while head_neg == head.item():
                head_neg = torch.randint(0, self.num_entities, (1,)).item()
            tail_neg = tail
        else:  # 替换尾实体
            tail_neg = torch.randint(0, self.num_entities, (1,)).item()
            while tail_neg == tail.item():
                tail_neg = torch.randint(0, self.num_entities, (1,)).item()
            head_neg = head

        return head, relation, tail, torch.LongTensor([head_neg]), torch.LongTensor([tail_neg])

# 创建训练集和验证集的Dataset和DataLoader
train_dataset = KnowledgeGraphDataset(train_data, num_entities)
train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)

valid_dataset = KnowledgeGraphDataset(valid_data, num_entities)
valid_loader = DataLoader(valid_dataset, batch_size=128, shuffle=False)


margin = 1.0  # 边际值

# 训练模型
num_epochs = 100  # 实际训练中可能需要更多的epoch

# 重置模型和优化器，以便于重新开始训练
model = ConvE(num_entities, num_relations, embedding_dim)
optimizer = optim.Adam(model.parameters(), lr=0.001)

losses = []  # 用于记录每个epoch的损失

for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    for head, relation, tail, head_neg, tail_neg in train_loader:
        optimizer.zero_grad()

        # 正例距离
        pos_distance = model(head, relation, tail)
        # 负例距离 - 修正后，确保对负例的处理逻辑正确
        neg_distance_head = model(head_neg.squeeze(1), relation, tail)
        neg_distance_tail = model(head, relation, tail_neg.squeeze(1))

        # 计算损失
        loss = torch.mean(torch.relu(margin + pos_distance - neg_distance_head)) + \
               torch.mean(torch.relu(margin + pos_distance - neg_distance_tail))
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)
    losses.append(avg_loss)
    #print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}')


def calculate_hit_at_1(model, data_loader, num_samples=100):
    model.eval()
    hits = 0
    total = 0

    with torch.no_grad():
        for head, relation, tail, _, _ in data_loader:
            batch_size = head.size(0)
            for i in range(batch_size):
                head_i = head[i].repeat(num_samples)
                relation_i = relation[i].repeat(num_samples)
                tail_i = torch.randint(0, num_entities, (num_samples,))
                # 确保真实的尾实体包含在样本中
                tail_i[0] = tail[i]

                distances = model(head_i, relation_i, tail_i)
                predicted_tail = torch.argmin(distances)

                # 如果预测的尾实体是真实的尾实体
                if predicted_tail == 0:
                    hits += 1
                total += 1

    hit_at_1 = hits / total
    return hit_at_1


# 计算验证集上的命中率@1
hit_at_1 = calculate_hit_at_1(model, valid_loader)
#print(f'Hit@1: {hit_at_1:.4f}')

def predict_tail(model, head_id, relation_id, num_entities):
    model.eval()
    with torch.no_grad():
        # 将头实体和关系扩展到所有可能的尾实体
        head = torch.LongTensor([head_id]).repeat(num_entities)
        relation = torch.LongTensor([relation_id]).repeat(num_entities)
        tail = torch.arange(0, num_entities)

        # 计算距离或得分
        distances = model(head, relation, tail)

        # 找到距离最小（或得分最高）的尾实体ID
        predicted_tail_id = torch.argmin(distances).item()

    return predicted_tail_id

def predict_tail_from_text(model, head_text, relation_text, entity_to_id, relation_to_id, id_to_entity):
    # 转换文本到ID
    head_id = entity_to_id.get(head_text)
    relation_id = relation_to_id.get(relation_text)

    if head_id is None or relation_id is None:
        return "输入的实体或关系不存在于知识库中。"

    # 预测尾实体ID
    predicted_tail_id = predict_tail(model, head_id, relation_id, len(entity_to_id))

    # 将尾实体ID转换回文本
    predicted_tail_text = id_to_entity[predicted_tail_id]

    return predicted_tail_text

# 将ID映射回实体的文本
id_to_entity = {id: entity for entity, id in entity_to_id.items()}

# 示例文本输入
# head_text = "枯叶夜蛾"
# relation_text = "使用药剂"

def completion(request):
    head_text = request.GET['entity1']
    relation_text = request.GET['relation']
    # 执行预测
    predicted_tail_text = predict_tail_from_text(model, head_text, relation_text, entity_to_id, relation_to_id, id_to_entity)
    print(f'Predicted Tail Entity: {predicted_tail_text}')
    return HttpResponse(json.dumps(predicted_tail_text, ensure_ascii = False))