import { render, screen } from '@testing-library/react'
import { Stats } from '@/components/home/stats'

describe('Stats Component', () => {
  it('renders all statistics', () => {
    render(<Stats />)
    
    expect(screen.getByText('5000+')).toBeInTheDocument()
    expect(screen.getByText('Active Jobs')).toBeInTheDocument()
    expect(screen.getByText('30+')).toBeInTheDocument()
    expect(screen.getByText('UN Organizations')).toBeInTheDocument()
    expect(screen.getByText('10000+')).toBeInTheDocument()
    expect(screen.getByText('Job Seekers')).toBeInTheDocument()
    expect(screen.getByText('95%')).toBeInTheDocument()
    expect(screen.getByText('Success Rate')).toBeInTheDocument()
  })

  it('renders statistics in proper grid layout', () => {
    const { container } = render(<Stats />)
    
    // Check for grid classes
    const gridContainer = container.querySelector('.grid')
    expect(gridContainer).toBeInTheDocument()
    
    // Should have 4 columns on medium screens and up
    expect(gridContainer).toHaveClass('md:grid-cols-4')
  })

  it('renders icons for each statistic', () => {
    render(<Stats />)
    
    // Check that icons are rendered (they should be SVG elements)
    const icons = screen.getAllByRole('img', { hidden: true })
    expect(icons.length).toBe(4)
  })

  it('has proper responsive design', () => {
    const { container } = render(<Stats />)
    
    const gridContainer = container.querySelector('.grid')
    
    // Should have responsive grid classes
    expect(gridContainer).toHaveClass('grid-cols-2') // 2 columns on mobile
    expect(gridContainer).toHaveClass('md:grid-cols-4') // 4 columns on medium screens
  })

  it('renders statistics with proper structure', () => {
    render(<Stats />)
    
    // Each stat should have an icon, value, and label
    const statContainers = screen.getAllByText(/5000\+|30\+|10000\+|95%/).map(el => el.closest('div'))
    
    statContainers.forEach(container => {
      expect(container).toBeInTheDocument()
      // Each container should have the text-center class
      expect(container).toHaveClass('text-center')
    })
  })

  it('has accessible structure', () => {
    render(<Stats />)
    
    // Check that all values are rendered
    const values = ['5000+', '30+', '10000+', '95%']
    values.forEach(value => {
      expect(screen.getByText(value)).toBeInTheDocument()
    })
    
    // Check that all labels are rendered
    const labels = ['Active Jobs', 'UN Organizations', 'Job Seekers', 'Success Rate']
    labels.forEach(label => {
      expect(screen.getByText(label)).toBeInTheDocument()
    })
  })

  it('renders with proper styling classes', () => {
    const { container } = render(<Stats />)
    
    const section = container.querySelector('section')
    expect(section).toHaveClass('border-y', 'bg-muted/50', 'py-12')
    
    const gridContainer = container.querySelector('.grid')
    expect(gridContainer).toHaveClass('grid', 'grid-cols-2', 'gap-8', 'md:grid-cols-4')
  })
})
