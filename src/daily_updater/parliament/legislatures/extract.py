# endpoints updated daily
# XIV Legislatura
from dataclasses import dataclass
from typing import List, Dict

import requests

from daily_updater.common import to_list

PATH_XIV = "todo"
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
        member_roles = to_list(
            member["depCargo"]["pt_ar_wsgode_objectos_DadosCargoDeputado"]
        )
        member_role = list(sorted(member_roles, key=lambda x: x["carDtInicio"]))[-1]
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
    }


a = get_raw_data(path=PATH_XV)

print(get_chair_of_general_assembly(a))
