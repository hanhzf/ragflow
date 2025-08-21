#!/usr/bin/env python3
import requests
import json
import sys
import csv
import os
import re

# RAGFlow API 配置
API_KEY = "ragflow-MwZTRjYWJlN2UyZTExZjBiZDg2MDI0Mm"
API_BASE_URL = "http://127.0.0.1:9380"
DATASET_ID = "2c01dc3e7db111f0a1e50242ac150006"

# 默认参数
DEFAULT_QUESTION = sys.argv[1] if len(sys.argv) > 1 else "董事会会审议、审批、决策事项"
QUESTION = os.environ.get("QUESTION", DEFAULT_QUESTION)
PAGE_SIZE = int(os.environ.get("PAGE_SIZE", 100))
SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD", 0.45))
VECTOR_SIMILARITY_WEIGHT = float(os.environ.get("VECTOR_SIMILARITY_WEIGHT", 0.7))

def clean_html_content(content):
    """清理HTML内容，去除HTML标签和语义"""
    if not content:
        return ""
    
    # 去除HTML标签
    content = re.sub(r'<[^>]+>', '', content)
    
    # 去除换行符
    content = content.replace('\n', ' ').replace('\r', ' ')
    
    # 去除多余的空格
    content = ' '.join(content.split())
    
    # 去除常见的HTML实体
    html_entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'"
    }
    
    for entity, replacement in html_entities.items():
        content = content.replace(entity, replacement)
    
    return content.strip()

print("正在调用RAGFlow检索API...")
print(f"数据集ID: {DATASET_ID}")
print(f"查询问题: {QUESTION}")
print(f"每页大小: {PAGE_SIZE}")
print("")

def fetch_all_pages(question, page_size):
    """获取所有页面的数据"""
    all_chunks = []
    page = 1
    total_pages = 0
    
    print("开始获取所有页面数据...")
    
    while True:
        print(f"正在获取第 {page} 页...")
        
        # 构造请求数据
        data = {
            "question": question,
            "dataset_ids": [DATASET_ID],
            "page": page,
            "page_size": page_size,
            "similarity_threshold": SIMILARITY_THRESHOLD,
            "vector_similarity_weight": VECTOR_SIMILARITY_WEIGHT,
            # "top_k": 1024,
            "top_k": 1024,
            "keyword": True,
            "highlight": True
        }

        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/retrieval",
                headers=headers,
                json=data
            )
            
            # 解析响应
            result = response.json()
            
            if "data" in result and "chunks" in result["data"]:
                chunks = result["data"]["chunks"]
                
                # 如果没有数据了，退出循环
                if not chunks:
                    print(f"第 {page} 页没有数据，获取完成")
                    break
                
                all_chunks.extend(chunks)
                print(f"第 {page} 页获取到 {len(chunks)} 条数据")
                
                # 检查是否还有更多页面
                if len(chunks) < page_size:
                    print(f"第 {page} 页数据少于 {page_size} 条，已获取完所有数据")
                    break
                
                page += 1
                
            else:
                print(f"❌ 第 {page} 页未找到检索结果数据")
                if "message" in result:
                    print(f"错误信息: {result['message']}")
                break
                
        except requests.exceptions.RequestException as e:
            print(f"第 {page} 页请求错误: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"第 {page} 页JSON解析错误: {e}")
            break
        except Exception as e:
            print(f"第 {page} 页发生未知错误: {e}")
            break
    
    print(f"\n总共获取了 {len(all_chunks)} 条数据，来自 {page} 页")
    return all_chunks

def export_to_csv(chunks, question):
    """导出结果到CSV文件"""
    
    # 1. 导出匹配结果表格
    results_filename = "search_results.csv"
    print(f"\n正在导出匹配结果到: {results_filename}")
    
    with open(results_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['序号', '匹配结果', '原始内容', '相似度', '文档名称']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for i, chunk in enumerate(chunks, 1):
            # 处理content内容，去除HTML标签和换行符
            content = clean_html_content(chunk.get('content', ''))
            
            writer.writerow({
                '序号': i,
                '匹配结果': chunk.get('highlight', ''),
                '原始内容': content,
                '相似度': f"{chunk.get('similarity', 0):.4f}",
                '文档名称': chunk.get('document_keyword', '')
            })
    
    # 2. 导出文件清单
    document_keywords = list(set([chunk.get('document_keyword', '') for chunk in chunks if chunk.get('document_keyword', '')]))
    document_keywords.sort()  # 按文档名称排序
    
    files_filename = "document_list.csv"
    print(f"正在导出文件清单到: {files_filename}")
    
    with open(files_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['序号', '文档名称', '匹配次数']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for i, keyword in enumerate(document_keywords, 1):
            # 统计每个文档的匹配次数
            match_count = sum(1 for chunk in chunks if chunk.get('document_keyword', '') == keyword)
            writer.writerow({
                '序号': i,
                '文档名称': keyword,
                '匹配次数': match_count
            })
    
    return results_filename, files_filename

# 执行API调用
try:
    # 获取所有页面的数据
    all_chunks = fetch_all_pages(QUESTION, PAGE_SIZE)
    
    if all_chunks:
        # 按相似度降序排序
        all_chunks.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        print("\n检索结果:")
        print("=" * 60)
        for i, chunk in enumerate(all_chunks, 1):
            # 处理content内容，去除HTML标签和换行符
            content = clean_html_content(chunk.get('content', ''))
            
            print(f"结果 {i}:")
            print(f"  匹配信息：")
            print(f"    highlight: {chunk.get('highlight', '')}")
            print(f"    content: {content}")
            print(f"  文档信息：")
            print(f"    document_keyword: {chunk.get('document_keyword', '')}")
            print(f"  相似度信息：")
            print(f"    similarity: {chunk.get('similarity', '')}")
            print("-" * 50)
        
        # 提取去重后的document_keyword清单和匹配文档总数
        document_keywords = list(set([chunk.get('document_keyword', '') for chunk in all_chunks if chunk.get('document_keyword', '')]))
        document_count = len(document_keywords)
        
        print("\n去重后的文档清单:")
        print("=" * 60)
        for i, keyword in enumerate(document_keywords, 1):
            print(f"{i}. {keyword}")
        
        print(f"\n匹配文档总数: {document_count}")
        
        # 导出到CSV文件
        results_file, files_file = export_to_csv(all_chunks, QUESTION)
        print(f"\n✅ CSV文件导出完成:")
        print(f"   - 匹配结果: {results_file}")
        print(f"   - 文件清单: {files_file}")
    
    else:
        print("❌ 未获取到任何检索结果数据")
    
except Exception as e:
    print(f"执行过程中发生错误: {e}")
    sys.exit(1)

print("")
print("调用完成！")