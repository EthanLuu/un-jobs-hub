import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '@/components/ui/button'

describe('Button Component', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>)
    
    expect(screen.getByRole('button', { name: /Click me/i })).toBeInTheDocument()
  })

  it('handles click events', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    const button = screen.getByRole('button', { name: /Click me/i })
    fireEvent.click(button)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('renders with default variant', () => {
    render(<Button>Default Button</Button>)
    
    const button = screen.getByRole('button', { name: /Default Button/i })
    expect(button).toHaveClass('bg-primary')
  })

  it('renders with secondary variant', () => {
    render(<Button variant="secondary">Secondary Button</Button>)
    
    const button = screen.getByRole('button', { name: /Secondary Button/i })
    expect(button).toHaveClass('bg-secondary')
  })

  it('renders with destructive variant', () => {
    render(<Button variant="destructive">Destructive Button</Button>)
    
    const button = screen.getByRole('button', { name: /Destructive Button/i })
    expect(button).toHaveClass('bg-destructive')
  })

  it('renders with outline variant', () => {
    render(<Button variant="outline">Outline Button</Button>)
    
    const button = screen.getByRole('button', { name: /Outline Button/i })
    expect(button).toHaveClass('border')
  })

  it('renders with ghost variant', () => {
    render(<Button variant="ghost">Ghost Button</Button>)
    
    const button = screen.getByRole('button', { name: /Ghost Button/i })
    expect(button).toHaveClass('hover:bg-accent')
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<Button size="sm">Small Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('h-9')
    
    rerender(<Button size="lg">Large Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('h-11')
    
    rerender(<Button size="icon">Icon Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('h-10', 'w-10')
  })

  it('can be disabled', () => {
    render(<Button disabled>Disabled Button</Button>)
    
    const button = screen.getByRole('button', { name: /Disabled Button/i })
    expect(button).toBeDisabled()
    expect(button).toHaveClass('disabled:pointer-events-none')
  })

  it('forwards ref correctly', () => {
    const ref = jest.fn()
    render(<Button ref={ref}>Button with Ref</Button>)
    
    expect(ref).toHaveBeenCalled()
  })

  it('renders as child component when asChild is true', () => {
    render(
      <Button asChild>
        <a href="/test">Link Button</a>
      </Button>
    )
    
    const link = screen.getByRole('link', { name: /Link Button/i })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '/test')
  })

  it('applies custom className', () => {
    render(<Button className="custom-class">Custom Button</Button>)
    
    const button = screen.getByRole('button', { name: /Custom Button/i })
    expect(button).toHaveClass('custom-class')
  })

  it('handles keyboard events', () => {
    const handleKeyDown = jest.fn()
    render(<Button onKeyDown={handleKeyDown}>Keyboard Button</Button>)
    
    const button = screen.getByRole('button', { name: /Keyboard Button/i })
    fireEvent.keyDown(button, { key: 'Enter' })
    
    expect(handleKeyDown).toHaveBeenCalledTimes(1)
  })

  it('has proper accessibility attributes', () => {
    render(<Button aria-label="Accessible Button">Button</Button>)
    
    const button = screen.getByRole('button', { name: /Accessible Button/i })
    expect(button).toHaveAttribute('aria-label', 'Accessible Button')
  })
})
