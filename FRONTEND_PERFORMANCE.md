# 前端性能优化建议

## 🎯 优化目标

- 首屏加载时间 < 2秒
- TTI (Time to Interactive) < 3秒
- Lighthouse性能分数 > 90

## 📊 当前实施的优化

### 1. Next.js 15 优化
- ✅ App Router - 自动代码分割
- ✅ Image组件 - 自动图片优化
- ✅ Font优化 - 字体自动优化

### 2. 数据获取优化
- ✅ SWR - 客户端数据缓存
- ⚠️  建议：添加服务端缓存（Redis）
- ⚠️  建议：实施 ISR (Incremental Static Regeneration)

## 🚀 推荐优化措施

### 1. 代码分割和懒加载

#### 实施组件懒加载
```typescript
// ❌ 不推荐：直接导入大型组件
import HeavyComponent from './HeavyComponent'

// ✅ 推荐：使用动态导入
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Skeleton />
})
```

#### 路由级别代码分割
Next.js App Router已自动实施，但可以进一步优化：

```typescript
// app/jobs/[id]/page.tsx
export const dynamic = 'force-static' // 或 'force-dynamic'
export const revalidate = 3600 // ISR: 每小时重新生成
```

### 2. 图片优化

#### 使用Next.js Image组件
```tsx
import Image from 'next/image'

// ✅ 优化后的图片
<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority={false} // 非关键图片设为false
  loading="lazy"
/>
```

#### 图片格式建议
- 使用 WebP 格式
- 提供多种尺寸
- 实施图片CDN (Cloudinary/Vercel Image)

### 3. CSS和样式优化

#### Tailwind CSS配置优化
```js
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      // 只包含使用的颜色和大小
    },
  },
  // 启用JIT模式（已默认开启）
}
```

#### CSS-in-JS优化
- 考虑使用零运行时CSS-in-JS（如Vanilla Extract）
- 或使用Tailwind CSS减少运行时计算

### 4. JavaScript包大小优化

#### 分析包大小
```bash
# 安装分析工具
npm install @next/bundle-analyzer

# 运行分析
ANALYZE=true npm run build
```

#### 优化策略
```typescript
// 1. 使用更小的替代库
// ❌ moment.js (大型库)
import moment from 'moment'

// ✅ date-fns (tree-shakeable)
import { format } from 'date-fns'

// 2. 按需导入
// ❌ 导入整个库
import * as _ from 'lodash'

// ✅ 只导入需要的函数
import debounce from 'lodash/debounce'
```

### 5. 数据获取优化

#### 实施请求去重
```typescript
// lib/api.ts
import useSWR from 'swr'

export function useJobs(params: JobParams) {
  // SWR自动去重相同的请求
  const { data, error } = useSWR(
    ['/api/jobs', params],
    () => fetchJobs(params),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 60秒内去重
    }
  )

  return { data, error, isLoading: !data && !error }
}
```

#### 实施预取
```typescript
'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export function JobCard({ job }: { job: Job }) {
  const router = useRouter()

  // 预取职位详情页
  useEffect(() => {
    router.prefetch(`/jobs/${job.id}`)
  }, [job.id, router])

  return <div>{/* ... */}</div>
}
```

### 6. 服务端渲染优化

#### 使用React Server Components
```typescript
// app/jobs/page.tsx
// 这是一个Server Component（默认）

import { getJobs } from '@/lib/api-server'

export default async function JobsPage() {
  const jobs = await getJobs() // 在服务端获取数据

  return (
    <div>
      {jobs.map(job => <JobCard key={job.id} job={job} />)}
    </div>
  )
}
```

#### Streaming和Suspense
```typescript
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <Suspense fallback={<Skeleton />}>
        <JobsList />
      </Suspense>
    </div>
  )
}
```

### 7. 缓存策略

#### 服务端缓存
```typescript
// lib/cache.ts
import { unstable_cache } from 'next/cache'

export const getCachedJobs = unstable_cache(
  async (params) => {
    return await fetchJobs(params)
  },
  ['jobs'],
  { revalidate: 300 } // 5分钟缓存
)
```

#### 客户端缓存
```typescript
// 使用SWR的缓存配置
const { data } = useSWR(
  '/api/jobs',
  fetcher,
  {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    refreshInterval: 0,
    dedupingInterval: 60000,
  }
)
```

### 8. 字体优化

#### 使用next/font
```typescript
// app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap', // 防止FOIT
  preload: true,
  variable: '--font-inter',
})

export default function RootLayout({ children }) {
  return (
    <html className={inter.variable}>
      <body>{children}</body>
    </html>
  )
}
```

### 9. 第三方脚本优化

#### 使用Script组件
```typescript
import Script from 'next/script'

export default function Page() {
  return (
    <>
      <Script
        src="https://analytics.example.com/script.js"
        strategy="afterInteractive" // 或 'lazyOnload'
      />
    </>
  )
}
```

### 10. 监控和分析

#### 实施Web Vitals监控
```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react'
import { SpeedInsights } from '@vercel/speed-insights/next'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  )
}
```

## 📋 优化清单

### 立即实施（高优先级）
- [ ] 添加组件懒加载
- [ ] 实施ISR（增量静态再生成）
- [ ] 优化图片加载（lazy loading）
- [ ] 添加预取策略
- [ ] 实施服务端缓存

### 中期优化（中优先级）
- [ ] 分析和优化包大小
- [ ] 实施代码分割策略
- [ ] 优化第三方脚本加载
- [ ] 添加骨架屏
- [ ] 实施渐进式加载

### 长期优化（低优先级）
- [ ] 实施PWA（渐进式Web应用）
- [ ] 添加离线支持
- [ ] 实施服务工作线程
- [ ] 优化CSS交付
- [ ] 实施HTTP/2推送

## 🎯 性能预算

设置性能预算以防止回退：

```json
{
  "budgets": [
    {
      "path": "/*",
      "maxSize": "300kb",
      "type": "bundle"
    },
    {
      "path": "/jobs/*",
      "maxSize": "200kb",
      "type": "bundle"
    }
  ]
}
```

## 📊 测量工具

1. **Lighthouse** - 综合性能评分
2. **WebPageTest** - 详细性能分析
3. **Chrome DevTools** - 性能分析和调试
4. **Vercel Analytics** - 实际用户性能数据
5. **Bundle Analyzer** - 包大小分析

## 🔍 常见问题

### Q: 如何诊断性能问题？
A: 使用Chrome DevTools Performance面板，记录页面加载，查找长任务和阻塞渲染的资源。

### Q: SWR vs React Query？
A: SWR更轻量，React Query功能更丰富。对于我们的用例，SWR已经足够。

### Q: 是否应该使用SSG？
A: 对于经常变化的职位数据，ISR（增量静态再生成）是更好的选择。

---

**更新日期**: 2024-12-19
**版本**: 1.0
**维护者**: UN Jobs Hub Team
