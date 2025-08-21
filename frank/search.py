#!/usr/bin/env python3
import requests
import json
import sys

# RAGFlow API 配置
API_KEY = "ragflow-MwZTRjYWJlN2UyZTExZjBiZDg2MDI0Mm"
API_BASE_URL = "http://127.0.0.1:9380"
DATASET_ID = "2c01dc3e7db111f0a1e50242ac150006"

# 默认参数
QUESTION = sys.argv[1] if len(sys.argv) > 1 else "董事会审核?"
PAGE = int(sys.argv[2]) if len(sys.argv) > 2 else 1
PAGE_SIZE = int(sys.argv[3]) if len(sys.argv) > 3 else 30

print("正在调用RAGFlow检索API...")
print(f"数据集ID: {DATASET_ID}")
print(f"查询问题: {QUESTION}")
print(f"页码: {PAGE}")
print(f"每页大小: {PAGE_SIZE}")
print("")

# 构造请求数据
data = {
    "question": QUESTION,
    "dataset_ids": [DATASET_ID],
    "page": PAGE,
    "page_size": PAGE_SIZE,
    "similarity_threshold": 0.2,
    "vector_similarity_weight": 0.7,
    "top_k": 1024,
    "keyword": True,
    "highlight": True
}

# 设置请求头
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 执行API调用
try:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/retrieval",
        headers=headers,
        json=data
    )
    
    # 解析响应
    result = response.json()
    
    # 提取需要的字段并按指定格式打印
    if "data" in result and "chunks" in result["data"]:
        chunks = result["data"]["chunks"]
        # 按相似度降序排序
        chunks.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        print("检索结果:")
        print("=" * 60)
        for i, chunk in enumerate(chunks, 1):
            print(f"结果 {i}:")
            print(f"  匹配信息：")
            print(f"    highlight: {chunk.get('highlight', '')}")
            print(f"    content: {chunk.get('content', '')}")
            print(f"  文档信息：")
            print(f"    document_keyword: {chunk.get('document_keyword', '')}")
            print(f"  相似度信息：")
            print(f"    similarity: {chunk.get('similarity', '')}")
            print("-" * 50)
        
        # 提取去重后的document_keyword清单和匹配文档总数
        document_keywords = list(set([chunk.get('document_keyword', '') for chunk in chunks if chunk.get('document_keyword', '')]))
        document_count = len(document_keywords)
        
        print("\n去重后的文档清单:")
        print("=" * 60)
        for i, keyword in enumerate(document_keywords, 1):
            print(f"{i}. {keyword}")
        
        print(f"\n匹配文档总数: {document_count}")
    
except requests.exceptions.RequestException as e:
    print(f"请求错误: {e}")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"JSON解析错误: {e}")
    sys.exit(1)

print("")
print("调用完成！")