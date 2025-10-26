import { render, screen, fireEvent } from '@testing-library/react'
import { Hero } from '@/components/home/hero'

// Mock useRouter
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

describe('Hero Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders hero section with title and description', () => {
    render(<Hero />)
    
    expect(screen.getByText(/Find Your Dream Job in the/i)).toBeInTheDocument()
    expect(screen.getByText(/UN System/i)).toBeInTheDocument()
    expect(screen.getByText(/Search and apply to thousands of positions/i)).toBeInTheDocument()
  })

  it('renders search form', () => {
    render(<Hero />)
    
    expect(screen.getByPlaceholderText(/Search by job title, keyword, or location/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Search Jobs/i })).toBeInTheDocument()
  })

  it('handles search form submission with query', () => {
    render(<Hero />)
    
    const searchInput = screen.getByPlaceholderText(/Search by job title, keyword, or location/i)
    const searchButton = screen.getByRole('button', { name: /Search Jobs/i })
    
    fireEvent.change(searchInput, { target: { value: 'software engineer' } })
    fireEvent.click(searchButton)
    
    expect(mockPush).toHaveBeenCalledWith('/jobs?keywords=software%20engineer')
  })

  it('handles search form submission without query', () => {
    render(<Hero />)
    
    const searchButton = screen.getByRole('button', { name: /Search Jobs/i })
    
    fireEvent.click(searchButton)
    
    expect(mockPush).toHaveBeenCalledWith('/jobs')
  })

  it('handles form submission with Enter key', () => {
    render(<Hero />)
    
    const searchInput = screen.getByPlaceholderText(/Search by job title, keyword, or location/i)
    
    fireEvent.change(searchInput, { target: { value: 'project manager' } })
    fireEvent.keyDown(searchInput, { key: 'Enter', code: 'Enter' })
    
    expect(mockPush).toHaveBeenCalledWith('/jobs?keywords=project%20manager')
  })

  it('trims whitespace from search query', () => {
    render(<Hero />)
    
    const searchInput = screen.getByPlaceholderText(/Search by job title, keyword, or location/i)
    const searchButton = screen.getByRole('button', { name: /Search Jobs/i })
    
    fireEvent.change(searchInput, { target: { value: '  software engineer  ' } })
    fireEvent.click(searchButton)
    
    expect(mockPush).toHaveBeenCalledWith('/jobs?keywords=software%20engineer')
  })

  it('renders statistics section', () => {
    render(<Hero />)
    
    expect(screen.getByText(/5000\+/)).toBeInTheDocument()
    expect(screen.getByText(/Active Jobs/)).toBeInTheDocument()
    expect(screen.getByText(/30\+/)).toBeInTheDocument()
    expect(screen.getByText(/UN Organizations/)).toBeInTheDocument()
  })

  it('has proper accessibility attributes', () => {
    render(<Hero />)
    
    const searchInput = screen.getByPlaceholderText(/Search by job title, keyword, or location/i)
    const searchButton = screen.getByRole('button', { name: /Search Jobs/i })
    
    expect(searchInput).toHaveAttribute('type', 'text')
    expect(searchButton).toHaveAttribute('type', 'submit')
  })
})
