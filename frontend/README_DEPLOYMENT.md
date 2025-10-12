# 前端快速部署到 Vercel

## 三种部署方式

### 🚀 方式一：Vercel CLI（最快 - 2 分钟）

```bash
# 1. 安装 Vercel CLI（如果还没安装）
npm install -g vercel

# 2. 在 frontend 目录下运行
cd frontend
vercel

# 3. 按照提示操作
# - 首次部署选择 "No" 链接到现有项目
# - 项目名称可以自定义
# - 其他选项都选默认值

# 4. 获取部署 URL
# Vercel 会输出预览 URL: https://your-app-xxx.vercel.app

# 5. 部署到生产环境
vercel --prod
```

### 🌐 方式二：Vercel Dashboard（最简单 - 5 分钟）

1. **访问** https://vercel.com/new

2. **导入 Git 仓库**
   - 点击 "Import Git Repository"
   - 连接 GitHub/GitLab/Bitbucket
   - 选择 `un-jobs-hub` 仓库

3. **配置项目**
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

4. **添加环境变量**（可选，后续可在 Dashboard 添加）
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

5. **点击 Deploy** 
   - 等待 2-3 分钟完成构建
   - 获取部署 URL

### 🔄 方式三：GitHub 自动部署（持续部署）

1. **推送代码到 GitHub**
   ```bash
   git add .
   git commit -m "Ready for Vercel deployment"
   git push origin main
   ```

2. **在 Vercel 导入仓库**
   - 访问 https://vercel.com/new
   - 选择 GitHub 仓库
   - 设置 Root Directory 为 `frontend`

3. **自动部署**
   - 每次 push 到 main 分支自动部署到生产环境
   - 每个 Pull Request 自动创建预览部署

## 环境变量配置

部署后需要配置后端 API 地址：

### 在 Vercel Dashboard 中设置

1. 进入项目 → Settings → Environment Variables
2. 添加变量：
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://your-backend-api.railway.app
   ```
3. 选择应用到的环境（Production, Preview, Development）
4. 保存后重新部署

### 或通过 CLI 设置

```bash
# 添加环境变量
vercel env add NEXT_PUBLIC_API_URL

# 输入值：https://your-backend-api.railway.app
# 选择环境：Production, Preview, Development（都选）

# 重新部署
vercel --prod
```

## 验证部署

1. **访问部署 URL**
   ```
   https://your-app.vercel.app
   ```

2. **检查 API 连接**
   - 打开浏览器开发者工具
   - 检查 Network 标签
   - 确认 API 请求发送到正确的后端地址

3. **测试功能**
   - 浏览职位列表
   - 测试登录/注册
   - 查看个人资料页面

## 自定义域名（可选）

1. 在 Vercel Dashboard → Domains
2. 添加你的域名（如 unjobs.com）
3. 按照指引配置 DNS 记录
4. 等待 DNS 生效（通常几分钟）

## 常见问题

### 构建失败
```bash
# 本地测试构建
npm run build

# 查看错误信息
# 修复后重新部署
```

### 环境变量未生效
- 确保变量名以 `NEXT_PUBLIC_` 开头
- 在 Dashboard 中检查变量是否正确设置
- 修改后需要重新部署

### API 连接失败
- 检查 CORS 配置（后端需要允许前端域名）
- 确认后端 API 地址正确
- 检查后端服务是否正常运行

## 部署状态监控

- **实时日志**: https://vercel.com/your-username/your-project/logs
- **部署历史**: 查看所有部署记录
- **性能指标**: 查看页面加载速度和 Core Web Vitals

## 下一步

✅ 前端已部署
⬜ 后端部署（推荐 Railway 或 Render）
⬜ 配置数据库
⬜ 更新环境变量
⬜ 设置自定义域名
