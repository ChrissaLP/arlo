import React from 'react'
import { render, fireEvent, wait, waitForElement } from '@testing-library/react'
import { Router } from 'react-router-dom'
import { createMemoryHistory } from 'history'
import Ballot from './Ballot'
import { contest, dummyBallots } from './_mocks'

const history = createMemoryHistory()

describe('Ballot', () => {
  it('renders correctly with an unaudited ballot', () => {
    const { container } = render(
      <Router history={history}>
        <Ballot
          home="/election/1/audit-board/1"
          ballots={dummyBallots.ballots}
          boardName="audit board #1"
          contests={[contest]}
          previousBallot={jest.fn()}
          nextBallot={jest.fn()}
          submitBallot={jest.fn()}
          batchId="batch-id-1"
          ballotPosition={2112}
        />
      </Router>
    )
    expect(container).toMatchSnapshot()
  })

  it('renders correctly with an audited ballot', () => {
    const { container, getByLabelText } = render(
      <Router history={history}>
        <Ballot
          home="/election/1/audit-board/1"
          ballots={dummyBallots.ballots}
          boardName="audit board #1"
          contests={[contest]}
          previousBallot={jest.fn()}
          nextBallot={jest.fn()}
          submitBallot={jest.fn()}
          batchId="batch-id-1"
          ballotPosition={313}
        />
      </Router>
    )
    const choiceOneButton = getByLabelText('Choice One')
    expect(choiceOneButton).toBeTruthy()
    expect(choiceOneButton).toHaveProperty('checked', true)
    expect(container).toMatchSnapshot()
  })

  it('switches audit and review views', async () => {
    const { container, getByText, getByTestId } = render(
      <Router history={history}>
        <Ballot
          home="/election/1/audit-board/1"
          ballots={dummyBallots.ballots}
          boardName="audit board #1"
          contests={[contest]}
          previousBallot={jest.fn()}
          nextBallot={jest.fn()}
          submitBallot={jest.fn()}
          batchId="batch-id-1"
          ballotPosition={2112}
        />
      </Router>
    )

    fireEvent.click(getByTestId('choice-id-1'), { bubbles: true })
    await wait(() =>
      fireEvent.click(getByTestId('enabled-review'), { bubbles: true })
    )
    await wait(() => {
      expect(getByText('Submit & Next Ballot')).toBeTruthy()
    })
    await wait(() => {
      expect(container).toMatchSnapshot()
    })
    fireEvent.click(getByText('Edit'), { bubbles: true })
    await wait(() => {
      expect(getByText('Choice One')).toBeTruthy()
      expect(getByText('Review')).toBeTruthy()
    })
  })

  const buttonLabels = [
    "Audit board can't agree",
    'Overvote/Blank vote/Not on Ballot',
  ]
  buttonLabels.forEach(buttonLabel => {
    it(`selects ${buttonLabel}`, async () => {
      const { container, getByLabelText, getByText, getByTestId } = render(
        <Router history={history}>
          <Ballot
            home="/election/1/audit-board/1"
            ballots={dummyBallots.ballots}
            boardName="audit board #1"
            contests={[contest]}
            previousBallot={jest.fn()}
            nextBallot={jest.fn()}
            submitBallot={jest.fn()}
            batchId="batch-id-1"
            ballotPosition={2112}
          />
        </Router>
      )

      fireEvent.click(getByLabelText(buttonLabel), {
        bubbles: true,
      })
      await wait(() =>
        fireEvent.click(getByTestId('enabled-review'), { bubbles: true })
      )
      await wait(() => expect(getByText('Submit & Next Ballot')).toBeTruthy())
      await wait(() => {
        expect(getByText(buttonLabel)).toBeTruthy()
        expect(container).toMatchSnapshot()
      })
    })
  })

  it('toggles and submits comment', async () => {
    const { container, getByText, getByTestId, queryByText } = render(
      <Router history={history}>
        <Ballot
          home="/election/1/audit-board/1"
          ballots={dummyBallots.ballots}
          boardName="audit board #1"
          contests={[contest]}
          previousBallot={jest.fn()}
          nextBallot={jest.fn()}
          submitBallot={jest.fn()}
          batchId="batch-id-1"
          ballotPosition={2112}
        />
      </Router>
    )

    fireEvent.click(getByText('Add comment'), { bubbles: true })

    const commentInput = getByTestId('comment-textarea')
    fireEvent.change(commentInput, { target: { value: 'a test comment' } })

    fireEvent.click(getByTestId('choice-id-1'), { bubbles: true })
    await wait(() =>
      fireEvent.click(getByTestId('enabled-review'), { bubbles: true })
    )
    await wait(() => {
      expect(getByText('Submit & Next Ballot')).toBeTruthy()
      expect(getByText('COMMENT: a test comment')).toBeTruthy()
      expect(container).toMatchSnapshot()
    })

    // Go back and make sure an empty comment doesn't get saved
    fireEvent.click(getByText('Edit'), { bubbles: true })

    fireEvent.change(commentInput, { target: { value: '' } })

    fireEvent.click(getByTestId('choice-id-1'), { bubbles: true })
    await wait(() =>
      fireEvent.click(getByTestId('enabled-review'), { bubbles: true })
    )
    await wait(() => {
      expect(queryByText('COMMENT:')).toBeFalsy()
    })
  })

  it('toggles and deletes a comment', async () => {
    const { container, getByText, queryByText, getByTestId } = render(
      <Router history={history}>
        <Ballot
          home="/election/1/audit-board/1"
          ballots={dummyBallots.ballots}
          boardName="audit board #1"
          contests={[contest]}
          previousBallot={jest.fn()}
          nextBallot={jest.fn()}
          submitBallot={jest.fn()}
          batchId="batch-id-1"
          ballotPosition={2112}
        />
      </Router>
    )

    fireEvent.click(getByText('Add comment'), { bubbles: true })

    const commentInput = getByTestId('comment-textarea')
    fireEvent.change(commentInput, { target: { value: 'a test comment' } })

    fireEvent.click(getByText('Remove comment'), { bubbles: true })

    fireEvent.click(getByTestId('choice-id-1'), { bubbles: true })
    await wait(() =>
      fireEvent.click(getByTestId('enabled-review'), { bubbles: true })
    )
    await wait(() => {
      expect(getByText('Submit & Next Ballot')).toBeTruthy()
      expect(queryByText('COMMENT: a test comment')).toBeFalsy()
      expect(container).toMatchSnapshot()
    })
  })

  it('submits review and progresses to next ballot', async () => {
    const submitMock = jest.fn()
    const nextBallotMock = jest.fn()
    const { container, getByText, getByTestId } = render(
      <Router history={history}>
        <Ballot
          home="/election/1/audit-board/1"
          ballots={dummyBallots.ballots}
          boardName="audit board #1"
          contests={[contest]}
          previousBallot={jest.fn()}
          nextBallot={nextBallotMock}
          submitBallot={submitMock}
          batchId="batch-id-1"
          ballotPosition={2112}
        />
      </Router>
    )

    fireEvent.click(getByTestId('choice-id-1'), { bubbles: true })

    const reviewButton = await waitForElement(
      () => getByTestId('enabled-review'),
      { container }
    )
    fireEvent.click(reviewButton, { bubbles: true })
    const nextButton = await waitForElement(
      () => getByText('Submit & Next Ballot'),
      { container }
    )
    fireEvent.click(nextButton, { bubbles: true })

    await wait(() => {
      expect(nextBallotMock).toBeCalled()
      expect(submitMock).toHaveBeenCalledTimes(1)
    })
  })

  it('navigates to previous ballot', async () => {
    const previousBallotMock = jest.fn()
    const { getByText, getByTestId } = render(
      <Router history={history}>
        <Ballot
          home="/election/1/audit-board/1"
          ballots={dummyBallots.ballots}
          boardName="audit board #1"
          contests={[contest]}
          previousBallot={previousBallotMock}
          nextBallot={jest.fn()}
          submitBallot={jest.fn()}
          batchId="batch-id-1"
          ballotPosition={2112}
        />
      </Router>
    )
    fireEvent.click(getByText('Back'), { bubbles: true })

    await wait(() => {
      expect(previousBallotMock).toBeCalledTimes(1)
    })

    fireEvent.click(getByTestId('choice-id-1'), { bubbles: true })
    await wait(() =>
      fireEvent.click(getByTestId('enabled-review'), { bubbles: true })
    )
    await wait(() => {
      expect(getByText('Submit & Next Ballot')).toBeTruthy()
    })
    fireEvent.click(getByText('Back'), { bubbles: true })
    await wait(() => {
      expect(getByText('Review')).toBeTruthy()
    })
  })

  it('redirects if ballot does not exist', async () => {
    const { container } = render(
      <Router history={history}>
        <Ballot
          home="/election/1/audit-board/1"
          ballots={dummyBallots.ballots}
          boardName="audit board #1"
          contests={[contest]}
          previousBallot={jest.fn()}
          nextBallot={jest.fn()}
          submitBallot={jest.fn()}
          batchId="batch-id"
          ballotPosition={6}
        />
      </Router>
    )

    await wait(() => {
      expect(container).toMatchSnapshot()
    })
  })
})
