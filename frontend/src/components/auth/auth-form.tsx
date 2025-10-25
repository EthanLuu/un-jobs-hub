"use client";

import { ReactNode } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

interface AuthFormProps {
  title: string;
  description: string;
  icon: ReactNode;
  children: ReactNode;
  error?: string;
  footer?: ReactNode;
}

export function AuthForm({ title, description, icon, children, error, footer }: AuthFormProps) {
  return (
    <div className="container flex min-h-[calc(100vh-4rem)] items-center justify-center py-8 px-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-1 pb-4">
          <div className="flex items-center justify-center mb-2">
            <div className="rounded-full bg-primary/10 p-3">
              {icon}
            </div>
          </div>
          <CardTitle className="text-center text-2xl font-bold tracking-tight">{title}</CardTitle>
          <CardDescription className="text-center text-sm">
            {description}
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6 pb-6">
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-sm">{error}</AlertDescription>
            </Alert>
          )}
          {children}
        </CardContent>
        {footer && (
          <CardFooter className="flex flex-col space-y-4 pt-6 pb-6">
            {footer}
          </CardFooter>
        )}
      </Card>
    </div>
  );
}
