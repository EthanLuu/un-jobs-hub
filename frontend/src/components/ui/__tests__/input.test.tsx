import { render, screen, fireEvent } from '@testing-library/react'
import { Input } from '@/components/ui/input'

describe('Input Component', () => {
  it('renders input with placeholder', () => {
    render(<Input placeholder="Enter text" />)
    
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument()
  })

  it('handles value changes', () => {
    const handleChange = jest.fn()
    render(<Input onChange={handleChange} />)
    
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'test value' } })
    
    expect(handleChange).toHaveBeenCalledTimes(1)
    expect(input).toHaveValue('test value')
  })

  it('renders with different types', () => {
    const { rerender } = render(<Input type="email" />)
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email')
    
    rerender(<Input type="password" />)
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'password')
    
    rerender(<Input type="number" />)
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'number')
  })

  it('can be disabled', () => {
    render(<Input disabled />)
    
    const input = screen.getByRole('textbox')
    expect(input).toBeDisabled()
  })

  it('can be required', () => {
    render(<Input required />)
    
    const input = screen.getByRole('textbox')
    expect(input).toBeRequired()
  })

  it('has proper accessibility attributes', () => {
    render(
      <Input 
        aria-label="Test Input"
        aria-describedby="help-text"
      />
    )
    
    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('aria-label', 'Test Input')
    expect(input).toHaveAttribute('aria-describedby', 'help-text')
  })

  it('forwards ref correctly', () => {
    const ref = jest.fn()
    render(<Input ref={ref} />)
    
    expect(ref).toHaveBeenCalled()
  })

  it('applies custom className', () => {
    render(<Input className="custom-class" />)
    
    const input = screen.getByRole('textbox')
    expect(input).toHaveClass('custom-class')
  })

  it('handles focus events', () => {
    const handleFocus = jest.fn()
    const handleBlur = jest.fn()
    
    render(<Input onFocus={handleFocus} onBlur={handleBlur} />)
    
    const input = screen.getByRole('textbox')
    
    fireEvent.focus(input)
    expect(handleFocus).toHaveBeenCalledTimes(1)
    
    fireEvent.blur(input)
    expect(handleBlur).toHaveBeenCalledTimes(1)
  })

  it('handles keyboard events', () => {
    const handleKeyDown = jest.fn()
    const handleKeyUp = jest.fn()
    
    render(<Input onKeyDown={handleKeyDown} onKeyUp={handleKeyUp} />)
    
    const input = screen.getByRole('textbox')
    
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(handleKeyDown).toHaveBeenCalledTimes(1)
    
    fireEvent.keyUp(input, { key: 'Enter' })
    expect(handleKeyUp).toHaveBeenCalledTimes(1)
  })

  it('renders with default value', () => {
    render(<Input defaultValue="default text" />)
    
    const input = screen.getByRole('textbox')
    expect(input).toHaveValue('default text')
  })

  it('renders with controlled value', () => {
    render(<Input value="controlled text" readOnly />)
    
    const input = screen.getByRole('textbox')
    expect(input).toHaveValue('controlled text')
  })

  it('has proper styling classes', () => {
    render(<Input />)
    
    const input = screen.getByRole('textbox')
    expect(input).toHaveClass('flex', 'h-10', 'w-full', 'rounded-md')
  })
})
