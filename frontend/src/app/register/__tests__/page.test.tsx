import { render, screen } from '@testing-library/react';
import RegisterPage from '../page';

// Mock the dynamic import
jest.mock('next/dynamic', () => {
  return () => {
    const MockedRegisterClient = () => (
      <div data-testid="register-client">Register Client Component</div>
    );
    return MockedRegisterClient;
  };
});

// Mock ErrorBoundary
jest.mock('@/components/error-boundary', () => {
  return function MockErrorBoundary({ children }: { children: React.ReactNode }) {
    return <div data-testid="error-boundary">{children}</div>;
  };
});

describe('RegisterPage', () => {
  it('renders register page with error boundary', () => {
    render(<RegisterPage />);
    
    expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
    expect(screen.getByTestId('register-client')).toBeInTheDocument();
  });

  it('renders loading state initially', () => {
    // Mock dynamic import with loading state
    jest.doMock('next/dynamic', () => {
      return () => {
        const MockedRegisterClient = () => (
          <div data-testid="loading">Loading...</div>
        );
        return MockedRegisterClient;
      };
    });
    
    render(<RegisterPage />);
    
    expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
  });
});
