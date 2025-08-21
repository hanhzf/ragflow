# RAGFlow 搜索工具使用说明

## 功能概述

`search.py` 是一个用于调用 RAGFlow 检索 API 的工具，支持将搜索结果导出为 CSV 格式的表格文件。

## 主要功能

1. **API 检索**: 调用 RAGFlow 检索 API 获取匹配结果
2. **CSV 导出**: 自动生成两个 CSV 文件
   - 匹配结果表格：包含所有检索到的匹配项
   - 文件清单：包含匹配的文档列表及匹配次数

## 使用方法

### 基本用法

```bash
python search.py [查询问题] [页码] [每页大小]
```

### 参数说明

- `查询问题`: 要搜索的问题或关键词（默认：董事会审核?）
- `页码`: 结果页码（默认：1）
- `每页大小`: 每页返回的结果数量（默认：30）

### 使用示例

```bash
# 使用默认参数
python search.py

# 自定义查询问题
python search.py "公司治理"

# 自定义查询问题和页码
python search.py "风险管理" 1 50
```

## 输出文件

### 1. 匹配结果表格 (search_results_YYYYMMDD_HHMMSS.csv)

包含以下列：
- **序号**: 结果序号
- **匹配结果**: 高亮显示的匹配内容 (highlight)
- **原始内容**: 完整的原始内容 (content)
- **相似度**: 匹配相似度分数
- **文档名称**: 来源文档名称 (document_keyword)

### 2. 文件清单 (document_list_YYYYMMDD_HHMMSS.csv)

包含以下列：
- **序号**: 文档序号
- **文档名称**: 文档名称
- **匹配次数**: 该文档在搜索结果中出现的次数

## 配置说明

在脚本开头可以修改以下配置：

```python
# RAGFlow API 配置
API_KEY = "your-api-key"
API_BASE_URL = "http://127.0.0.1:9380"
DATASET_ID = "your-dataset-id"
```

## 注意事项

1. 确保 RAGFlow 服务正在运行
2. 检查 API_KEY 和 DATASET_ID 是否正确
3. CSV 文件使用 UTF-8 编码，支持中文内容
4. 文件名包含时间戳，避免覆盖之前的搜索结果
5. 结果按相似度降序排列，最相关的结果排在前面

## 错误处理

脚本包含完善的错误处理机制：
- API 请求错误
- JSON 解析错误
- CSV 导出错误

如遇到问题，请检查控制台输出的错误信息。
