"use client";

import dynamic from 'next/dynamic';

const LoginClient = dynamic(() => import('./login-client').then(mod => ({ default: mod.LoginClient })), {
  ssr: false
});

export default function LoginPage() {
  return <LoginClient />;
}
