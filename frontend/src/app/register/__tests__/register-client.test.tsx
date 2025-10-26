import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { useToast } from '@/components/ui/use-toast';
import { RegisterClient } from '../register-client';

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
      'auth.createAccount': '创建账户',
      'auth.registerDescription': '注册新账户',
      'auth.email': '邮箱',
      'auth.username': '用户名',
      'auth.password': '密码',
      'auth.confirmPassword': '确认密码',
      'auth.signUp': '注册',
      'auth.registering': '注册中...',
      'auth.haveAccount': '已有账户？',
      'auth.signInNow': '立即登录',
      'validation.validEmail': '请输入有效的邮箱地址',
      'validation.passwordTooShort': '密码至少需要6个字符',
      'validation.passwordMismatch': '密码不匹配',
      'validation.usernameRequired': '用户名是必需的',
      'success.registerSuccess': '注册成功',
      'success.welcomeMessage': '欢迎加入我们！',
      'errors.registerFailed': '注册失败',
      'errors.emailExists': '邮箱已被使用',
      'errors.networkError': '网络错误，请稍后重试',
      'passwordStrength.veryWeak': '非常弱',
      'passwordStrength.weak': '弱',
      'passwordStrength.medium': '中等',
      'passwordStrength.good': '良好',
      'passwordStrength.strong': '强',
      'passwordStrength.veryStrong': '非常强',
    };
    return translations[key] || key;
  },
}));

describe('RegisterClient', () => {
  const mockPush = jest.fn();
  const mockRefresh = jest.fn();
  const mockRegister = jest.fn();
  const mockToast = jest.fn();

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
      refresh: mockRefresh,
    });
    
    (useAuth as jest.Mock).mockReturnValue({
      register: mockRegister,
    });
    
    (useToast as jest.Mock).mockReturnValue({
      toast: mockToast,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders register form correctly', () => {
    render(<RegisterClient />);
    
    expect(screen.getByText('创建账户')).toBeInTheDocument();
    expect(screen.getByText('注册新账户')).toBeInTheDocument();
    expect(screen.getByLabelText(/邮箱/)).toBeInTheDocument();
    expect(screen.getByLabelText(/用户名/)).toBeInTheDocument();
    expect(screen.getByLabelText(/密码/)).toBeInTheDocument();
    expect(screen.getByLabelText(/确认密码/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /注册/ })).toBeInTheDocument();
  });

  it('validates email format', async () => {
    render(<RegisterClient />);
    
    const emailInput = screen.getByLabelText(/邮箱/);
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.blur(emailInput);
    
    await waitFor(() => {
      expect(screen.getByText('请输入有效的邮箱地址')).toBeInTheDocument();
    });
  });

  it('validates password length', async () => {
    render(<RegisterClient />);
    
    const passwordInput = screen.getByLabelText(/密码/);
    fireEvent.change(passwordInput, { target: { value: '123' } });
    
    await waitFor(() => {
      expect(screen.getByText('密码至少需要6个字符')).toBeInTheDocument();
    });
  });

  it('validates password confirmation', async () => {
    render(<RegisterClient />);
    
    const passwordInput = screen.getByLabelText(/密码/);
    const confirmPasswordInput = screen.getByLabelText(/确认密码/);
    
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'different123' } });
    
    await waitFor(() => {
      expect(screen.getByText('密码不匹配')).toBeInTheDocument();
    });
  });

  it('validates username requirement', async () => {
    render(<RegisterClient />);
    
    const submitButton = screen.getByRole('button', { name: /注册/ });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('用户名是必需的')).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    mockRegister.mockResolvedValue({});
    
    render(<RegisterClient />);
    
    const emailInput = screen.getByLabelText(/邮箱/);
    const usernameInput = screen.getByLabelText(/用户名/);
    const passwordInput = screen.getByLabelText(/密码/);
    const confirmPasswordInput = screen.getByLabelText(/确认密码/);
    const submitButton = screen.getByRole('button', { name: /注册/ });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith('test@example.com', 'testuser', 'password123');
    });
  });

  it('handles registration error', async () => {
    const error = new Error('Email already exists');
    mockRegister.mockRejectedValue(error);
    
    render(<RegisterClient />);
    
    const emailInput = screen.getByLabelText(/邮箱/);
    const usernameInput = screen.getByLabelText(/用户名/);
    const passwordInput = screen.getByLabelText(/密码/);
    const confirmPasswordInput = screen.getByLabelText(/确认密码/);
    const submitButton = screen.getByRole('button', { name: /注册/ });
    
    fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('邮箱已被使用')).toBeInTheDocument();
    });
  });

  it('shows password strength indicator', async () => {
    render(<RegisterClient />);
    
    const passwordInput = screen.getByLabelText(/密码/);
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    await waitFor(() => {
      expect(screen.getByText('良好')).toBeInTheDocument();
    });
  });

  it('toggles password visibility', () => {
    render(<RegisterClient />);
    
    const passwordInput = screen.getByLabelText(/密码/);
    const toggleButtons = screen.getAllByRole('button', { name: '' });
    const passwordToggle = toggleButtons[0];
    
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    fireEvent.click(passwordToggle);
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    fireEvent.click(passwordToggle);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });
});
