import { render, screen, fireEvent } from '@testing-library/react'
import { AuthForm } from '@/components/auth/auth-form'

describe('AuthForm Component', () => {
  const defaultProps = {
    title: 'Test Form',
    description: 'This is a test form',
    icon: '🔐',
    children: <div>Form content</div>,
  }

  it('renders form with title and description', () => {
    render(<AuthForm {...defaultProps} />)
    
    expect(screen.getByText('Test Form')).toBeInTheDocument()
    expect(screen.getByText('This is a test form')).toBeInTheDocument()
  })

  it('renders icon when provided', () => {
    render(<AuthForm {...defaultProps} />)
    
    expect(screen.getByText('🔐')).toBeInTheDocument()
  })

  it('renders children content', () => {
    render(<AuthForm {...defaultProps} />)
    
    expect(screen.getByText('Form content')).toBeInTheDocument()
  })

  it('renders error message when provided', () => {
    render(<AuthForm {...defaultProps} error="Test error message" />)
    
    expect(screen.getByText('Test error message')).toBeInTheDocument()
  })

  it('renders footer when provided', () => {
    const footer = <div>Footer content</div>
    render(<AuthForm {...defaultProps} footer={footer} />)
    
    expect(screen.getByText('Footer content')).toBeInTheDocument()
  })

  it('applies proper styling classes', () => {
    const { container } = render(<AuthForm {...defaultProps} />)
    
    const form = container.querySelector('form')
    expect(form).toHaveClass('space-y-6')
    
    const card = container.querySelector('[class*="card"]')
    expect(card).toBeInTheDocument()
  })

  it('has proper accessibility structure', () => {
    render(<AuthForm {...defaultProps} />)
    
    // Check for proper heading structure
    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toHaveTextContent('Test Form')
    
    // Check for form element
    const form = screen.getByRole('form')
    expect(form).toBeInTheDocument()
  })

  it('renders without icon when not provided', () => {
    const propsWithoutIcon = {
      title: 'Test Form',
      description: 'This is a test form',
      children: <div>Form content</div>,
    }
    
    render(<AuthForm {...propsWithoutIcon} />)
    
    expect(screen.getByText('Test Form')).toBeInTheDocument()
    expect(screen.queryByText('🔐')).not.toBeInTheDocument()
  })

  it('handles empty error state', () => {
    render(<AuthForm {...defaultProps} error="" />)
    
    expect(screen.getByText('Test Form')).toBeInTheDocument()
    expect(screen.queryByText('Test error message')).not.toBeInTheDocument()
  })

  it('renders with proper layout structure', () => {
    const { container } = render(<AuthForm {...defaultProps} />)
    
    // Check for container structure
    const mainContainer = container.querySelector('.container')
    expect(mainContainer).toBeInTheDocument()
    
    // Check for card structure
    const card = container.querySelector('[class*="card"]')
    expect(card).toBeInTheDocument()
  })

  it('handles long content gracefully', () => {
    const longDescription = 'This is a very long description that should wrap properly and not break the layout of the form component.'
    
    render(
      <AuthForm 
        {...defaultProps} 
        description={longDescription}
      />
    )
    
    expect(screen.getByText(longDescription)).toBeInTheDocument()
  })
})
