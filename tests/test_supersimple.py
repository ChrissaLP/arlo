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


    yield Sampler('SuperSimple', seed, risk_limit, contests, cvrs=[1]*100001)


def test_compute_diluted_margin(sampler):

    computed = sampler.audit.compute_diluted_margin(sampler.contests, sampler.margins, 100000)
    expected = 0.02

    assert computed == expected, 'Diluted margin computation incorrect: got {}, expected {}'.format(computed, expected)

def test_get_sample_sizes(sampler):

    computed = sampler.get_sample_sizes(None)
    expected = 761 # From Stark, though his paper has rounding errors so we add 1. 

    assert computed == expected, 'Sample size computation incorrect: got {}, expected {}'.format(computed, expected)

