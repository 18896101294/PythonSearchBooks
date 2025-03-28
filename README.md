# Z-Library 搜索下载 API

这是一个用于搜索和下载 Z-Library 书籍的 RESTful API 服务。

## 功能特点

- 搜索书籍
- 获取下载链接
- 下载书籍
- Docker 容器化部署

## API 端点

### 1. 搜索书籍

```
GET /api/search?q={book_name}
```

参数：

- `q`: 要搜索的书籍名称

返回示例：

```json
{
  "status": "success",
  "count": 5,
  "books": [
    {
      "id": 1,
      "title": "Python编程",
      "author": "作者名",
      "publisher": "出版社",
      "language": "语言",
      "extension": "格式",
      "filesize": "大小",
      "rating": 4.5,
      "quality": "质量",
      "year": "年份",
      "detail_url": "详情页URL",
      "download_url": "下载链接"
    }
  ]
}
```

### 2. 获取下载链接

```
GET /api/get_download_url?url={detail_url}
```

参数：

- `url`: 书籍详情页 URL

返回示例：

```json
{
  "status": "success",
  "download_url": "下载链接"
}
```

### 3. 下载书籍

```
POST /api/download
```

请求体：

```json
{
  "download_url": "下载链接",
  "filename": "可选的文件名"
}
```

返回示例：

```json
{
  "status": "success",
  "message": "下载成功",
  "filepath": "文件保存路径"
}
```

## 部署说明

### 使用 Docker 部署

1. 构建 Docker 镜像：

```bash
docker build -t zlib-api .
```

2. 运行容器：

```bash
docker run -d -p 5001:5001 -v $(pwd)/downloads:/app/downloads zlib-api
```

### 直接运行

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 运行服务：

```bash
python api.py
```

## 注意事项

1. 下载的文件会保存在 `downloads` 目录中
2. 使用 Docker 部署时，请确保挂载 `downloads` 目录以持久化下载的文件
3. 建议在生产环境中添加适当的安全措施（如认证、HTTPS 等）

## 示例使用

使用 curl 测试 API：

```bash
# 搜索书籍
curl "http://localhost:5001/api/search?q=Python编程"

# 获取下载链接
curl "http://localhost:5001/api/get_download_url?url=/book/123456"

# 下载书籍
curl -X POST -H "Content-Type: application/json" \
     -d '{"download_url":"https://example.com/download/123","filename":"book.pdf"}' \
     http://localhost:5001/api/download
```
