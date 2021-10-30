import pandas as pd

from typing import List


def get_party_approvals(data_initiatives_votes: pd.DataFrame) -> pd.DataFrame:
    """
    Manipulate the votes to get the percentage of approval per party for each other party
    """
    
    # get all party votes fields
    parties_vote_direction_fields = [x for x in data_initiatives_votes.columns if x.startswith("iniciativa_votacao")]
    to_exclude = "iniciativa_votacao_res iniciativa_votacao_desc iniciativa_votacao_outros_afavor iniciativa_votacao_outros_abstenção iniciativa_votacao_outros_contra".split()
    parties_vote_direction_fields = list(set(parties_vote_direction_fields) - set(to_exclude))

    def calculate_vote_distribution(group: pd.DataFrame, parties_vote_direction_fields: List[str]) -> pd.Series:
        values = [
            group["iniciativa_aprovada"].count(),
            group["iniciativa_aprovada"].mean()
        ]

        # add the number of initiatives and % of approved initiatives for this group
        res = pd.Series(values, "total_iniciativas total_iniciativas_aprovadas".split())

        # add approval distribution per party
        res = res.append((group[parties_vote_direction_fields] == "afavor").mean())

        return res

    return data_initiatives_votes.groupby("iniciativa_autor").apply(lambda x: calculate_vote_distribution(x, parties_vote_direction_fields)).sort_values("total_iniciativas", ascending=False)