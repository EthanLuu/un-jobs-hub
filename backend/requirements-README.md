# Requirements Files

## requirements.txt
精简版依赖，用于 Vercel Serverless 部署。
- 移除了重量级库（Playwright, Scrapy, sentence-transformers）
- 只包含 API 端点所需的核心功能
- 适合无服务器环境

## requirements-full.txt
完整版依赖，用于本地开发和 Railway/Render 部署。
- 包含所有功能的依赖
- 支持爬虫任务、ML 模型等
- 适合完整应用部署

## 使用场景

### Vercel 部署（API 端点）
使用 `requirements.txt`
```bash
pip install -r requirements.txt
```

### 本地开发或 Railway 部署（完整功能）
使用 `requirements-full.txt`  
```bash
pip install -r requirements-full.txt
```
