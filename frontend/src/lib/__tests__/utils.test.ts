import { cn, formatDate, formatCurrency, truncateText, generateSlug } from '@/lib/utils'

describe('Utility Functions', () => {
  describe('cn function', () => {
    it('combines class names correctly', () => {
      expect(cn('class1', 'class2')).toBe('class1 class2')
    })

    it('handles conditional classes', () => {
      expect(cn('base', true && 'conditional')).toBe('base conditional')
      expect(cn('base', false && 'conditional')).toBe('base')
    })

    it('handles undefined and null values', () => {
      expect(cn('base', undefined, null)).toBe('base')
    })

    it('handles empty strings', () => {
      expect(cn('base', '')).toBe('base')
    })

    it('handles arrays of classes', () => {
      expect(cn(['class1', 'class2'])).toBe('class1 class2')
    })

    it('handles objects with boolean values', () => {
      expect(cn({ 'class1': true, 'class2': false })).toBe('class1')
    })
  })

  describe('formatDate function', () => {
    it('formats date correctly', () => {
      const date = new Date('2024-12-31')
      expect(formatDate(date)).toBe('December 31, 2024')
    })

    it('handles different date formats', () => {
      const date = new Date('2024-01-01')
      expect(formatDate(date, 'short')).toBe('1/1/2024')
      expect(formatDate(date, 'long')).toBe('January 1, 2024')
    })

    it('handles invalid dates', () => {
      const invalidDate = new Date('invalid')
      expect(formatDate(invalidDate)).toBe('Invalid Date')
    })

    it('handles null and undefined', () => {
      expect(formatDate(null)).toBe('')
      expect(formatDate(undefined)).toBe('')
    })
  })

  describe('formatCurrency function', () => {
    it('formats currency correctly', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00')
      expect(formatCurrency(1000, 'EUR')).toBe('€1,000.00')
    })

    it('handles different locales', () => {
      expect(formatCurrency(1000, 'USD', 'en-US')).toBe('$1,000.00')
      expect(formatCurrency(1000, 'EUR', 'de-DE')).toBe('1.000,00 €')
    })

    it('handles zero and negative values', () => {
      expect(formatCurrency(0)).toBe('$0.00')
      expect(formatCurrency(-100)).toBe('-$100.00')
    })

    it('handles decimal values', () => {
      expect(formatCurrency(1234.56)).toBe('$1,234.56')
    })
  })

  describe('truncateText function', () => {
    it('truncates text correctly', () => {
      const longText = 'This is a very long text that should be truncated'
      expect(truncateText(longText, 20)).toBe('This is a very long...')
    })

    it('returns original text if shorter than limit', () => {
      const shortText = 'Short text'
      expect(truncateText(shortText, 20)).toBe('Short text')
    })

    it('handles empty string', () => {
      expect(truncateText('', 10)).toBe('')
    })

    it('handles null and undefined', () => {
      expect(truncateText(null, 10)).toBe('')
      expect(truncateText(undefined, 10)).toBe('')
    })

    it('uses custom suffix', () => {
      const longText = 'This is a very long text'
      expect(truncateText(longText, 10, '...')).toBe('This is...')
    })
  })

  describe('generateSlug function', () => {
    it('generates slug correctly', () => {
      expect(generateSlug('Software Engineer')).toBe('software-engineer')
      expect(generateSlug('Program Manager - P-4')).toBe('program-manager-p-4')
    })

    it('handles special characters', () => {
      expect(generateSlug('IT & Communications')).toBe('it-communications')
      expect(generateSlug('Special@#$Characters')).toBe('specialcharacters')
    })

    it('handles multiple spaces', () => {
      expect(generateSlug('Multiple   Spaces')).toBe('multiple-spaces')
    })

    it('handles empty string', () => {
      expect(generateSlug('')).toBe('')
    })

    it('handles null and undefined', () => {
      expect(generateSlug(null)).toBe('')
      expect(generateSlug(undefined)).toBe('')
    })

    it('handles unicode characters', () => {
      expect(generateSlug('Café & Résumé')).toBe('caf-rsum')
    })

    it('trims leading and trailing hyphens', () => {
      expect(generateSlug('  Test  ')).toBe('test')
      expect(generateSlug('---Test---')).toBe('test')
    })
  })

  describe('Edge cases and error handling', () => {
    it('handles very long strings', () => {
      const veryLongString = 'a'.repeat(10000)
      const result = generateSlug(veryLongString)
      expect(result).toBe('a'.repeat(10000))
    })

    it('handles strings with only special characters', () => {
      expect(generateSlug('!@#$%^&*()')).toBe('')
    })

    it('handles strings with only spaces', () => {
      expect(generateSlug('   ')).toBe('')
    })

    it('handles mixed case correctly', () => {
      expect(generateSlug('MiXeD cAsE')).toBe('mixed-case')
    })
  })
})
