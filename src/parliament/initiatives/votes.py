from collections import defaultdict
from typing import List

import numpy as np
import pandas as pd


def get_party_approvals(data_initiatives_votes: pd.DataFrame) -> pd.DataFrame:
    """
    Manipulate the votes to get the percentage of approval per party for each other party
    """

    if len(data_initiatives_votes) == 0:
        return pd.DataFrame()

    data_initiatives_votes = data_initiatives_votes.copy()

    # get all party votes fields
    parties_vote_direction_fields = [
        x for x in data_initiatives_votes.columns if x.startswith("iniciativa_votacao")
    ]
    to_exclude = "iniciativa_votacao_res iniciativa_votacao_desc iniciativa_votacao_outros_afavor iniciativa_votacao_outros_abstenção iniciativa_votacao_outros_contra iniciativa_votacao_outros_ausência iniciativa_votacao_unanime".split()
    parties_vote_direction_fields = list(
        set(parties_vote_direction_fields) - set(to_exclude)
    )

    # when the vote was unanimous, individual party vote direction is empty
    # with this code we fix it
    unanime_rows = data_initiatives_votes["iniciativa_votacao_unanime"] == "unanime"
    new_values = data_initiatives_votes.loc[
        unanime_rows, parties_vote_direction_fields
    ].applymap(
        lambda x: "afavor" if pd.isna(x) else x
    )  # move all NaN values to "afavor"
    data_initiatives_votes.loc[unanime_rows, parties_vote_direction_fields] = new_values

    def calculate_vote_distribution(
        group: pd.DataFrame, parties_vote_direction_fields: List[str]
    ) -> pd.Series:
        values = [
            group["iniciativa_aprovada"].count(),
            group["iniciativa_aprovada"].mean(),
        ]

        # add the number of initiatives and % of approved initiatives for this group
        res = pd.Series(values, "total_iniciativas total_iniciativas_aprovadas".split())

        # add approval distribution per party
        res = pd.concat(
            [res, (group[parties_vote_direction_fields] == "afavor").mean()]
        )

        return res

    return (
        data_initiatives_votes.groupby("iniciativa_autor")
        .apply(lambda x: calculate_vote_distribution(x, parties_vote_direction_fields))
        .sort_values("total_iniciativas", ascending=False)
    )


def get_party_correlations(data_initiatives_votes: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the number of times each party pair voted the same
    """

    if len(data_initiatives_votes) == 0:
        return pd.DataFrame()

    # get all party votes fields
    parties_columns = [
        x for x in data_initiatives_votes.columns if x.startswith("iniciativa_votacao")
    ]
    to_exclude = "iniciativa_votacao_res iniciativa_votacao_desc iniciativa_votacao_outros_afavor iniciativa_votacao_outros_abstenção iniciativa_votacao_outros_contra iniciativa_votacao_outros_ausência iniciativa_votacao_unanime".split()
    parties_columns = list(set(parties_columns) - set(to_exclude))

    res = defaultdict(list)
    for party_a in parties_columns:
        for party_b in parties_columns:
            pa = data_initiatives_votes.loc[
                ~data_initiatives_votes[party_a].isin(["ausência", ""]), party_a
            ]
            pb = data_initiatives_votes.loc[
                ~data_initiatives_votes[party_b].isin(["ausência", ""]), party_b
            ]
            # indexes that we should consider
            indexes = pa.dropna().index.intersection(pb.dropna().index)
            if len(indexes) == 0:
                res[party_a].append(0)
            else:
                corr = pd.crosstab(pa[indexes], pb[indexes], margins=True)
                diag = np.diag(corr)

                total = diag[-1]
                total_corr = diag[:-1].sum()

                res[party_a].append(total_corr / total)

    return (
        pd.DataFrame(res, index=parties_columns)
        .reset_index()
        .rename(columns={"index": "nome"})
    )


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

    parties_columns = [
        x for x in data_initiatives_votes.columns if x.startswith("iniciativa_votacao")
    ]
    to_exclude = "iniciativa_votacao_res iniciativa_votacao_desc iniciativa_votacao_outros_afavor iniciativa_votacao_outros_abstenção iniciativa_votacao_outros_contra iniciativa_votacao_outros_ausência iniciativa_votacao_unanime".split()
    parties_columns = list(set(parties_columns) - set(to_exclude))

    data = []
    for col in parties_columns:
        party = (
            col.replace("iniciativa_votacao_", "")
            .replace("cr", "CRISTINA RODRIGUES")
            .replace("jkm", "JOACINE KATAR MOREIRA")
            .upper()
        )

        mask = (data_initiatives_votes["iniciativa_autor"] == party) & (
            (data_initiatives_votes[col] != "afavor")
            | data_initiatives_votes[col].isnull()
        )
        errors = data_initiatives_votes.loc[mask, col]

        data.append(
            {
                "party": party,
                "invalid_entries": len(errors)
                / (data_initiatives_votes["iniciativa_autor"] == party).sum(),
            }
        )

    return pd.DataFrame(data).set_index("party")


def get_initiatives(data_initiatives_votes: pd.DataFrame) -> pd.DataFrame:
    """
    Get all initiatives, removing not needed fields
    """

    data_initiatives_votes = data_initiatives_votes.copy()

    # get needed fields' name
    parties_vote_direction_fields = [
        x for x in data_initiatives_votes.columns if x.startswith("iniciativa_votacao")
    ]
    to_exclude = "iniciativa_votacao_res iniciativa_votacao_desc iniciativa_votacao_outros_afavor iniciativa_votacao_outros_abstenção iniciativa_votacao_outros_contra iniciativa_votacao_outros_ausência iniciativa_votacao_unanime".split()
    parties_vote_direction_fields = list(
        set(parties_vote_direction_fields) - set(to_exclude)
    )

    # when the vote was unanimous, individual party vote direction is empty
    # with this code we fix it
    unanime_rows = data_initiatives_votes["iniciativa_votacao_unanime"] == "unanime"
    new_values = data_initiatives_votes.loc[
        unanime_rows, parties_vote_direction_fields
    ].applymap(
        lambda x: "afavor" if pd.isna(x) else x
    )  # move all NaN values to "afavor"
    data_initiatives_votes.loc[unanime_rows, parties_vote_direction_fields] = new_values

    # add addtional column
    data_initiatives_votes["iniciativa_url_res"] = (
        "https://www.parlamento.pt/ActividadeParlamentar/Paginas/DetalheIniciativa.aspx?BID="
        + data_initiatives_votes["iniciativa_id"]
    )

    columns = [
        "iniciativa_evento_fase",
        "iniciativa_titulo",
        "iniciativa_url",
        "iniciativa_url_res",
        "iniciativa_autor",
        "iniciativa_autor_deputados_nomes",
        "iniciativa_evento_data",
        "iniciativa_tipo",
        "iniciativa_votacao_res",
    ] + parties_vote_direction_fields

    df = data_initiatives_votes[columns].rename(
        {
            "iniciativa_evento_data": "iniciativa_data",
            "iniciativa_evento_fase": "iniciativa_fase",
        },
        axis="columns",
    )

    df["iniciativa_data"] = df["iniciativa_data"].dt.strftime("%Y-%m-%d")

    return df.reset_index().rename(columns={"index": "iniciativa_id"})
