# 后端部署到 Vercel 指南

## ⚠️ 重要限制

Vercel 的 Serverless 函数有以下限制：
- **执行时间**: 最多 10 秒（Hobby plan）/ 60 秒（Pro plan）
- **内存**: 最多 1024 MB
- **不支持**: WebSocket、长时间运行的任务、Celery 等后台任务
- **数据库**: 需要使用外部数据库服务

### 推荐方案对比

| 平台 | 优点 | 缺点 | 适合场景 |
|------|------|------|----------|
| **Vercel** | 部署简单、自动 HTTPS | 有执行时间限制、不支持后台任务 | API 端点、无状态服务 |
| **Railway** | 支持长时间任务、支持 Celery、免费额度 | 配置稍复杂 | 完整后端应用（推荐） |
| **Render** | 免费 PostgreSQL、支持后台任务 | 冷启动较慢 | 完整后端应用 |

## 🚀 Vercel 快速部署（适合 API 部分）

### 方式一：Vercel CLI

```bash
cd backend
vercel
```

### 方式二：Vercel Dashboard

1. 访问 https://vercel.com/new
2. 导入 GitHub 仓库
3. 配置：
   - Root Directory: `backend`
   - Framework Preset: Other
4. 添加环境变量（见下方）
5. 点击 Deploy

## ⚙️ 环境变量配置

在 Vercel Dashboard → Settings → Environment Variables 添加：

```bash
# 数据库（使用外部服务）
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# 密钥（生成方式：openssl rand -hex 32）
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# CORS（前端域名）
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://*.vercel.app

# OpenAI（可选）
OPENAI_API_KEY=sk-...

# Redis（如果使用 Vercel KV）
REDIS_URL=redis://...
```

## 📦 数据库选项

### 1. Neon (推荐 - Serverless Postgres)
- 免费额度：500 MB 存储
- 网站：https://neon.tech
- 自动休眠，唤醒快
- 完美适配 Vercel

### 2. Supabase
- 免费额度：500 MB 数据库
- 网站：https://supabase.com
- 提供额外功能（认证、存储）

### 3. PlanetScale
- 免费额度：10 GB 存储
- 网站：https://planetscale.com
- MySQL 兼容

## 🔧 配置步骤

### 1. 创建数据库（以 Neon 为例）

```bash
# 访问 https://neon.tech
# 创建项目并获取连接字符串
# 格式：postgresql://user:pass@host/dbname?sslmode=require
```

### 2. 在 Vercel 添加环境变量

```bash
vercel env add DATABASE_URL
# 粘贴 Neon 的连接字符串

vercel env add SECRET_KEY
# 输入生成的密钥

vercel env add ALLOWED_ORIGINS
# 输入前端域名
```

### 3. 部署

```bash
vercel --prod
```

## ⚠️ Vercel 限制的功能

由于 Vercel Serverless 的限制，以下功能**不支持**：

### ❌ 不支持的功能

1. **Celery 后台任务**
   - 爬虫定时任务
   - 邮件发送任务
   - 长时间运行的任务

2. **文件上传**
   - 简历上传功能受限
   - 需要使用 Vercel Blob 或 S3

3. **WebSocket**
   - 实时通知功能

### ✅ 支持的功能

- ✓ RESTful API 端点
- ✓ 用户认证（JWT）
- ✓ 数据库查询
- ✓ 短时间的 OpenAI API 调用
- ✓ 简单的数据处理

## 🎯 完整部署方案（推荐）

为了支持所有功能，推荐使用混合部署：

### 方案 A：Vercel (API) + Railway (Worker)

**Vercel 部署**：
- API 端点
- 用户认证
- 数据查询

**Railway 部署**：
- Celery Worker
- 定时爬虫
- 文件处理

### 方案 B：全部使用 Railway

最简单的方案，一次性部署所有功能。

参考 `DEPLOYMENT.md` 中的 Railway 部署指南。

## 🐛 常见问题

### 1. 部署成功但 API 不工作

检查日志：
```bash
vercel logs
```

常见原因：
- 数据库连接失败（检查 DATABASE_URL）
- 环境变量未设置
- Python 依赖安装失败

### 2. 数据库连接超时

确保：
- 使用 `?sslmode=require` 参数
- 数据库允许外部连接
- 检查防火墙设置

### 3. CORS 错误

在 Vercel Dashboard 添加：
```
ALLOWED_ORIGINS=https://your-app.vercel.app,https://*.vercel.app
```

## 📊 性能优化

### 1. 使用连接池

```python
# config.py
DATABASE_URL = settings.database_url
if DATABASE_URL and "postgresql" in DATABASE_URL:
    DATABASE_URL += "?pool_size=1&max_overflow=0"
```

### 2. 缓存策略

```python
# 使用 Vercel KV 作为 Redis
from vercel_kv import kv

@app.get("/api/jobs")
async def get_jobs():
    cached = await kv.get("jobs")
    if cached:
        return cached
    # ... 查询数据库
```

## 🔗 相关链接

- Vercel 文档: https://vercel.com/docs
- Vercel Python 运行时: https://vercel.com/docs/runtimes#official-runtimes/python
- Neon 数据库: https://neon.tech
- Railway 部署: 见 `DEPLOYMENT.md`

## 📝 下一步

1. [ ] 部署后端到 Vercel
2. [ ] 配置外部数据库（Neon/Supabase）
3. [ ] 设置环境变量
4. [ ] 测试 API 端点
5. [ ] 更新前端 API_URL
6. [ ] （可选）部署 Celery Worker 到 Railway
