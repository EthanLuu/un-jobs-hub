import { render, screen } from '@testing-library/react'
import { Features } from '@/components/home/features'

describe('Features Component', () => {
  it('renders all feature cards', () => {
    render(<Features />)
    
    expect(screen.getByText('Smart Job Search')).toBeInTheDocument()
    expect(screen.getByText('AI-Powered Matching')).toBeInTheDocument()
    expect(screen.getByText('Resume Analysis')).toBeInTheDocument()
    expect(screen.getByText('Save Favorites')).toBeInTheDocument()
    expect(screen.getByText('Job Alerts')).toBeInTheDocument()
    expect(screen.getByText('Global Coverage')).toBeInTheDocument()
  })

  it('renders feature descriptions', () => {
    render(<Features />)
    
    expect(screen.getByText(/Advanced filters to find jobs/i)).toBeInTheDocument()
    expect(screen.getByText(/Upload your resume and get intelligent/i)).toBeInTheDocument()
    expect(screen.getByText(/Get instant feedback on your resume/i)).toBeInTheDocument()
    expect(screen.getByText(/Bookmark jobs you're interested in/i)).toBeInTheDocument()
    expect(screen.getByText(/Set up custom alerts/i)).toBeInTheDocument()
    expect(screen.getByText(/Access jobs from 30\+ UN organizations/i)).toBeInTheDocument()
  })

  it('renders feature icons', () => {
    render(<Features />)
    
    // Check that icons are rendered (they should be SVG elements)
    const icons = screen.getAllByRole('img', { hidden: true })
    expect(icons.length).toBeGreaterThan(0)
  })

  it('has proper grid layout', () => {
    const { container } = render(<Features />)
    
    // Check for grid classes
    const gridContainer = container.querySelector('.grid')
    expect(gridContainer).toBeInTheDocument()
  })

  it('renders feature cards with proper structure', () => {
    render(<Features />)
    
    // Each feature should have a title and description
    const featureTitles = screen.getAllByRole('heading', { level: 3 })
    expect(featureTitles).toHaveLength(6)
    
    // Check that each title has corresponding description
    featureTitles.forEach(title => {
      expect(title).toBeInTheDocument()
      const card = title.closest('[class*="card"]')
      expect(card).toBeInTheDocument()
    })
  })

  it('has accessible structure', () => {
    render(<Features />)
    
    // Check for proper heading hierarchy
    const headings = screen.getAllByRole('heading')
    expect(headings.length).toBe(6)
    
    // All headings should be h3
    headings.forEach(heading => {
      expect(heading.tagName).toBe('H3')
    })
  })
})
