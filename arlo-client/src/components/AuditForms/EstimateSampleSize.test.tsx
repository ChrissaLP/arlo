import React from 'react'
import { render } from '@testing-library/react'
import EstimateSampleSize from './EstimateSampleSize'
import { mockAudit } from './_mocks'

it('renders corretly', () => {
  const container = render(
    <EstimateSampleSize
      audit={mockAudit}
      isLoading={false}
      setIsLoading={jest.fn()}
      updateAudit={jest.fn()}
    />
  )
  expect(container).toMatchSnapshot()
})
