"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
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
      { strength: 0, text: "太弱", color: "text-red-500" },
      { strength: 1, text: "弱", color: "text-orange-500" },
      { strength: 2, text: "一般", color: "text-yellow-500" },
      { strength: 3, text: "良好", color: "text-blue-500" },
      { strength: 4, text: "强", color: "text-green-500" },
      { strength: 5, text: "很强", color: "text-green-600" },
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
          errors.email = "请输入有效的邮箱地址";
        } else {
          delete errors.email;
        }
        break;
      case "username":
        if (value && value.length < 3) {
          errors.username = "用户名至少需要3个字符";
        } else if (value && !/^[a-zA-Z0-9_]+$/.test(value)) {
          errors.username = "用户名只能包含字母、数字和下划线";
        } else {
          delete errors.username;
        }
        break;
      case "password":
        if (value && value.length < 6) {
          errors.password = "密码至少需要6个字符";
        } else {
          delete errors.password;
        }
        // 检查确认密码是否匹配
        if (formData.confirmPassword && value !== formData.confirmPassword) {
          errors.confirmPassword = "两次输入的密码不一致";
        } else if (formData.confirmPassword) {
          delete errors.confirmPassword;
        }
        break;
      case "confirmPassword":
        if (value && value !== formData.password) {
          errors.confirmPassword = "两次输入的密码不一致";
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
      setError("请输入有效的邮箱地址");
      return;
    }

    if (formData.username.length < 3) {
      setError("用户名至少需要3个字符");
      return;
    }

    if (formData.password.length < 6) {
      setError("密码至少需要6个字符");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("两次输入的密码不一致");
      return;
    }

    setIsLoading(true);

    try {
      await register(formData.email, formData.username, formData.password);
      
      // 显示成功提示
      toast({
        title: "注册成功",
        description: "欢迎加入！正在跳转到个人中心...",
        variant: "success",
      });

      // 延迟跳转以显示提示
      setTimeout(() => {
        router.push("/profile");
        router.refresh();
      }, 500);
    } catch (err: any) {
      // 友好的错误提示
      let errorMessage = "注册失败，请重试";
      
      if (err.message) {
        const msg = err.message.toLowerCase();
        if (msg.includes("email") && msg.includes("already")) {
          errorMessage = "该邮箱已被注册，请使用其他邮箱";
        } else if (msg.includes("username") && msg.includes("already")) {
          errorMessage = "该用户名已被使用，请选择其他用户名";
        } else if (msg.includes("network") || msg.includes("fetch")) {
          errorMessage = "网络连接失败，请检查网络后重试";
        } else {
          errorMessage = err.message;
        }
      }
      
      setError(errorMessage);
      
      toast({
        title: "注册失败",
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
      title="创建账户"
      description="填写信息以开始使用联合国职位中心"
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
                创建中...
              </>
            ) : (
              "创建账户"
            )}
          </Button>
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                或
              </span>
            </div>
          </div>
          <p className="text-center text-sm text-muted-foreground">
            已有账户？{" "}
            <Link href="/login" className="font-medium text-primary hover:underline">
              立即登录
            </Link>
          </p>
        </>
      }
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-2">
          <Label htmlFor="email">
            邮箱地址 <span className="text-destructive">*</span>
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
          <Label htmlFor="username">
            用户名 <span className="text-destructive">*</span>
          </Label>
          <Input
            id="username"
            name="username"
            type="text"
            placeholder="用户名（字母、数字、下划线）"
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
              用户名可用
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">
            密码 <span className="text-destructive">*</span>
          </Label>
          <div className="relative">
            <Input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder="至少6个字符"
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
              <span className="text-muted-foreground">密码强度:</span>
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
          <Label htmlFor="confirmPassword">
            确认密码 <span className="text-destructive">*</span>
          </Label>
          <div className="relative">
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type={showConfirmPassword ? "text" : "password"}
              placeholder="再次输入密码"
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
              密码匹配
            </p>
          )}
        </div>

        <p className="text-xs text-muted-foreground">
          注册即表示您同意我们的{" "}
          <Link href="/terms" className="text-primary hover:underline">
            服务条款
          </Link>{" "}
          和{" "}
          <Link href="/privacy" className="text-primary hover:underline">
            隐私政策
          </Link>
        </p>
      </form>
    </AuthForm>
  );
}
