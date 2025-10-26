"use client";

import dynamic from 'next/dynamic';

const RegisterClient = dynamic(() => import('./register-client').then(mod => ({ default: mod.RegisterClient })), {
  ssr: false
});

export default function RegisterPage() {
  return <RegisterClient />;
}
