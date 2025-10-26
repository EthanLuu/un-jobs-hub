/**
 * Component lazy loading utilities for Next.js
 * Provides optimized lazy loading for heavy components
 */

import dynamic from 'next/dynamic';
import { ComponentType } from 'react';

/**
 * Loading skeleton component
 */
export const ComponentSkeleton = () => (
  <div className="animate-pulse space-y-4">
    <div className="h-8 bg-gray-200 rounded w-3/4"></div>
    <div className="h-4 bg-gray-200 rounded w-full"></div>
    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
  </div>
);

/**
 * Card skeleton component
 */
export const CardSkeleton = () => (
  <div className="animate-pulse">
    <div className="border rounded-lg p-6 space-y-4">
      <div className="h-6 bg-gray-200 rounded w-2/3"></div>
      <div className="h-4 bg-gray-200 rounded w-full"></div>
      <div className="h-4 bg-gray-200 rounded w-4/5"></div>
      <div className="flex space-x-2 mt-4">
        <div className="h-8 w-20 bg-gray-200 rounded"></div>
        <div className="h-8 w-24 bg-gray-200 rounded"></div>
      </div>
    </div>
  </div>
);

/**
 * List skeleton component
 */
export const ListSkeleton = ({ count = 5 }: { count?: number }) => (
  <div className="space-y-4">
    {Array.from({ length: count }).map((_, i) => (
      <CardSkeleton key={i} />
    ))}
  </div>
);

/**
 * Lazy load a component with loading state
 */
export function lazyLoad<P extends object>(
  importFunc: () => Promise<{ default: ComponentType<P> }>,
  loadingComponent: ComponentType = ComponentSkeleton
) {
  return dynamic(importFunc, {
    loading: loadingComponent,
    ssr: true, // Enable SSR by default
  });
}

/**
 * Lazy load component without SSR (client-side only)
 */
export function lazyLoadClient<P extends object>(
  importFunc: () => Promise<{ default: ComponentType<P> }>,
  loadingComponent: ComponentType = ComponentSkeleton
) {
  return dynamic(importFunc, {
    loading: loadingComponent,
    ssr: false, // Disable SSR for client-only components
  });
}

/**
 * Preload a component
 * Use this to prefetch components that will likely be needed soon
 */
export function preload<P extends object>(
  importFunc: () => Promise<{ default: ComponentType<P> }>
) {
  // Trigger the import to cache it
  importFunc();
}

// Pre-configured lazy loaded components
export const LazyJobCard = lazyLoad(
  () => import('@/components/jobs/job-card'),
  CardSkeleton
);

export const LazyJobSearchFilters = lazyLoad(
  () => import('@/components/jobs/job-search-filters'),
  () => <div className="h-96 animate-pulse bg-gray-100 rounded"></div>
);

export const LazyChart = lazyLoadClient(
  () => import('@/components/charts/chart-component'),
  () => <div className="h-64 animate-pulse bg-gray-100 rounded"></div>
);
