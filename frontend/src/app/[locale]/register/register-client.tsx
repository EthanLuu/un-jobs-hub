"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Link } from '@/i18n/navigation';
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/contexts/auth-context";
import { UserPlus, Eye, EyeOff, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { AuthForm } from "@/components/auth/auth-form";
import { useToast } from "@/components/ui/use-toast";

export function RegisterClient() {
  const router = useRouter();
  const { register } = useAuth();
  const { toast } = useToast();
  const t = useTranslations();
  
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  // 密码强度验证
  const getPasswordStrength = (password: string) => {
    if (!password) return { strength: 0, text: "", color: "" };
    
    let strength = 0;
    if (password.length >= 6) strength++;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;

    const strengthMap = [
      { strength: 0, text: t("passwordStrength.veryWeak"), color: "text-red-500" },
      { strength: 1, text: t("passwordStrength.weak"), color: "text-orange-500" },
      { strength: 2, text: t("passwordStrength.medium"), color: "text-yellow-500" },
      { strength: 3, text: t("passwordStrength.good"), color: "text-blue-500" },
      { strength: 4, text: t("passwordStrength.strong"), color: "text-green-500" },
      { strength: 5, text: t("passwordStrength.veryStrong"), color: "text-green-600" },
    ];

    return strengthMap[strength];
  };

  // 实时验证
  const validateField = (name: string, value: string) => {
    const errors: Record<string, string> = { ...fieldErrors };

    switch (name) {
      case "email":
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (value && !emailRegex.test(value)) {
          errors.email = t("validation.validEmail");
        } else {
          delete errors.email;
        }
        break;
      case "username":
        if (value && value.length < 3) {
          errors.username = t("validation.usernameTooShort");
        } else if (value && !/^[a-zA-Z0-9_]+$/.test(value)) {
          errors.username = t("validation.invalidUsername");
        } else {
          delete errors.username;
        }
        break;
      case "password":
        if (value && value.length < 6) {
          errors.password = t("validation.passwordTooShort");
        } else {
          delete errors.password;
        }
        // 检查确认密码是否匹配
        if (formData.confirmPassword && value !== formData.confirmPassword) {
          errors.confirmPassword = t("validation.passwordsDontMatch");
        } else if (formData.confirmPassword) {
          delete errors.confirmPassword;
        }
        break;
      case "confirmPassword":
        if (value && value !== formData.password) {
          errors.confirmPassword = t("validation.passwordsDontMatch");
        } else {
          delete errors.confirmPassword;
        }
        break;
    }

    setFieldErrors(errors);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    validateField(name, value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // 最终验证
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError(t("validation.validEmail"));
      return;
    }

    if (formData.username.length < 3) {
      setError(t("validation.usernameTooShort"));
      return;
    }

    if (formData.password.length < 6) {
      setError(t("validation.passwordTooShort"));
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError(t("validation.passwordsDontMatch"));
      return;
    }

    setIsLoading(true);

    try {
      await register(formData.email, formData.username, formData.password);
      
      // 显示成功提示
      toast({
        title: t("success.signupSuccess"),
        description: t("success.signupWelcome"),
        variant: "success",
      });

      // 延迟跳转以显示提示
      setTimeout(() => {
        router.push("/profile");
        router.refresh();
      }, 500);
    } catch (err: any) {
      // 友好的错误提示
      let errorMessage = t("errors.signupFailed");
      
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
        if (msg.includes("email") && (msg.includes("already") || msg.includes("registered"))) {
          errorMessage = t("errors.emailExists");
        } else if (msg.includes("username") && (msg.includes("already") || msg.includes("taken"))) {
          errorMessage = t("errors.usernameExists");
        } else if (msg.includes("network") || msg.includes("fetch") || msg.includes("failed to fetch")) {
          errorMessage = t("errors.networkError");
        } else if (msg.length > 0 && !msg.includes("object") && msg.length < 200) {
          // 只显示简短、有意义的错误消息
          errorMessage = rawMessage;
        }
      }
      
      setError(errorMessage);
      
      toast({
        title: t("errors.signupFailed"),
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const passwordStrength = getPasswordStrength(formData.password);
  const hasErrors = Object.keys(fieldErrors).length > 0;

  return (
    <AuthForm
      title={t("auth.createAccount")}
      description={t("auth.registerDescription")}
      icon={<UserPlus className="h-6 w-6 text-primary" />}
      error={error}
      footer={
        <>
          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading || hasErrors}
            onClick={handleSubmit}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {t("auth.creatingAccount")}
              </>
            ) : (
              t("auth.createAccount")
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
            {t("auth.alreadyHaveAccount")}{" "}
            <Link href="/login" className="font-medium text-primary hover:underline">
              {t("auth.signInNow")}
            </Link>
          </p>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="email" className="text-sm font-medium">
            {t("auth.email")} <span className="text-destructive">*</span>
          </Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="example@email.com"
            value={formData.email}
            onChange={handleChange}
            required
            disabled={isLoading}
            className={fieldErrors.email ? "border-destructive" : ""}
            autoComplete="email"
          />
          {fieldErrors.email && (
            <p className="text-xs text-destructive flex items-center gap-1">
              <XCircle className="h-3 w-3" />
              {fieldErrors.email}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="username" className="text-sm font-medium">
            {t("auth.username")} <span className="text-destructive">*</span>
          </Label>
          <Input
            id="username"
            name="username"
            type="text"
            placeholder={t("auth.usernamePlaceholder")}
            value={formData.username}
            onChange={handleChange}
            required
            disabled={isLoading}
            className={fieldErrors.username ? "border-destructive" : ""}
            autoComplete="username"
          />
          {fieldErrors.username && (
            <p className="text-xs text-destructive flex items-center gap-1">
              <XCircle className="h-3 w-3" />
              {fieldErrors.username}
            </p>
          )}
          {!fieldErrors.username && formData.username.length >= 3 && (
            <p className="text-xs text-green-600 flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3" />
              {t("auth.usernameAvailable")}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password" className="text-sm font-medium">
            {t("auth.password")} <span className="text-destructive">*</span>
          </Label>
          <div className="relative">
            <Input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder={t("auth.passwordPlaceholder")}
              value={formData.password}
              onChange={handleChange}
              required
              disabled={isLoading}
              className={fieldErrors.password ? "border-destructive pr-10" : "pr-10"}
              autoComplete="new-password"
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
          {formData.password && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-muted-foreground">{t("auth.passwordStrength")}:</span>
              <span className={passwordStrength.color}>
                {passwordStrength.text}
              </span>
            </div>
          )}
          {fieldErrors.password && (
            <p className="text-xs text-destructive flex items-center gap-1">
              <XCircle className="h-3 w-3" />
              {fieldErrors.password}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className="text-sm font-medium">
            {t("auth.confirmPassword")} <span className="text-destructive">*</span>
          </Label>
          <div className="relative">
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type={showConfirmPassword ? "text" : "password"}
              placeholder={t("auth.confirmPasswordPlaceholder")}
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              disabled={isLoading}
              className={fieldErrors.confirmPassword ? "border-destructive pr-10" : "pr-10"}
              autoComplete="new-password"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              tabIndex={-1}
              disabled={isLoading}
            >
              {showConfirmPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
          {fieldErrors.confirmPassword && (
            <p className="text-xs text-destructive flex items-center gap-1">
              <XCircle className="h-3 w-3" />
              {fieldErrors.confirmPassword}
            </p>
          )}
          {!fieldErrors.confirmPassword && 
           formData.confirmPassword && 
           formData.password === formData.confirmPassword && (
            <p className="text-xs text-green-600 flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3" />
              {t("auth.passwordMatch")}
            </p>
          )}
        </div>

        <p className="text-xs text-muted-foreground">
          {t("auth.terms")}{" "}
          <Link href="/terms" className="text-primary hover:underline">
            {t("auth.termsOfService")}
          </Link>{" "}
          和{" "}
          <Link href="/privacy" className="text-primary hover:underline">
            {t("auth.privacyPolicy")}
          </Link>
        </p>
      </form>
    </AuthForm>
  );
}
