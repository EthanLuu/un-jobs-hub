"use client";

import dynamic from 'next/dynamic';
import ErrorBoundary from '@/components/error-boundary';

const LoginClient = dynamic(() => import('./login-client').then(mod => ({ default: mod.LoginClient })), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center min-h-screen">Loading...</div>
});

export default function LoginPage() {
  return (
    <ErrorBoundary>
      <LoginClient />
    </ErrorBoundary>
  );
}
