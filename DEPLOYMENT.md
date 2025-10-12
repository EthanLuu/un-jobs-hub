# Vercel 快速部署指南

## 前端部署（Next.js）

### 方式一：通过 Vercel CLI（推荐，最快）

1. **安装 Vercel CLI**
```bash
npm install -g vercel
```

2. **登录 Vercel**
```bash
vercel login
```

3. **在 frontend 目录下部署**
```bash
cd frontend
vercel
```

首次部署时会询问：
- **Set up and deploy?** → Yes
- **Which scope?** → 选择你的账号
- **Link to existing project?** → No（首次部署）
- **What's your project's name?** → unjobs-frontend（或自定义）
- **In which directory is your code located?** → ./（当前目录）
- **Want to override the settings?** → No

4. **配置环境变量**

部署后，在 Vercel Dashboard 中设置环境变量：
- 进入项目 Settings → Environment Variables
- 添加：`NEXT_PUBLIC_API_URL` = `你的后端 API 地址`

5. **重新部署使环境变量生效**
```bash
vercel --prod
```

### 方式二：通过 Vercel Dashboard（最简单）

1. **访问** https://vercel.com/new
2. **导入 Git 仓库**
   - 连接你的 GitHub/GitLab/Bitbucket
   - 选择 `un-jobs-hub` 仓库
3. **配置项目**
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
4. **添加环境变量**
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: 你的后端 API 地址（先用临时值，后面更新）
5. **点击 Deploy**

### 方式三：通过 GitHub 集成（自动化）

1. **推送代码到 GitHub**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **在 Vercel 中导入**
   - 访问 https://vercel.com/new
   - 选择 GitHub 仓库
   - Vercel 会自动检测 Next.js 并配置

3. **配置根目录**
   - 设置 Root Directory 为 `frontend`

4. **自动部署**
   - 每次 push 到 main 分支会自动部署
   - Pull Request 会创建预览部署

---

## 后端部署（FastAPI）

Vercel 不直接支持 Python 后端，推荐使用以下平台：

### 推荐：Railway（免费额度，易用）

1. **访问** https://railway.app
2. **连接 GitHub 仓库**
3. **创建新项目** → Deploy from GitHub repo
4. **选择仓库** → un-jobs-hub
5. **添加服务**
   - 点击 "New Service" → "GitHub Repo"
   - Root Directory: `backend`
6. **配置环境变量**（在 Variables 标签）：
```
DATABASE_URL=postgresql://...（Railway 提供的 Postgres）
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://...（需要添加 Redis 插件）
OPENAI_API_KEY=sk-...（可选）
```

7. **添加数据库**
   - 点击 "New" → "Database" → "Add PostgreSQL"
   - Railway 会自动添加 DATABASE_URL 环境变量

8. **部署**
   - Railway 会自动检测 requirements.txt
   - 使用 Dockerfile 或自动构建

### 替代方案：Render

1. **访问** https://render.com
2. **New Web Service**
3. **连接 GitHub 仓库**
4. **配置**：
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **添加环境变量**（同 Railway）
6. **添加 PostgreSQL 数据库**（从 Dashboard）

---

## 环境变量配置总结

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### Backend (Railway/Render)
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
JWT_SECRET_KEY=your-jwt-secret-key
REDIS_URL=redis://host:6379/0
OPENAI_API_KEY=sk-...（可选）

# CORS
CORS_ORIGINS=https://your-frontend.vercel.app

# Email（可选）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 快速部署流程（5分钟）

1. **后端部署到 Railway**
   - 访问 railway.app，连接 GitHub，选择仓库
   - 设置 Root Directory: backend
   - 添加 PostgreSQL 插件
   - 添加必要的环境变量

2. **获取后端 URL**
   - 部署完成后，Railway 会提供一个 URL（如：`https://un-jobs-backend.railway.app`）

3. **前端部署到 Vercel**
   ```bash
   cd frontend
   vercel
   ```
   或访问 vercel.com/new，导入 GitHub 仓库

4. **配置前端环境变量**
   - 在 Vercel Dashboard 中设置 `NEXT_PUBLIC_API_URL` 为后端 URL

5. **重新部署前端**
   ```bash
   vercel --prod
   ```

6. **完成！**
   - 前端: `https://your-app.vercel.app`
   - 后端: `https://your-backend.railway.app`
