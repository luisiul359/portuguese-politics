# endpoints updated daily
# XIV Legislatura
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict

import requests

from daily_updater.common import get_most_recent_status

PATH_XIV = "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063484d364c793968636d356c64433976634756755a4746305953394559575276633046695a584a3062334d76513239746347397a61634f6e77364e764a5449775a47556c4d6a44446b334a6e77364e76637939595356596c4d6a424d5a576470633278686448567959533950636d646862304e766258427663326c6a5957395953565a66616e4e76626935306548513d&fich=OrgaoComposicaoXIV_json.txt&Inline=true"
# XIV Legislatura
PATH_XV = "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063484d364c793968636d356c64433976634756755a4746305953394559575276633046695a584a3062334d76513239746347397a61634f6e77364e764a5449775a47556c4d6a44446b334a6e77364e7663793959566955794d45786c5a326c7a6247463064584a684c3039795a324676513239746347397a61574e68623168575832707a6232347564486830&fich=OrgaoComposicaoXV_json.txt&Inline=true"


@dataclass
class LegislatureMember:
    name: str
    id: str

    def to_dict(self):
        return {"nome": self.name, "dep_id": self.id}


def get_raw_data(path: str) -> List[Dict]:
    """Load the most recent data provided by Parlamento"""

    try:
        payload = requests.get(
            path,
            # fake, but without it the request is rejected
            headers={"User-Agent": "Mozilla/5.0"},
        )
        assert payload.status_code == 200

        return payload.json()["OrganizacaoAR"]
    except Exception as e:
        print(path)
        raise e


def get_chair_of_general_assembly(organization_general_assembly: Dict) -> Dict:
    x = organization_general_assembly["MesaAR"]
    # getting the acronym of the legislature, eg. XV
    leg_description = x["DetalheOrgao"]["legDes"]
    members = x["HistoricoComposicao"][
        "pt_ar_wsgode_objectos_DadosMesaComposicaoHistorico"
    ]
    president = None
    vice_presidents = []
    for member in members:
        member_role = get_most_recent_status(
            member["depCargo"]["pt_ar_wsgode_objectos_DadosCargoDeputado"],
            "carDtInicio",
        )
        if member_role["carDes"] == "Presidente":
            president = LegislatureMember(
                name=member["depNomeParlamentar"], id=member["depId"]
            )

        elif member_role["carDes"] == "Vice-Presidente":
            vice_presidents.append(
                LegislatureMember(name=member["depNomeParlamentar"], id=member["depId"])
            )

    return {
        "presidente": president.to_dict(),
        "vice_presidentes": [
            vice_president.to_dict() for vice_president in vice_presidents
        ],
        "legislatura": leg_description,
    }


def get_party_deputy_counter(organization_general_assembly: Dict):
    deputies = organization_general_assembly["Plenario"]["Composicao"][
        "pt_ar_wsgode_objectos_DadosDeputadoSearch"
    ]

    party_counter = defaultdict(lambda: 0)
    for deputy in deputies:
        deputy_role = get_most_recent_status(
            deputy["depSituacao"]["pt_ar_wsgode_objectos_DadosSituacaoDeputado"],
            "sioDtInicio",
        )
        party = get_most_recent_status(
            deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"], "gpDtInicio"
        )["gpSigla"]

        if "Efetivo" in deputy_role["sioDes"]:
            party_counter[party] += 1

    return dict(party_counter)


def main():
    data = get_raw_data(path=PATH_XIV)
    chair_of_general_assembly = get_chair_of_general_assembly(data)
    party_counters = get_party_deputy_counter(data)
    total_number_of_deputies = sum(party_counters.values())
    return {
        **chair_of_general_assembly,
        **{
            "partidos": [
                {
                    "nome": party_name,
                    "nr_deputados": party_counter,
                    "percentagem_deputados_total": round(
                        party_counter / total_number_of_deputies * 100, 1
                    ),
                    "lider_de_bancada": "ze manel",
                }
                for party_name, party_counter in party_counters.items()
            ]
        },
    }


a = main()
print(a)
