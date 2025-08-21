#!/bin/bash

# RAGFlow API 配置
API_KEY="ragflow-MwZTRjYWJlN2UyZTExZjBiZDg2MDI0Mm"
API_BASE_URL="http://127.0.0.1"
DATASET_ID="2c01dc3e7db111f0a1e50242ac150006"

# 默认参数
QUESTION="${1:-董事会审核?}"
PAGE="${2:-1}"
PAGE_SIZE="${3:-30}"

echo "正在调用RAGFlow检索API..."
echo "数据集ID: $DATASET_ID"
echo "查询问题: $QUESTION"
echo "页码: $PAGE"
echo "每页大小: $PAGE_SIZE"
echo ""

# 执行API调用
curl --request POST \
     --url "$API_BASE_URL/api/v1/retrieval" \
     --header 'Content-Type: application/json' \
     --header "Authorization: Bearer $API_KEY" \
     --data "{
          \"question\": \"$QUESTION\",
          \"dataset_ids\": [\"$DATASET_ID\"],
          \"page\": $PAGE,
          \"page_size\": $PAGE_SIZE,
          \"similarity_threshold\": 0.2,
          \"vector_similarity_weight\": 0.7,
          \"top_k\": 1024,
          \"keyword\": true,
          \"highlight\": true
     }" \
     --silent \
     --show-error \
     --write-out "\n\nHTTP状态码: %{http_code}\n响应时间: %{time_total}s\n"

echo ""
echo "调用完成！"
