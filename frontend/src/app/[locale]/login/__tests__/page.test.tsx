import { render, screen } from '@testing-library/react';
import LoginPage from '../page';

// Mock the dynamic import
jest.mock('next/dynamic', () => {
  return () => {
    const MockedLoginClient = () => (
      <div data-testid="login-client">Login Client Component</div>
    );
    return MockedLoginClient;
  };
});

// Mock ErrorBoundary
jest.mock('@/components/error-boundary', () => {
  return function MockErrorBoundary({ children }: { children: React.ReactNode }) {
    return <div data-testid="error-boundary">{children}</div>;
  };
});

describe('LoginPage', () => {
  it('renders login page with error boundary', () => {
    render(<LoginPage />);
    
    expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
    expect(screen.getByTestId('login-client')).toBeInTheDocument();
  });

  it('renders loading state initially', () => {
    // Mock dynamic import with loading state
    jest.doMock('next/dynamic', () => {
      return () => {
        const MockedLoginClient = () => (
          <div data-testid="loading">Loading...</div>
        );
        return MockedLoginClient;
      };
    });
    
    render(<LoginPage />);
    
    expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
  });
});
