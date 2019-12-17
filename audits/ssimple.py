import math
from scipy import stats
from audits.audit import RiskLimitingAudit

class SuperSimple(RiskLimitingAudit):

    def __init__(self, risk_limit):
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
                    margin = contests[contest][winner] - contests[contest][loser]
                    
                    if margin < closest_margin:
                        closest_margin = margin

        return closest_margin/total_ballots

    def get_sample_sizes(self, contests, margins, total_ballots, reported_results, sample_results):
        """
        Computes initial sample sizes parameterized by likelihood that the
        initial sample will confirm the election result, assuming no
        discrepancies.

        Inputs:
            total_ballots  - the total number of ballots cast in the election
            sample_results - if a sample has already been drawn, this will
                             contain its results. 

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

        # TODO Do we want to fix these values?
        gamma = 1.1
        l = 0.5 

        rho = -math.log(self.risk_limit)/((1/(2*gamma)) + l*math.log(1 - 1/(2*gamma))) 

        diluted_margin = self.compute_diluted_margin(contests, margins, total_ballots)
        return math.ceil(rho*diluted_margin) 

    def compute_risk(self, contests, margins, reported_results, sample_results):
        """
        Computes the risk-value of <sample_results> based on results in <contest>.

        Inputs: 
            contests       - the contests and results being audited
            margins        - the margins for the contest being audited
            reported_results - mapping of candidates to reported votes
            sample_results - mapping of candidates to votes in the (cumulative)
                             sample:

                    {
                        candidate1: sampled_votes,
                        candidate2: sampled_votes,
                        ...
                    }

        Outputs:
            measurements    - the p-value of the hypotheses that the election
                              result is correct based on the sample, for each winner-loser pair. 
            confirmed       - a boolean indicating whether the audit can stop
        """
        
        p = 1


        U = self.compute_U(contests, margins, reported_results)

        for ctr,batch in enumerate(sample_results):
            e_p = self.compute_error(contests, margins, reported_results[batch], sample_results[batch])
            u_p = self.compute_max_error(contests, margins, reported_results[batch])

            taint = e_p/u_p
            print(taint, ctr)

            p *= (1 - 1/U)/(1 - taint)

            if p < self.risk_limit:
               return p, True

        return p, p < self.risk_limit
