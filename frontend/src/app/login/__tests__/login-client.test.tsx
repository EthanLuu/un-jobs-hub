import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { useToast } from '@/components/ui/use-toast';
import { LoginClient } from '../login-client';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/contexts/auth-context', () => ({
  useAuth: jest.fn(),
}));

jest.mock('@/components/ui/use-toast', () => ({
  useToast: jest.fn(),
}));

jest.mock('next-intl', () => ({
  useTranslations: () => (key: string) => {
    const translations: Record<string, string> = {
      'auth.welcomeBack': '欢迎回来',
      'auth.loginDescription': '登录到您的账户',
      'auth.email': '邮箱',
      'auth.password': '密码',
      'auth.signIn': '登录',
      'auth.signingIn': '登录中...',
      'auth.forgotPassword': '忘记密码？',
      'auth.rememberMe': '记住我',
      'auth.noAccount': '没有账户？',
      'auth.signUpNow': '立即注册',
      'validation.validEmail': '请输入有效的邮箱地址',
      'validation.passwordTooShort': '密码至少需要6个字符',
      'success.loginSuccess': '登录成功',
      'success.loginWelcomeBack': '欢迎回来！',
      'errors.loginFailed': '登录失败',
      'errors.invalidCredentials': '邮箱或密码错误',
      'errors.accountInactive': '账户未激活',
      'errors.networkError': '网络错误，请稍后重试',
    };
    return translations[key] || key;
  },
}));

describe('LoginClient', () => {
  const mockPush = jest.fn();
  const mockRefresh = jest.fn();
  const mockLogin = jest.fn();
  const mockToast = jest.fn();

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
      refresh: mockRefresh,
    });
    
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
    });
    
    (useToast as jest.Mock).mockReturnValue({
      toast: mockToast,
    });

    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      },
      writable: true,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders login form correctly', () => {
    render(<LoginClient />);
    
    expect(screen.getByText('欢迎回来')).toBeInTheDocument();
    expect(screen.getByText('登录到您的账户')).toBeInTheDocument();
    expect(screen.getByLabelText(/邮箱/)).toBeInTheDocument();
    expect(screen.getByLabelText(/密码/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /登录/ })).toBeInTheDocument();
  });

  it('validates email format', async () => {
    render(<LoginClient />);
    
    const emailInput = screen.getByLabelText(/邮箱/);
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.blur(emailInput);
    
    await waitFor(() => {
      expect(screen.getByText('请输入有效的邮箱地址')).toBeInTheDocument();
    });
  });

  it('validates password length', async () => {
    render(<LoginClient />);
    
    const passwordInput = screen.getByLabelText(/密码/);
    fireEvent.change(passwordInput, { target: { value: '123' } });
    
    await waitFor(() => {
      expect(screen.getByText('密码至少需要6个字符')).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    mockLogin.mockResolvedValue({});
    
    render(<LoginClient />);
    
    const emailInput = screen.getByLabelText(/邮箱/);
    const passwordInput = screen.getByLabelText(/密码/);
    const submitButton = screen.getByRole('button', { name: /登录/ });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  it('handles login error', async () => {
    const error = new Error('Invalid credentials');
    mockLogin.mockRejectedValue(error);
    
    render(<LoginClient />);
    
    const emailInput = screen.getByLabelText(/邮箱/);
    const passwordInput = screen.getByLabelText(/密码/);
    const submitButton = screen.getByRole('button', { name: /登录/ });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('邮箱或密码错误')).toBeInTheDocument();
    });
  });

  it('toggles password visibility', () => {
    render(<LoginClient />);
    
    const passwordInput = screen.getByLabelText(/密码/);
    const toggleButton = screen.getByRole('button', { name: '' });
    
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('handles remember me functionality', async () => {
    mockLogin.mockResolvedValue({});
    
    render(<LoginClient />);
    
    const emailInput = screen.getByLabelText(/邮箱/);
    const passwordInput = screen.getByLabelText(/密码/);
    const rememberCheckbox = screen.getByRole('checkbox');
    const submitButton = screen.getByRole('button', { name: /登录/ });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(rememberCheckbox);
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(window.localStorage.setItem).toHaveBeenCalledWith('rememberedEmail', 'test@example.com');
    });
  });
});
