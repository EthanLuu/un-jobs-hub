"use client";

import dynamic from 'next/dynamic';
import ErrorBoundary from '@/components/error-boundary';

const RegisterClient = dynamic(() => import('./register-client').then(mod => ({ default: mod.RegisterClient })), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center min-h-screen">Loading...</div>
});

export default function RegisterPage() {
  return (
    <ErrorBoundary>
      <RegisterClient />
    </ErrorBoundary>
  );
}
