# UN Jobs Hub - Frontend Documentation

> Next.js 15 frontend with App Router, TypeScript, and Tailwind CSS

## 📋 Overview

The frontend is built with **Next.js 15** using the App Router, providing a modern, type-safe, and performant user interface for browsing UN jobs, managing applications, and AI-powered job matching.

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│       Next.js 15 (App Router)           │
│   React 19 + TypeScript 5               │
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────────┐ ┌─────────────┐
│ API Client   │ │ SWR Cache   │
│ (with retry) │ │ (State Mgmt)│
└──────┬───────┘ └─────────────┘
       │
       ▼
┌──────────────────────┐
│  FastAPI Backend     │
│  (REST API)          │
└──────────────────────┘
```

## 🔧 Tech Stack

- **Framework:** Next.js 15 (App Router)
- **React:** React 19 (with RSC support)
- **Language:** TypeScript 5
- **Styling:** Tailwind CSS 4.0
- **UI Components:** Shadcn/UI + Radix UI
- **State Management:** SWR (for server state)
- **Forms:** React Hook Form + Zod
- **Icons:** Lucide React
- **Animations:** Framer Motion (optional)
- **Internationalization:** next-intl
- **Deployment:** Vercel

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                      # App Router pages
│   │   ├── [locale]/            # Internationalized routes
│   │   │   ├── page.tsx         # Home page
│   │   │   ├── jobs/            # Job listing and details
│   │   │   │   ├── page.tsx     # Job list page
│   │   │   │   ├── [id]/        # Job detail page
│   │   │   │   └── jobs-client.tsx
│   │   │   ├── match/           # AI matching page
│   │   │   ├── favorites/       # User favorites
│   │   │   └── profile/         # User profile
│   │   ├── auth/                # Authentication (no locale)
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── api/                 # API routes (if needed)
│   │   ├── layout.tsx           # Root layout
│   │   └── globals.css          # Global styles
│   │
│   ├── components/              # React components
│   │   ├── ui/                  # Shadcn/UI base components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── select.tsx
│   │   │   └── ...
│   │   ├── home/                # Home page components
│   │   │   ├── hero-section.tsx
│   │   │   ├── features-section.tsx
│   │   │   └── stats-section.tsx
│   │   ├── jobs/                # Job-related components
│   │   │   ├── job-card.tsx
│   │   │   ├── job-search-filters.tsx
│   │   │   ├── active-filters.tsx
│   │   │   └── job-list.tsx
│   │   ├── layout/              # Layout components
│   │   │   ├── header.tsx
│   │   │   ├── footer.tsx
│   │   │   └── sidebar.tsx
│   │   ├── loading.tsx          # Loading components (v1.8.0)
│   │   └── toast-provider.tsx   # Toast notifications (v1.8.0)
│   │
│   ├── lib/                     # Utilities and helpers
│   │   ├── api.ts               # Enhanced API client (v1.8.0)
│   │   ├── api-errors.ts        # Typed error handling (v1.8.0)
│   │   ├── lazy-load.tsx        # Lazy loading utilities (v1.3.0)
│   │   ├── utils.ts             # General utilities (cn, etc.)
│   │   └── validators.ts        # Zod schemas
│   │
│   ├── hooks/                   # Custom React hooks
│   │   ├── use-jobs.ts
│   │   ├── use-auth.ts
│   │   └── use-toast.ts
│   │
│   ├── types/                   # TypeScript type definitions
│   │   ├── job.ts
│   │   ├── user.ts
│   │   └── api.ts
│   │
│   └── i18n/                    # Internationalization
│       ├── request.ts
│       └── messages/
│           ├── en.json
│           └── zh.json
│
├── public/                      # Static assets
│   ├── images/
│   └── fonts/
│
├── tailwind.config.ts           # Tailwind configuration
├── tsconfig.json                # TypeScript configuration
├── next.config.js               # Next.js configuration
├── package.json
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Set up environment variables:**
```bash
cp .env.example .env.local
```

Required variables:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Run development server:**
```bash
npm run dev
```

Visit: http://localhost:3000

### Build for Production

```bash
# Build
npm run build

# Start production server
npm start

# Or use Vercel
vercel deploy
```

## 🎨 Component Library

### Shadcn/UI Components

Base UI components from [shadcn/ui](https://ui.shadcn.com/):

```bash
# Add a component
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add select
```

**Available Components:**
- `Button` - Customizable button with variants
- `Card` - Content container
- `Input` - Form input with validation
- `Select` - Dropdown selection
- `Dialog` - Modal dialogs
- `Tabs` - Tabbed interface
- `Badge` - Status badges
- `Avatar` - User avatars
- And 40+ more...

### Custom Components

**Loading Components (v1.8.0):**
```typescript
import { Loading, LoadingOverlay, PageLoading } from '@/components/loading'

// Basic loading spinner
<Loading size="md" text="Loading jobs..." />

// Full-screen overlay
<LoadingOverlay />

// Page-level loading
<PageLoading />
```

**Toast Notifications (v1.8.0):**
```typescript
import { useToast } from '@/components/toast-provider'

function MyComponent() {
  const toast = useToast()

  const handleSuccess = () => {
    toast.success('Job saved successfully!')
  }

  const handleError = () => {
    toast.error('Failed to save job')
  }

  return <button onClick={handleSuccess}>Save</button>
}
```

**Job Components:**
```typescript
import { JobCard } from '@/components/jobs/job-card'
import { JobSearchFilters } from '@/components/jobs/job-search-filters'
import { ActiveFilters } from '@/components/jobs/active-filters'

// Job card with all details
<JobCard job={job} />

// Search filters
<JobSearchFilters
  onFilterChange={handleFilterChange}
  organizations={orgs}
  locations={locations}
/>

// Active filter badges
<ActiveFilters
  filters={activeFilters}
  onRemoveFilter={handleRemove}
/>
```

## 🌐 API Client

### Enhanced API Client (v1.8.0)

Features:
- Automatic retry with exponential backoff
- Request timeout (30 seconds default)
- Typed error handling
- Token management
- Request/response interceptors

**Usage:**
```typescript
import { apiClient } from '@/lib/api'

// GET request
const jobs = await apiClient.getJobs({
  search: 'data analyst',
  organization: 'WHO',
  skip: 0,
  limit: 20
})

// POST request
const user = await apiClient.register({
  email: 'user@example.com',
  password: 'password123',
  username: 'username'
})

// With error handling
try {
  await apiClient.login(credentials)
} catch (error) {
  if (error instanceof APIError) {
    if (error.code === APIErrorCode.AUTH_ERROR) {
      console.error('Invalid credentials')
    }
  }
}
```

### API Methods

**Authentication:**
```typescript
apiClient.register(data: RegisterData)
apiClient.login(credentials: LoginCredentials)
apiClient.getCurrentUser()
apiClient.updateProfile(data: ProfileUpdate)
```

**Jobs:**
```typescript
apiClient.getJobs(params: JobsParams)
apiClient.getJob(id: string)
apiClient.getFilterOptions()
```

**Favorites:**
```typescript
apiClient.getFavorites()
apiClient.addFavorite(jobId: string)
apiClient.updateFavorite(id: string, data: FavoriteUpdate)
apiClient.removeFavorite(id: string)
```

**Resume:**
```typescript
apiClient.uploadResume(file: File)
apiClient.getResumes()
apiClient.getResume(id: string)
apiClient.deleteResume(id: string)
```

**Matching:**
```typescript
apiClient.matchJobs(resumeId: string)
apiClient.matchJob(resumeId: string, jobId: string)
```

### Error Handling (v1.8.0)

**Typed Errors:**
```typescript
import { APIError, APIErrorCode } from '@/lib/api-errors'

try {
  await apiClient.someMethod()
} catch (error) {
  if (error instanceof APIError) {
    switch (error.code) {
      case APIErrorCode.NETWORK_ERROR:
        toast.error('Network error. Please check your connection.')
        break
      case APIErrorCode.TIMEOUT_ERROR:
        toast.error('Request timed out. Please try again.')
        break
      case APIErrorCode.AUTH_ERROR:
        // Redirect to login
        router.push('/auth/login')
        break
      case APIErrorCode.VALIDATION_ERROR:
        // Show validation errors
        console.log(error.details)
        break
      default:
        toast.error('An error occurred')
    }
  }
}
```

**Automatic Retry:**
- Network errors: Retry up to 2 times
- Timeout errors: Retry once
- 5xx errors: Retry with backoff
- 4xx errors: No retry

## 🎨 Styling

### Tailwind CSS

**Configuration:**
```typescript
// tailwind.config.ts
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: { /* custom colors */ },
        secondary: { /* custom colors */ },
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
  ],
}
```

**Usage:**
```typescript
// Using cn() utility for conditional classes
import { cn } from '@/lib/utils'

<div className={cn(
  'base-classes',
  isActive && 'active-classes',
  'hover:opacity-80'
)} />
```

**Common Patterns:**
```typescript
// Card with hover effect
<div className="rounded-lg border bg-card p-6 shadow-sm transition-shadow hover:shadow-md">

// Responsive grid
<div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">

// Flexbox centering
<div className="flex items-center justify-center">

// Gradient text
<h1 className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
```

### CSS Variables

```css
/* globals.css */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  /* ... more variables */
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... dark mode colors */
}
```

## 🌍 Internationalization

Using `next-intl` for i18n:

**Configuration:**
```typescript
// src/i18n/request.ts
import { getRequestConfig } from 'next-intl/server'

export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`./messages/${locale}.json`)).default
}))
```

**Usage in Components:**
```typescript
import { useTranslations } from 'next-intl'

function MyComponent() {
  const t = useTranslations('jobs')

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  )
}
```

**Message Files:**
```json
// src/i18n/messages/en.json
{
  "jobs": {
    "title": "UN Jobs",
    "description": "Find your dream UN job",
    "search": "Search jobs",
    "filters": {
      "organization": "Organization",
      "location": "Location"
    }
  }
}
```

**Routing:**
```
/en/jobs       # English
/zh/jobs       # Chinese
/auth/login    # No locale (authentication)
```

## 📡 Data Fetching

### SWR for Server State

**Basic Usage:**
```typescript
import useSWR from 'swr'
import { apiClient } from '@/lib/api'

function JobsList() {
  const { data, error, isLoading } = useSWR(
    '/jobs',
    () => apiClient.getJobs({ skip: 0, limit: 20 })
  )

  if (isLoading) return <Loading />
  if (error) return <div>Error loading jobs</div>

  return <div>{/* Render jobs */}</div>
}
```

**With Pagination:**
```typescript
const [page, setPage] = useState(0)
const limit = 20

const { data, error, isLoading } = useSWR(
  ['/jobs', page],
  ([_, page]) => apiClient.getJobs({ skip: page * limit, limit })
)
```

**Mutations:**
```typescript
import { mutate } from 'swr'

const handleSaveJob = async (jobId: string) => {
  await apiClient.addFavorite(jobId)

  // Revalidate favorites
  mutate('/favorites')
}
```

### Server Components

```typescript
// app/[locale]/jobs/page.tsx
async function JobsPage() {
  // Fetch on server
  const jobs = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/jobs`)
    .then(res => res.json())

  return <JobsList initialData={jobs} />
}
```

## 🧩 Custom Hooks

### useAuth
```typescript
import { useAuth } from '@/hooks/use-auth'

function Profile() {
  const { user, isAuthenticated, login, logout } = useAuth()

  if (!isAuthenticated) {
    return <LoginPrompt />
  }

  return <div>Welcome, {user.name}</div>
}
```

### useJobs
```typescript
import { useJobs } from '@/hooks/use-jobs'

function JobsPage() {
  const {
    jobs,
    isLoading,
    error,
    filters,
    setFilters,
    page,
    setPage
  } = useJobs()

  return (
    <>
      <JobSearchFilters filters={filters} onChange={setFilters} />
      <JobList jobs={jobs} />
      <Pagination page={page} onChange={setPage} />
    </>
  )
}
```

## 🔒 Authentication

### Auth Flow

1. **Register:**
```typescript
const handleRegister = async (data: RegisterData) => {
  try {
    await apiClient.register(data)
    toast.success('Account created! Please log in.')
    router.push('/auth/login')
  } catch (error) {
    // Handle error
  }
}
```

2. **Login:**
```typescript
const handleLogin = async (credentials: LoginCredentials) => {
  try {
    const response = await apiClient.login(credentials)
    // Token automatically stored in localStorage
    router.push('/jobs')
  } catch (error) {
    toast.error('Invalid credentials')
  }
}
```

3. **Protected Routes:**
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')

  if (!token && request.nextUrl.pathname.startsWith('/profile')) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }
}
```

## 🎯 Performance Optimization

### Code Splitting

**Lazy Loading Components:**
```typescript
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Loading />,
  ssr: false  // Client-side only if needed
})
```

**Route-based Splitting:**
Automatic with Next.js App Router - each page is a separate bundle.

### Image Optimization

```typescript
import Image from 'next/image'

<Image
  src="/hero-image.jpg"
  alt="UN Jobs"
  width={1200}
  height={600}
  priority  // For above-the-fold images
  placeholder="blur"
  blurDataURL="data:image/..."
/>
```

### Font Optimization

```typescript
// app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
})

export default function RootLayout({ children }) {
  return (
    <html className={inter.className}>
      <body>{children}</body>
    </html>
  )
}
```

## 🧪 Testing

```bash
# Run tests
npm run test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage

# E2E tests (Playwright)
npm run test:e2e
```

**Example Test:**
```typescript
import { render, screen } from '@testing-library/react'
import JobCard from '@/components/jobs/job-card'

describe('JobCard', () => {
  it('renders job title', () => {
    const job = {
      id: '1',
      title: 'Data Analyst',
      organization: 'WHO',
      location: 'Geneva'
    }

    render(<JobCard job={job} />)
    expect(screen.getByText('Data Analyst')).toBeInTheDocument()
  })
})
```

## 📊 Analytics

### Vercel Analytics

```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

## 🚀 Deployment

### Vercel (Recommended)

1. **Connect GitHub repository**
2. **Configure environment variables:**
   - `NEXT_PUBLIC_API_URL`
   - Any other public variables
3. **Deploy automatically on push to `main`**

**Or deploy manually:**
```bash
npm install -g vercel
vercel --prod
```

### Self-Hosting

```bash
# Build
npm run build

# Start production server
npm start

# Or use PM2
pm2 start npm --name "unjobs-frontend" -- start
```

### Docker

```dockerfile
# Dockerfile (if needed)
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

## 📝 Code Standards

### TypeScript

**Always use proper types:**
```typescript
// Good
interface Job {
  id: string
  title: string
  organization: string
}

function JobCard({ job }: { job: Job }) {
  return <div>{job.title}</div>
}

// Bad
function JobCard({ job }: { job: any }) {
  return <div>{job.title}</div>
}
```

**Use type inference where possible:**
```typescript
// Good
const jobs = useJobs()  // Type inferred from hook

// Unnecessary
const jobs: Job[] = useJobs()
```

### Component Structure

```typescript
'use client'  // If client component

import { useState } from 'react'
import { Button } from '@/components/ui/button'

interface Props {
  // Props interface
}

export default function MyComponent({ prop1, prop2 }: Props) {
  // Hooks first
  const [state, setState] = useState()

  // Event handlers
  const handleClick = () => {
    // ...
  }

  // Render
  return (
    <div>
      {/* JSX */}
    </div>
  )
}
```

### File Naming

- Components: `PascalCase.tsx` (e.g., `JobCard.tsx`)
- Utilities: `kebab-case.ts` (e.g., `api-client.ts`)
- Hooks: `use-hook-name.ts` (e.g., `use-jobs.ts`)
- Types: `PascalCase.ts` or `kebab-case.ts`

## 🤝 Contributing

1. Follow the existing code style
2. Use TypeScript strictly (no `any`)
3. Add proper error handling
4. Test components before committing
5. Update documentation for significant changes

## 📄 License

MIT License - See [LICENSE](../LICENSE) file

---

**Version:** 1.10.0
**Last Updated:** 2024-12-19
**Maintainer:** UN Jobs Hub Team
