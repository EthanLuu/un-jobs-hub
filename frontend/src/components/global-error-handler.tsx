"use client";

import { useEffect } from 'react';
import { useToast } from '@/components/ui/use-toast';

export function GlobalErrorHandler() {
  const { toast } = useToast();

  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      console.error('Global error:', event.error);
      
      toast({
        title: '发生错误',
        description: '应用程序遇到了意外错误，请刷新页面重试',
        variant: 'destructive',
      });
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason);
      
      toast({
        title: '请求失败',
        description: '网络请求失败，请检查网络连接后重试',
        variant: 'destructive',
      });
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [toast]);

  return null;
}
