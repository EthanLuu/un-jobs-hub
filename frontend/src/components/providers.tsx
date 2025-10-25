"use client";

import { ReactNode } from "react";
import { SWRConfig } from "swr";
import { AuthProvider } from "@/contexts/auth-context";
import { Toaster } from "@/components/ui/toaster";

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <SWRConfig
      value={{
        fetcher: (url: string) => fetch(url).then((res) => res.json()),
        revalidateOnFocus: false,
      }}
    >
      <AuthProvider>
        {children}
        <Toaster />
      </AuthProvider>
    </SWRConfig>
  );
}



