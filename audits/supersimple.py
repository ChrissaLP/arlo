import math
from scipy import stats
from audits.audit import RiskLimitingAudit


class SuperSimple(RiskLimitingAudit):
    def __init__(self, risk_limit):
        self.l = 0.5
        self.gamma = 1.03905 # This gamma is used in Stark's tool, AGI, and CORLA 


        # This sets the expected number of one-vote misstatements at 1 in 1000
        self.o1 = 0.001
        self.u1 = 0.001

        # This sets the expected two-vote misstatements at 1 in 10000
        self.o2 = 0.0001
        self.u2 = 0.0001

        super().__init__(risk_limit)

    def compute_diluted_margin(self, contests, margins, total_ballots):
        """
        Computes the diluted margin across all contests

        Input:
            contests - dictionary of targeted contests. Maps:
                        {
                            contest: {
                                candidate1: votes,
                                candidate2: votes,
                                ...
                                'ballots': ballots, # total ballots cast
                                'winners': winners # number of winners in this contest
                            }
                            ...
                        }
            margins - dictionary of diluted margin info:
                        {
                            contest: {
                                'winners': {
                                    winner1: {
                                              'p_w': p_w,     # Proportion of ballots for this winner
                                              's_w': 's_w'    # proportion of votes for this winner 
                                              'swl': {      # fraction of votes for w among (w, l)
                                                    'loser1':  s_w/(s_w + s_l1),
                                                    ...,
                                                    'losern':  s_w/(s_w + s_ln)
                                                }
                                              }, 
                                    ..., 
                                    winnern: {...} ] 
                                'losers': {
                                    loser1: {
                                              'p_l': p_l,     # Proportion of votes for this loser
                                              's_l': s_l,     # Proportion of ballots for this loser
                                              }, 
                                    ..., 
                                    losern: {...} ] 
                                
                            }
                        }

        Output:
            diluted_margin - the overall diluted margin, i.e. the smallest margin divided by
                             total ballots cast in audited contests.
        """

        closest_margin = total_ballots
        for contest in contests:
            for winner in margins[contest]['winners']:
                for loser in margins[contest]['losers']:
                    margin = contests[contest][winner] - contests[contest][
                        loser]

                    if margin < closest_margin:
                        closest_margin = margin

        return closest_margin / total_ballots

    def get_sample_sizes(self, contests, margins, total_ballots,
                         reported_results, sample_results):
        """
        Computes initial sample sizes parameterized by likelihood that the
        initial sample will confirm the election result, assuming no
        discrepancies.

        Inputs:
            total_ballots  - the total number of ballots cast in the election
            sample_results - if a sample has already been drawn, this will
                             contain its results, of the form:
                             {
                                'sample_size': n,
                                '1-under':     u1,
                                '1-over':      o1,
                                '2-under':     u2,
                                '2-over':      o2,
                             } 

        Outputs:
            samples - dictionary mapping confirmation likelihood to sample size:
                    {
                       contest1:  { 
                            likelihood1: sample_size,
                            likelihood2: sample_size,
                            ...
                        },
                        ...
                    }
        """


        diluted_margin = self.compute_diluted_margin(contests, margins,
                                                     total_ballots)

        obs_o1 = sample_results['1-over']
        obs_u1 = sample_results['1-under']
        obs_o2 = sample_results['2-over']
        obs_u2 = sample_results['2-under']
        num_sampled = sample_results['sample_size']

        if num_sampled:
            r1 = obs_o1/num_sampled
            r2 = obs_o2/num_sampled
            s1 = obs_u1/num_sampled
            s2 = obs_u2/num_sampled
        else:
            r1 = self.o1
            r2 = self.o2
            s1 = self.u1
            s2 = self.u2


        denom = math.log(1 - diluted_margin/(2*self.gamma)) - \
                r1*math.log(1 - 1/(2*self.gamma)) -     \
                r2*math.log(1 - 1/self.gamma) -         \
                s1*math.log(1 + 1/(2*self.gamma)) -     \
                s2*math.log(1 + 1/self.gamma)      

        if denom >= 0:
            return total_ballots

        return math.ceil(math.log(self.risk_limit)/denom)

    def compute_risk(self, contests, margins, cvrs, sample_cvr):
        """
        Computes the risk-value of <sample_results> based on results in <contest>.

        Inputs: 
            contests       - the contests and results being audited
            margins        - the margins for the contest being audited
            cvrs           - mapping of ballot_id to votes:
                    {
                        'ballot_id': {
                            'contest': {
                                'candidate1': 1,
                                'candidate2': 0,
                                ...
                            }
                        ...
                    }

            sample_cvr - the CVR of the audited ballot  
                    {
                        'ballot_id': {
                            'contest': {
                                'candidate1': 1,
                                'candidate2': 0,
                                ...
                            }
                        ...
                    }

        Outputs:
            measurements    - the p-value of the hypotheses that the election
                              result is correct based on the sample, for each winner-loser pair. 
            confirmed       - a boolean indicating whether the audit can stop
        """

        p = 1

        diluted_margin = self.compute_diluted_margin(contests, margins,
                                                     len(cvrs))
        V = diluted_margin * len(cvrs)

        U = 2 * self.gamma / diluted_margin

        result = False
        for ballot in sample_cvr:
            e_r = 0

            for contest in contests:
                if contest not in sample_cvr[ballot]:
                    continue
                for winner in margins[contest]['winners']:
                    for loser in margins[contest]['losers']:
                        v_w = cvrs[ballot][contest][winner]
                        a_w = sample_cvr[ballot][contest][winner]

                        v_l = cvrs[ballot][contest][loser]
                        a_l = sample_cvr[ballot][contest][loser]

                        V_wl = contests[contest][winner] - contests[contest][
                            loser]

                        e = ((v_w - a_w) - (v_l - a_l)) / V_wl
                        if e > e_r:
                            e_r = e

            p_b = (1 - 1 / U) / (1 - (e_r / ((2 * self.gamma) / V)))
            p *= p_b

        if p < self.risk_limit:
            result = True

        return p, result
