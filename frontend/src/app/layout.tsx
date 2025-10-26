import { ReactNode } from 'react';

// This is the root layout for the entire app
// The actual HTML structure is handled by [locale]/layout.tsx
export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return children;
}



