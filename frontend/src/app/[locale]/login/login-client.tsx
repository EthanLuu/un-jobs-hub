"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Link } from '@/i18n/navigation';
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { useAuth } from "@/contexts/auth-context";
import { LogIn, Eye, EyeOff, Loader2 } from "lucide-react";
import { AuthForm } from "@/components/auth/auth-form";
import { useToast } from "@/components/ui/use-toast";

export function LoginClient() {
  const router = useRouter();
  const { login } = useAuth();
  const { toast } = useToast();
  const t = useTranslations();
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [emailError, setEmailError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // 从本地存储加载记住的邮箱
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedEmail = localStorage.getItem("rememberedEmail");
      if (savedEmail) {
        setEmail(savedEmail);
        setRememberMe(true);
      }
    }
  }, []);

  // 邮箱验证
  const validateEmail = (email: string) => {
    if (!email) {
      setEmailError("");
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setEmailError("请输入有效的邮箱地址");
      return false;
    }
    setEmailError("");
    return true;
  };

  // 处理邮箱输入
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    if (newEmail) {
      validateEmail(newEmail);
    } else {
      setEmailError("");
    }
  };

  // 获取密码强度文本
  const getPasswordStrengthText = () => {
    if (!password) return "";
    if (password.length < 6) return t("validation.passwordTooShort");
    return "";
  };

  // 处理表单提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // 验证邮箱
    if (!validateEmail(email)) {
      setError(t("validation.validEmail"));
      return;
    }

    // 验证密码
    if (!password || password.length < 6) {
      setError(t("validation.passwordTooShort"));
      return;
    }

    setIsLoading(true);

    try {
      await login(email, password);
      
      // 处理"记住我"
      if (typeof window !== 'undefined') {
        if (rememberMe) {
          localStorage.setItem("rememberedEmail", email);
        } else {
          localStorage.removeItem("rememberedEmail");
        }
      }

      // 显示成功提示
      toast({
        title: t("success.loginSuccess"),
        description: t("success.loginWelcomeBack"),
        variant: "success",
      });

      // 延迟跳转以显示提示
      setTimeout(() => {
        router.push("/profile");
        router.refresh();
      }, 500);
    } catch (err: any) {
      // 友好的错误提示
      let errorMessage = t("errors.loginFailed");
      
      // 尝试提取错误消息
      let rawMessage = "";
      if (typeof err === 'string') {
        rawMessage = err;
      } else if (err instanceof Error) {
        rawMessage = err.message;
      } else if (typeof err === 'object' && err !== null) {
        rawMessage = err.message || err.detail || JSON.stringify(err);
      }
      
      if (rawMessage) {
        const msg = rawMessage.toLowerCase();
        if (msg.includes("incorrect") || msg.includes("invalid")) {
          errorMessage = t("errors.invalidCredentials");
        } else if (msg.includes("inactive")) {
          errorMessage = t("errors.accountInactive");
        } else if (msg.includes("network") || msg.includes("fetch") || msg.includes("failed to fetch")) {
          errorMessage = t("errors.networkError");
        } else if (msg.length > 0 && !msg.includes("object") && msg.length < 200) {
          // 只显示简短、有意义的错误消息
          errorMessage = rawMessage;
        }
      }
      
      setError(errorMessage);
      
      // 也显示一个toast提示
      toast({
        title: t("errors.loginFailed"),
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Enter键提交
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !isLoading) {
      handleSubmit(e as any);
    }
  };

  return (
    <AuthForm
      title={t("auth.welcomeBack")}
      description={t("auth.loginDescription")}
      icon={<LogIn className="h-6 w-6 text-primary" />}
      error={error}
      footer={
        <>
          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading}
            onClick={handleSubmit}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {t("auth.signingIn")}
              </>
            ) : (
              t("auth.signIn")
            )}
          </Button>
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                or
              </span>
            </div>
          </div>
          <p className="text-center text-sm text-muted-foreground">
            {t("auth.noAccount")}{" "}
            <Link href="/register" className="font-medium text-primary hover:underline">
              {t("auth.signUpNow")}
            </Link>
          </p>
        </>
      }
    >
      <form onSubmit={handleSubmit} onKeyDown={handleKeyDown} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="email" className="text-sm font-medium">
            {t("auth.email")} <span className="text-destructive">*</span>
          </Label>
          <Input
            id="email"
            type="email"
            placeholder="example@email.com"
            value={email}
            onChange={handleEmailChange}
            required
            disabled={isLoading}
            className={emailError ? "border-destructive" : ""}
            autoComplete="email"
          />
          {emailError && (
            <p className="text-xs text-destructive mt-1">{emailError}</p>
          )}
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="password" className="text-sm font-medium">
              {t("auth.password")} <span className="text-destructive">*</span>
            </Label>
            <Link 
              href="/forgot-password" 
              className="text-xs text-primary hover:underline"
              tabIndex={-1}
            >
              {t("auth.forgotPassword")}
            </Link>
          </div>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
              autoComplete="current-password"
              className="pr-10"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              tabIndex={-1}
              disabled={isLoading}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
          {password && getPasswordStrengthText() && (
            <p className="text-xs text-destructive mt-1">{getPasswordStrengthText()}</p>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="remember"
            checked={rememberMe}
            onCheckedChange={(checked) => setRememberMe(checked as boolean)}
            disabled={isLoading}
          />
          <label
            htmlFor="remember"
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer select-none"
          >
            {t("auth.rememberMe")}
          </label>
        </div>
      </form>
    </AuthForm>
  );
}
