from typing import Dict, List, Union, Tuple

import pandas as pd
import requests

PATH_LEGISLATIVAS_2019 = "https://raw.githubusercontent.com/Politica-Para-Todos/ppt-archive/master/legislativas/legislativas-2019/data.json"

# mapping between party and manifesto inside PPT repo
PARTY_TO_MANIFESTO_LEGISLATIVAS_2019 = {
    "A": "alianca_020919.md",
    "BE": "be_120919.md",
    "CDS-PP": "cdspp.md",
    "CH": "CHEGA_201909.md",
    "IL": "Iniciativa Liberal.md",
    "L": "livre.md",
    "MAS": "mas.md",
    "NC": "NOS_CIDADAOS_Set2019.md",
    "PCTP/MRPP": "PCTP.md",
    "PCP-PEV": ["PCP.md", "pev_31082019.md"],
    "MPT": "mpt27092019.md",
    "PDR": "PDR_22092019.md",
    "PNR": "pnr.md",
    "PPD/PSD": "psd.md",
    "PS": "PS_01092019.md",
    "PURP": "PURP.md",
    "PAN": "pan_31082019.md",
    "RIR": "RIR.md",
}


def get_data(path: str) -> Dict:
    """Load the most recent data provided by PPT"""

    try:
        payload = requests.get(path)
        assert payload.status_code == 200

        return payload.json()
    except Exception as e:
        print(path)
        raise e


def extract_legislativas_2019() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract Portuguese Legislativas 2019 information from PPT community

    Will return info regarding parties and regarding candidates
    """

    # load data
    raw_legislativas_2019 = get_data(PATH_LEGISLATIVAS_2019)

    # we do not use this information
    raw_legislativas_2019.pop("manifestos")

    def _get_manifesto(party) -> Union[str, List]:
        manifesto = PARTY_TO_MANIFESTO_LEGISLATIVAS_2019.get(party, "")
        # deal with alliances
        if isinstance(manifesto, list):
            return [
                f"https://raw.githubusercontent.com/Politica-Para-Todos/manifestos/master/legislativas/20191006_legislativas/{m}"
                for m in manifesto
            ]

        return (
            f"https://raw.githubusercontent.com/Politica-Para-Todos/manifestos/master/legislativas/20191006_legislativas/{manifesto}"
            if manifesto
            else ""
        )

    parties = []
    candidates = []

    def clean_str(txt: str) -> str:
        return None if txt in ["-", ""] else txt

    for party, values in raw_legislativas_2019["parties"].items():
        tmp_party = {
            "acronym": party.strip(),
            "name": clean_str(values.get("name", "").strip()),
            "description": clean_str(values.get("description", "").strip()),
            "description_source": clean_str(values.get("description_source", "").strip()),
            "email": clean_str(values.get("email", "").strip()),
            "facebook": clean_str(values.get("facebook", "").strip()),
            "instagram": clean_str(values.get("instagram", "").strip()),
            "logo": f"https://raw.githubusercontent.com/Politica-Para-Todos/ppt-archive/master/legislativas/legislativas-2019/partidos_logos/{values['logo']}"
            if "logo" in values
            else None,
            "twitter": clean_str(values.get("twitter", "").strip()),
            "website": clean_str(values.get("website").strip()),
            "manifesto": _get_manifesto(party),
        }

        # store party info
        parties.append(tmp_party)

        for district, main_secundary_candidates in values.get("candidates", {}).items():
            for c in main_secundary_candidates.get(
                "main", []
            ) + main_secundary_candidates.get("secundary", []):
                tmp_candidates = {
                    "party": party.strip(),
                    "district": district.strip(),
                    "name": c.get("name", ""),
                    "position": c.get("position", ""),
                    "type": c.get("type", ""),
                }

                if c.get("is_lead_candidate", False):
                    tmp_candidates.update(
                        {
                            "biography": clean_str(c.get("biography", "")),
                            "biography_source": clean_str(c.get("biography_source", "").strip()),
                            "link_parlamento": clean_str(c.get("link_parlamento", "").strip()),
                            "photo": f"https://raw.githubusercontent.com/Politica-Para-Todos/ppt-archive/master/legislativas/legislativas-2019/cabeca_de_lista_fotos/{c['photo']}"
                            if "photo" in c
                            else None,
                            "photo_source": clean_str(c.get("photo_source", "").strip()),
                        }
                    )

                # store all candidates
                candidates.append(tmp_candidates)

    return pd.DataFrame(parties).set_index("acronym"), pd.DataFrame(candidates)
