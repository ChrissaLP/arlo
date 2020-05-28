import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Progress from '.'
import { FileProcessingStatus } from '../useJurisdictions'

jest.mock('react-router', () => ({
  useParams: jest.fn().mockReturnValue({ electionId: '1' }),
}))

const jurisdictions = {
  beforeAudit: [
    {
      id: 'jurisdiction-id-1',
      name: 'Jurisdiction One',
      ballotManifest: {
        file: null,
        processing: null,
        numBallots: null,
        numBatches: null,
      },
      currentRoundStatus: null,
    },
    {
      id: 'jurisdiction-id-2',
      name: 'Jurisdiction Two',
      ballotManifest: {
        file: {
          name: 'manifest.csv',
          uploadedAt: '2020-05-05T17:25:25.663592',
        },
        processing: {
          completedAt: '2020-05-05T17:25:26.099157',
          error: null,
          startedAt: '2020-05-05T17:25:26.097433',
          status: 'PROCESSED' as FileProcessingStatus,
        },
        numBallots: 2117,
        numBatches: 10,
      },
      currentRoundStatus: null,
    },
    {
      id: 'jurisdiction-id-3',
      name: 'Jurisdiction Three',
      ballotManifest: {
        file: {
          name: 'manifest.csv',
          uploadedAt: '2020-05-05T17:25:25.663592',
        },
        processing: {
          completedAt: '2020-05-05T17:25:26.099157',
          error: 'Invalid CSV',
          startedAt: '2020-05-05T17:25:26.097433',
          status: 'ERRORED' as FileProcessingStatus,
        },
        numBallots: null,
        numBatches: null,
      },
      currentRoundStatus: null,
    },
  ],
}

describe('Progress screen', () => {
  it('before the audit starts shows ballot manifest upload status', async () => {
    const { container } = render(
      <Progress jurisdictions={jurisdictions.beforeAudit} />
    )

    // Check basic data is all there
    screen.getByText('Audit Progress by Jurisdiction')
    screen.getByText('Jurisdiction One')
    screen.getByText('No manifest uploaded')
    screen.getByText('Jurisdiction Two')
    screen.getByText('Manifest received')
    screen.getByText('Jurisdiction Three')
    screen.getByText('Manifest upload failed: Invalid CSV')
    expect(container).toMatchSnapshot()

    // Switch is disabled, because there's no ballot info yet
    expect(
      screen.getByRole('checkbox', { name: 'Count unique sampled ballots' })
    ).toBeDisabled()

    // Click on a jurisdiction name to open the detail modal
    userEvent.click(screen.getByText('Jurisdiction One'))
    screen.getByText('Jurisdiction One Audit Information')
    expect(container).toMatchSnapshot()

    // Close the detail modal
    userEvent.click(screen.getAllByRole('button', { name: 'Close' })[0])
    expect(
      screen.queryByText('Jurisdiction One Audit Information')
    ).not.toBeInTheDocument()
  })
})
