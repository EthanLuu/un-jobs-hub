# Next.js Performance Optimization Guide

## Implemented Optimizations

### 1. Component Lazy Loading

A utility library has been created at `src/lib/lazy-load.tsx` for easy component lazy loading:

```typescript
import { lazyLoad, LazyJobCard } from '@/lib/lazy-load';

// Use pre-configured lazy components
<LazyJobCard job={job} />

// Or create custom lazy loaded components
const LazyCustomComponent = lazyLoad(
  () => import('@/components/custom-component')
);
```

### 2. Image Optimization

Use Next.js Image component for automatic optimization:

```typescript
import Image from 'next/image';

<Image
  src="/path/to/image.jpg"
  alt="Description"
  width={800}
  height={600}
  priority={false}  // Set to true for above-the-fold images
  loading="lazy"
/>
```

### 3. Route Prefetching

Next.js automatically prefetches routes. You can control this:

```typescript
import Link from 'next/link';

// Disable prefetch for less important links
<Link href="/path" prefetch={false}>
  Link text
</Link>
```

### 4. Loading States

Use Suspense boundaries with loading components:

```typescript
import { Suspense } from 'react';
import { ListSkeleton } from '@/lib/lazy-load';

<Suspense fallback={<ListSkeleton />}>
  <JobList />
</Suspense>
```

## Recommended Next Steps

### 1. Implement ISR (Incremental Static Regeneration)

For job listing pages that don't change frequently:

```typescript
// app/jobs/[id]/page.tsx
export const revalidate = 3600; // Revalidate every hour

export async function generateStaticParams() {
  const jobs = await fetchJobs();
  return jobs.map((job) => ({
    id: job.id.toString(),
  }));
}
```

### 2. Add Client-Side Caching

Use SWR's built-in caching more effectively:

```typescript
// lib/api.ts
import useSWR from 'swr';

export function useJobs(params: JobParams) {
  return useSWR(
    ['/api/jobs', params],
    () => fetchJobs(params),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 60000, // 1 minute
      refreshInterval: 300000, // 5 minutes
    }
  );
}
```

### 3. Optimize Bundle Size

Add bundle analyzer to check package sizes:

```bash
npm install @next/bundle-analyzer
```

```javascript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer(nextConfig);
```

Run with:
```bash
ANALYZE=true npm run build
```

### 4. Implement Code Splitting

Split large components into smaller chunks:

```typescript
// Instead of one large dashboard component
const DashboardCharts = lazyLoad(() => import('./dashboard-charts'));
const DashboardStats = lazyLoad(() => import('./dashboard-stats'));
const DashboardActivity = lazyLoad(() => import('./dashboard-activity'));
```

### 5. Use Route Groups for Better Organization

```
app/
  (marketing)/
    layout.tsx
    page.tsx
    about/
      page.tsx
  (dashboard)/
    layout.tsx
    jobs/
      page.tsx
    profile/
      page.tsx
```

### 6. Optimize Fonts

Already using next/font, ensure optimal configuration:

```typescript
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  preload: true,
  variable: '--font-inter',
  adjustFontFallback: true, // Reduce layout shift
});
```

## Performance Checklist

- [ ] Lazy load heavy components
- [ ] Use Image component for all images
- [ ] Implement proper loading states
- [ ] Add Suspense boundaries
- [ ] Configure ISR for static content
- [ ] Optimize SWR caching
- [ ] Analyze and reduce bundle size
- [ ] Implement route prefetching strategy
- [ ] Use Server Components where possible
- [ ] Add Web Vitals monitoring

## Measuring Performance

### 1. Use Lighthouse

```bash
npm install -g lighthouse
lighthouse http://localhost:3000 --view
```

### 2. Add Web Vitals Tracking

Already implemented in `app/layout.tsx`:

```typescript
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

### 3. Monitor Core Web Vitals

- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1

## Additional Resources

- [Next.js Performance Docs](https://nextjs.org/docs/app/building-your-application/optimizing)
- [Web Vitals](https://web.dev/vitals/)
- [React Performance](https://react.dev/learn/render-and-commit)
