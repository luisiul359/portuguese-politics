import pandas as pd
import numpy as np

from typing import List
from collections import defaultdict


def get_party_approvals(data_initiatives_votes: pd.DataFrame) -> pd.DataFrame:
    """
    Manipulate the votes to get the percentage of approval per party for each other party
    """

    if len(data_initiatives_votes) == 0:
        return pd.DataFrame()
    
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


def get_party_correlations(data_initiatives_votes: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the number of times each party pair voted the same
    """

    if len(data_initiatives_votes) == 0:
        return pd.DataFrame()

    # get all party votes fields
    parties_columns = [x for x in data_initiatives_votes.columns if x.startswith("iniciativa_votacao")]
    to_exclude = "iniciativa_votacao_res iniciativa_votacao_desc iniciativa_votacao_outros_afavor iniciativa_votacao_outros_abstenção iniciativa_votacao_outros_contra".split()
    parties_columns = list(set(parties_columns) - set(to_exclude))

    res = defaultdict(list)
    for party_a in parties_columns:
        for party_b in parties_columns:
            pa = data_initiatives_votes.loc[~data_initiatives_votes[party_a].isin(["ausência", ""]), party_a]
            pb = data_initiatives_votes.loc[~data_initiatives_votes[party_b].isin(["ausência", ""]), party_b]
            corr = pd.crosstab(pa, pb, margins=True)
            diag = np.diag(corr)
            
            total = diag[-1]
            total_corr = diag[:-1].sum()

            res[party_a].append(total_corr / total)

    return pd.DataFrame(res, index=parties_columns).reset_index().rename(columns = {'index':'nome'})


def collect_parties_strange_votes(data_initiatives_votes: pd.DataFrame) -> pd.DataFrame:
    """
    Return all entries where the party did not approve its own initiatives.

    In the following situations a party can vote different from approve its
    own initiatives:

    * In Portugal parties with just 1 deputy can't attend commissions where some topics 
    are discussed and voted, even when the initiative its from that party.

    * When the final document is the merge of similar initiatives and the party
    does not agree with that final document

    * In Portugal the deputies must vote equal to the party, but in some situations
    they can vote independently, in those situations we are filling the columns
    "iniciativa_votacao_outros_*" and not the party column
    """

    parties_columns = [x for x in data_initiatives_votes.columns if x.startswith("iniciativa_votacao")]
    to_exclude = "iniciativa_votacao_res iniciativa_votacao_desc iniciativa_votacao_outros_afavor iniciativa_votacao_outros_abstenção iniciativa_votacao_outros_contra".split()
    parties_columns = list(set(parties_columns) - set(to_exclude))

    data = []
    for col in parties_columns:
        party = col.replace("iniciativa_votacao_", "").replace("cr", "CRISTINA RODRIGUES").replace("jkm", "JOACINE KATAR MOREIRA").upper()

        mask = (data_initiatives_votes["iniciativa_autor"] == party) & ((data_initiatives_votes[col] != "afavor") | data_initiatives_votes[col].isnull())
        errors = data_initiatives_votes.loc[mask, col]

        data.append({
            "party": party,
            "invalid_entries": len(errors) / (data_initiatives_votes["iniciativa_autor"] == party).sum()
        })


    return pd.DataFrame(data).set_index("party")


def get_initiatives(data_initiatives_votes: pd.DataFrame) -> pd.DataFrame:
    """
    Get all initiatives, removing not needed fields
    """
    
    # get needed fields' name
    parties_vote_direction_fields = [x for x in data_initiatives_votes.columns if x.startswith("iniciativa_votacao")]
    to_exclude = "iniciativa_votacao_res iniciativa_votacao_desc iniciativa_votacao_outros_afavor iniciativa_votacao_outros_abstenção iniciativa_votacao_outros_contra".split()
    parties_vote_direction_fields = list(set(parties_vote_direction_fields) - set(to_exclude))

    columns = ["iniciativa_evento_fase", "iniciativa_titulo", "iniciativa_url", "iniciativa_autor", "iniciativa_autor_deputados_nomes", "iniciativa_evento_data", "iniciativa_tipo", "iniciativa_votacao_res"] + parties_vote_direction_fields

    df = data_initiatives_votes[columns].rename({
        "iniciativa_evento_data": "iniciativa_data",
        "iniciativa_evento_fase": "iniciativa_fase"
        }, axis="columns")

    df["iniciativa_data"] = df["iniciativa_data"].dt.strftime("%Y-%m-%d").reset_index().rename(columns={"index": "iniciativa_id"})

    return df
