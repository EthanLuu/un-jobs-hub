import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { SWRConfig } from 'swr'
import { Hero } from '@/components/home/hero'
import { Features } from '@/components/home/features'
import { Stats } from '@/components/home/stats'

// Mock API responses
const mockJobsResponse = {
  jobs: [
    {
      id: 1,
      title: 'Software Engineer',
      organization: 'UN',
      location: 'Geneva',
      grade: 'P-3',
      contract_type: 'Fixed-term',
      category: 'Information Technology',
      description: 'Lead software development projects.',
      apply_url: 'https://example.com/apply',
      deadline: '2024-12-31',
      posted_date: '2024-01-01',
      is_active: true,
    },
    {
      id: 2,
      title: 'Program Manager',
      organization: 'UNDP',
      location: 'New York',
      grade: 'P-4',
      contract_type: 'Fixed-term',
      category: 'Programme Management',
      description: 'Manage development programs.',
      apply_url: 'https://example.com/apply2',
      deadline: '2024-11-30',
      posted_date: '2024-01-15',
      is_active: true,
    },
  ],
  total: 2,
  page: 1,
  page_size: 20,
  total_pages: 1,
}

// Mock fetch
global.fetch = jest.fn()

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <SWRConfig value={{ provider: () => new Map() }}>
    {children}
  </SWRConfig>
)

describe('Home Page Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockJobsResponse,
    })
  })

  it('renders complete home page layout', () => {
    render(
      <TestWrapper>
        <div>
          <Hero />
          <Features />
          <Stats />
        </div>
      </TestWrapper>
    )

    // Check Hero section
    expect(screen.getByText(/Find Your Dream Job in the/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Search by job title, keyword, or location/i)).toBeInTheDocument()

    // Check Features section
    expect(screen.getByText('Smart Job Search')).toBeInTheDocument()
    expect(screen.getByText('AI-Powered Matching')).toBeInTheDocument()

    // Check Stats section
    expect(screen.getByText('5000+')).toBeInTheDocument()
    expect(screen.getByText('Active Jobs')).toBeInTheDocument()
  })

  it('handles search flow from hero to jobs page', async () => {
    const mockPush = jest.fn()
    jest.doMock('next/navigation', () => ({
      useRouter: () => ({
        push: mockPush,
      }),
    }))

    render(
      <TestWrapper>
        <Hero />
      </TestWrapper>
    )

    const searchInput = screen.getByPlaceholderText(/Search by job title, keyword, or location/i)
    const searchButton = screen.getByRole('button', { name: /Search Jobs/i })

    fireEvent.change(searchInput, { target: { value: 'software engineer' } })
    fireEvent.click(searchButton)

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/jobs?keywords=software%20engineer')
    })
  })

  it('displays statistics correctly', () => {
    render(
      <TestWrapper>
        <Stats />
      </TestWrapper>
    )

    // Check all statistics are displayed
    const stats = [
      { value: '5000+', label: 'Active Jobs' },
      { value: '30+', label: 'UN Organizations' },
      { value: '10000+', label: 'Job Seekers' },
      { value: '95%', label: 'Success Rate' },
    ]

    stats.forEach(({ value, label }) => {
      expect(screen.getByText(value)).toBeInTheDocument()
      expect(screen.getByText(label)).toBeInTheDocument()
    })
  })

  it('renders features with proper descriptions', () => {
    render(
      <TestWrapper>
        <Features />
      </TestWrapper>
    )

    const features = [
      {
        title: 'Smart Job Search',
        description: 'Advanced filters to find jobs by organization, location, grade, and category across the entire UN system.',
      },
      {
        title: 'AI-Powered Matching',
        description: 'Upload your resume and get intelligent job recommendations based on your skills and experience.',
      },
      {
        title: 'Resume Analysis',
        description: 'Get instant feedback on your resume and see how well you match each position.',
      },
      {
        title: 'Save Favorites',
        description: "Bookmark jobs you're interested in and track your application status all in one place.",
      },
      {
        title: 'Job Alerts',
        description: 'Set up custom alerts and get notified when new jobs matching your criteria are posted.',
      },
      {
        title: 'Global Coverage',
        description: 'Access jobs from 30+ UN organizations including UNDP, UNICEF, WHO, FAO, and more.',
      },
    ]

    features.forEach(({ title, description }) => {
      expect(screen.getByText(title)).toBeInTheDocument()
      expect(screen.getByText(description)).toBeInTheDocument()
    })
  })

  it('has proper responsive design', () => {
    const { container } = render(
      <TestWrapper>
        <div>
          <Hero />
          <Features />
          <Stats />
        </div>
      </TestWrapper>
    )

    // Check for responsive classes
    const heroSection = container.querySelector('section')
    expect(heroSection).toHaveClass('py-20', 'md:py-32')

    const statsGrid = container.querySelector('.grid')
    expect(statsGrid).toHaveClass('grid-cols-2', 'md:grid-cols-4')
  })

  it('handles keyboard navigation', () => {
    render(
      <TestWrapper>
        <Hero />
      </TestWrapper>
    )

    const searchInput = screen.getByPlaceholderText(/Search by job title, keyword, or location/i)

    // Test Enter key
    fireEvent.change(searchInput, { target: { value: 'test query' } })
    fireEvent.keyDown(searchInput, { key: 'Enter', code: 'Enter' })

    // Test Tab navigation
    fireEvent.keyDown(searchInput, { key: 'Tab', code: 'Tab' })
    
    // Should not throw any errors
    expect(searchInput).toBeInTheDocument()
  })

  it('maintains accessibility standards', () => {
    render(
      <TestWrapper>
        <div>
          <Hero />
          <Features />
          <Stats />
        </div>
      </TestWrapper>
    )

    // Check for proper heading hierarchy
    const headings = screen.getAllByRole('heading')
    expect(headings.length).toBeGreaterThan(0)

    // Check for proper form structure
    const form = screen.getByRole('form')
    expect(form).toBeInTheDocument()

    // Check for proper button roles
    const buttons = screen.getAllByRole('button')
    expect(buttons.length).toBeGreaterThan(0)

    // Check for proper input roles
    const inputs = screen.getAllByRole('textbox')
    expect(inputs.length).toBeGreaterThan(0)
  })

  it('handles loading states gracefully', async () => {
    // Mock slow response
    ;(fetch as jest.Mock).mockImplementation(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: async () => mockJobsResponse,
        }), 100)
      )
    )

    render(
      <TestWrapper>
        <Hero />
      </TestWrapper>
    )

    // Component should render without errors during loading
    expect(screen.getByText(/Find Your Dream Job in the/i)).toBeInTheDocument()
    
    // Wait for any async operations to complete
    await waitFor(() => {
      expect(screen.getByText(/Find Your Dream Job in the/i)).toBeInTheDocument()
    })
  })

  it('handles error states gracefully', async () => {
    // Mock error response
    ;(fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

    render(
      <TestWrapper>
        <Hero />
      </TestWrapper>
    )

    // Component should still render despite API errors
    expect(screen.getByText(/Find Your Dream Job in the/i)).toBeInTheDocument()
  })
})
