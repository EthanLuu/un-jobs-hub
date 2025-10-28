# 生成网站图标

## 已创建的文件

1. **icon.svg** - 主图标（SVG 格式，512x512）
   - 蓝色背景 (#0066CC)
   - UN 标志性的桂冠图案
   - "UN" 文字
   - 公文包图标（代表职位）
   - 地球仪图案

2. **site.webmanifest** - PWA 配置文件

## 需要生成的图标文件

为了完整支持所有平台，你需要从 SVG 生成以下尺寸的 PNG 图标：

### 方法 1: 使用在线工具（最简单）

访问 [Favicon Generator](https://realfavicongenerator.net/)：

1. 上传 `public/icon.svg`
2. 点击 "Generate favicons"
3. 下载生成的文件包
4. 解压并复制以下文件到 `frontend/public/`:
   - `favicon.ico`
   - `favicon-16x16.png`
   - `favicon-32x32.png`
   - `apple-touch-icon.png` (180x180)
   - `android-chrome-192x192.png`
   - `android-chrome-512x512.png`

### 方法 2: 使用命令行工具

如果你安装了 ImageMagick 或 Inkscape：

```bash
cd frontend/public

# 使用 Inkscape (推荐用于 SVG)
inkscape icon.svg --export-filename=favicon-16x16.png --export-width=16 --export-height=16
inkscape icon.svg --export-filename=favicon-32x32.png --export-width=32 --export-height=32
inkscape icon.svg --export-filename=apple-touch-icon.png --export-width=180 --export-height=180
inkscape icon.svg --export-filename=android-chrome-192x192.png --export-width=192 --export-height=192
inkscape icon.svg --export-filename=android-chrome-512x512.png --export-width=512 --export-height=512

# 或使用 ImageMagick
convert -background none icon.svg -resize 16x16 favicon-16x16.png
convert -background none icon.svg -resize 32x32 favicon-32x32.png
convert -background none icon.svg -resize 180x180 apple-touch-icon.png
convert -background none icon.svg -resize 192x192 android-chrome-192x192.png
convert -background none icon.svg -resize 512x512 android-chrome-512x512.png

# 生成 favicon.ico (包含多个尺寸)
convert favicon-16x16.png favicon-32x32.png favicon.ico
```

### 方法 3: 使用 Node.js 脚本

如果你想自动化这个过程，可以使用以下脚本：

```bash
# 安装依赖
npm install --save-dev sharp

# 运行脚本（需要创建）
node scripts/generate-icons.js
```

## 图标设计说明

### 颜色方案
- **主色**: #0066CC (UN 蓝色)
- **辅助色**: #FFFFFF (白色)

### 设计元素
1. **桂冠图案** - UN 标志性元素
2. **地球仪** - 代表全球性和国际化
3. **公文包** - 代表职位和就业
4. **"UN" 文字** - 清晰的品牌标识

### 浏览器支持
- ✅ Chrome/Edge (icon.svg + PNG fallbacks)
- ✅ Firefox (icon.svg + PNG fallbacks)
- ✅ Safari (apple-touch-icon.png)
- ✅ iOS (apple-touch-icon.png)
- ✅ Android (android-chrome-*.png)

## 验证图标

图标生成后，你可以通过以下方式验证：

1. **本地测试**:
   ```bash
   npm run dev
   # 访问 http://localhost:3000
   # 检查浏览器标签页图标
   ```

2. **在线测试**:
   - 部署后访问你的网站
   - 检查各种设备和浏览器

3. **PWA 测试**:
   - Chrome DevTools > Application > Manifest
   - 检查所有图标是否正确显示

## 自定义图标

如果你想修改图标，编辑 `icon.svg` 文件：

1. 使用 [Figma](https://figma.com) 或 [Inkscape](https://inkscape.org)
2. 保持 512x512 的尺寸
3. 导出为 SVG
4. 重新生成各种尺寸的 PNG

## 故障排除

### 图标不显示

1. 清除浏览器缓存 (Ctrl+Shift+Del)
2. 检查文件路径是否正确
3. 验证 `site.webmanifest` 配置
4. 检查 Next.js metadata 配置

### 图标模糊

- 确保 PNG 文件使用了正确的尺寸
- SVG 应该清晰显示在所有尺寸

### PWA 安装问题

- 验证 `site.webmanifest` 格式
- 确保所有必需的图标文件都存在
- 检查 HTTPS (PWA 需要)

## 参考资料

- [Next.js Metadata](https://nextjs.org/docs/app/api-reference/functions/generate-metadata)
- [Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [Favicon Generator](https://realfavicongenerator.net/)
