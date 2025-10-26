import { renderHook, act } from '@testing-library/react'
import { SWRConfig } from 'swr'
import { api } from '@/lib/api'

// Mock fetch
global.fetch = jest.fn()

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('makes GET request successfully', async () => {
    const mockData = { id: 1, title: 'Test Job' }
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    })

    const result = await api.get('/jobs/1')
    
    expect(fetch).toHaveBeenCalledWith('/api/jobs/1', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    expect(result).toEqual(mockData)
  })

  it('makes POST request successfully', async () => {
    const mockData = { id: 1, title: 'New Job' }
    const requestData = { title: 'New Job' }
    
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    })

    const result = await api.post('/jobs', requestData)
    
    expect(fetch).toHaveBeenCalledWith('/api/jobs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    })
    expect(result).toEqual(mockData)
  })

  it('makes PUT request successfully', async () => {
    const mockData = { id: 1, title: 'Updated Job' }
    const requestData = { title: 'Updated Job' }
    
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    })

    const result = await api.put('/jobs/1', requestData)
    
    expect(fetch).toHaveBeenCalledWith('/api/jobs/1', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    })
    expect(result).toEqual(mockData)
  })

  it('makes DELETE request successfully', async () => {
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 204,
    })

    await api.delete('/jobs/1')
    
    expect(fetch).toHaveBeenCalledWith('/api/jobs/1', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })
  })

  it('handles authentication headers', async () => {
    const token = 'test-token'
    const mockData = { id: 1, title: 'Test Job' }
    
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    })

    const result = await api.get('/jobs/1', { token })
    
    expect(fetch).toHaveBeenCalledWith('/api/jobs/1', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    })
    expect(result).toEqual(mockData)
  })

  it('handles errors properly', async () => {
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ error: 'Not found' }),
    })

    await expect(api.get('/jobs/999')).rejects.toThrow('Not found')
  })

  it('handles network errors', async () => {
    ;(fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

    await expect(api.get('/jobs/1')).rejects.toThrow('Network error')
  })

  it('handles JSON parsing errors', async () => {
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => {
        throw new Error('Invalid JSON')
      },
    })

    await expect(api.get('/jobs/1')).rejects.toThrow('Invalid JSON')
  })

  it('handles empty responses', async () => {
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 204,
    })

    const result = await api.delete('/jobs/1')
    expect(result).toBeUndefined()
  })

  it('handles custom headers', async () => {
    const mockData = { id: 1, title: 'Test Job' }
    const customHeaders = { 'X-Custom-Header': 'custom-value' }
    
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    })

    const result = await api.get('/jobs/1', { headers: customHeaders })
    
    expect(fetch).toHaveBeenCalledWith('/api/jobs/1', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Custom-Header': 'custom-value',
      },
    })
    expect(result).toEqual(mockData)
  })
})
