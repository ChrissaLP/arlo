import pytest
import math
import numpy as np

from sampler import Sampler

@pytest.fixture
def sampler():
    seed = '12345678901234567890abcdefghijklmnopqrstuvwxyz😊'

    risk_limit = .1
    contests = {
        'Contest A': {
            'winner': 60000,
            'loser': 40000,
            'ballots': 100000,
            'numWinners': 1,
        },
        'Contest B': {
            'winner': 30000,
            'loser': 24000,
            'ballots': 60000,
            'numWinners': 1,
        },
        'Contest C': {
            'winner': 18000,
            'loser': 12600,
            'ballots': 36000,
            'numWinners': 1,
        },
        'Contest D': {
            'winner': 8000,
            'loser': 6000,
            'ballots': 15000,
            'numWinners': 1
        },
        'Contest E': {
            'winner': 10000,
            'loser': 0,
            'ballots': 10000,
            'numWinners': 1
        }
    }


    cvr = {}
    for i in range(100000):
        contest_a_res = None
        contest_b_res = None
        contest_c_res = None
        contest_d_res = None
        contest_e_res = None


        if i < 60000:
            contest_a_res = {
                'winner': 1,
                'loser': 0
            }
        else: 
            contest_a_res = {
                'winner': 0,
                'loser': 1
            }

        if i < 30000:
            contest_b_res = {
                'winner': 1,
                'loser': 0
            }
        elif i > 30000 and i < 60000:
            contest_b_res = {
                'winner': 0,
                'loser': 1
            }
             
        if i < 18000:
            contest_c_res = {
                'winner': 1,
                'loser': 0
            }
        elif i > 18000 and i < 30600:
            contest_c_res = {
                'winner': 0,
                'loser': 1
            }

        if i < 8000:
            contest_d_res = {
                'winner': 1,
                'loser': 0
            }
        elif i > 8000 and i < 14000:
            contest_d_res = {
                'winner': 0,
                'loser': 1
            }

        if i < 10000:
            contest_e_res = {
                'winner': 1,
                'loser': 0
            }

        cvr[i] = {
                'Contest A': contest_a_res
        }

        if contest_b_res:
            cvr[i]['Contest B'] = contest_b_res

        if contest_c_res:
            cvr[i]['Contest C'] = contest_c_res
        if contest_d_res:
            cvr[i]['Contest D'] = contest_d_res
        if contest_e_res:
            cvr[i]['Contest E'] = contest_e_res


    yield Sampler('SuperSimple', seed, risk_limit, contests, cvrs=cvr)


def test_compute_diluted_margin(sampler):

    computed = sampler.audit.compute_diluted_margin(sampler.contests, sampler.margins, 100000)
    expected = 0.02

    assert computed == expected, 'Diluted margin computation incorrect: got {}, expected {}'.format(computed, expected)

def test_get_sample_sizes(sampler):

    computed = sampler.get_sample_sizes(None)
    expected = 761 # From Stark, though his paper has rounding errors so we add 1. 

    assert computed == expected, 'Sample size computation incorrect: got {}, expected {}'.format(computed, expected)

def test_compute_risk(sampler):
    sample_cvr = {}
    for i in range(500):
        sample_cvr[i] = {
            'Contest A': {
                'winner': 1,
                'loser': 0
            },
            'Contest B': {
                'winner': 1,
                'loser': 0
            },
            'Contest C': {
                'winner': 1,
                'loser': 0
            },
            'Contest D': {
                'winner': 1,
                'loser': 0
            },
            'Contest E': {
                'winner': 1,
                'loser': 0
            },
        }

    computed, finished = sampler.audit.compute_risk(sampler.contests, sampler.margins, sampler.cvrs, sample_cvr)
    bound  = 0.01
    delta = 0.0005 # Stark's math was roughly rounded? So deal with it

    assert computed <= bound + delta, 'Computed risk {} is above the bound {}!'.format(computed, bound)
    assert computed > bound - delta, 'Computed risk {} is unexpectedly low!'.format(computed)
    assert finished, 'Audit should have finished but didn\'t'

    # Test one-vote overstatement 
    sample_cvr[0] = {
            'Contest A': {
                'winner': 0,
                'loser': 0
            },
            'Contest B': {
                'winner': 0,
                'loser': 0
            },
            'Contest C': {
                'winner': 0,
                'loser': 0
            },
            'Contest D': {
                'winner': 0,
                'loser': 0
            },
            'Contest E': {
                'winner': 0,
                'loser': 0
            },
    }

    bound = 0.019
    computed, finished = sampler.audit.compute_risk(sampler.contests, sampler.margins, sampler.cvrs, sample_cvr)
    assert computed <= bound + delta, 'Computed risk {} is above the bound {}!'.format(computed, bound)
    assert computed > bound - delta, 'Computed risk {} is unexpectedly low!'.format(computed)
    assert finished, 'Audit should have finished but didn\'t'
    
    # Test two-vote overstatement 
    sample_cvr[0] = {
            'Contest A': {
                'winner': 0,
                'loser': 1
            },
            'Contest B': {
                'winner': 0,
                'loser': 1
            },
            'Contest C': {
                'winner': 0,
                'loser': 1
            },
            'Contest D': {
                'winner': 0,
                'loser': 1
            },
            'Contest E': {
                'winner': 0,
                'loser': 1
            },
    }

    bound = 0.114
    computed, finished = sampler.audit.compute_risk(sampler.contests, sampler.margins, sampler.cvrs, sample_cvr)

    assert computed <= bound + delta, 'Computed risk {} is above the bound {}!'.format(computed, bound)
    assert computed > bound - delta, 'Computed risk {} is unexpectedly low!'.format(computed)
    assert not finished, 'Audit shouldn\'t have finished but did!'


    sample_cvr[1] = {
            'Contest A': {
                'winner': 0,
                'loser': 1
            },
            'Contest B': {
                'winner': 0,
                'loser': 1
            },
            'Contest C': {
                'winner': 0,
                'loser': 1
            },
            'Contest D': {
                'winner': 0,
                'loser': 1
            },
            'Contest E': {
                'winner': 0,
                'loser': 1
            },
    }

    sample_cvr[2] = {
            'Contest A': {
                'winner': 0,
                'loser': 1
            },
            'Contest B': {
                'winner': 0,
                'loser': 1
            },
            'Contest C': {
                'winner': 0,
                'loser': 1
            },
            'Contest D': {
                'winner': 0,
                'loser': 1
            },
            'Contest E': {
                'winner': 0,
                'loser': 1
            },
    }

    bound = 1 
    computed, finished = sampler.audit.compute_risk(sampler.contests, sampler.margins, sampler.cvrs, sample_cvr)

    assert computed <= bound + delta, 'Computed risk {} is above the bound {}!'.format(computed, bound)
    assert computed > bound - delta, 'Computed risk {} is unexpectedly low!'.format(computed)
    assert not finished, 'Audit shouldn\'t have finished but did!'
