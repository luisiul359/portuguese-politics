import requests
import pandas as pd

from typing import Dict, List


# data updated daily
PATH = "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d6c6a6157463061585a68637939595356596c4d6a424d5a57647063327868644856795953394a626d6c6a6157463061585a686331684a566c3971633239754c6e523464413d3d&fich=IniciativasXIV_json.txt&Inline=true"


def get_data(path: str) -> List[Dict]:
    """ Load the most recent data provided by Parlamento """
    
    payload = requests.get(path)
    assert payload.status_code == 200

    return payload.json().get("ArrayOfPt_gov_ar_objectos_iniciativas_DetalhePesquisaIniciativasOut", {}).get("pt_gov_ar_objectos_iniciativas_DetalhePesquisaIniciativasOut", [])


def get_initiatives_followups(initiatives: List) -> pd.DataFrame:
  """ Create a many to many relationship between initiatives (the main initiative and the folow-up) """
  
  data_initiatives_followups = pd.DataFrame()
  for initiative in initiatives:
    initiative_id = initiative.get("iniId", "")
    initiative_nr = initiative.get("iniNr", "")
    
    initiatives_followups = initiative.get("iniciativasOriginadas", {}).get("pt_gov_ar_objectos_iniciativas_DadosGeraisOut", [])
    if isinstance(initiatives_followups, Dict):
      initiatives_followups = [initiatives_followups]

    for initiative_followup in initiatives_followups:
      initiative_followup_id = initiative_followup.get("id", "")
      initiative_followup_nr = initiative_followup.get("numero", "")
      initiative_followup_assunto = initiative_followup.get("assunto", "")
      initiative_followup_desc = initiative_followup.get("descTipo", "")
      
      data_initiatives_followups = data_initiatives_followups.append(
        {
          "iniciativaId": initiative_id,
          "iniciativaNr": initiative_nr,
          "iniciativasOriginadaId": initiative_followup_id,
          "iniciativasOriginadaNr": initiative_followup_nr,
          "iniciativasOriginadaAssunto": initiative_followup_assunto,
          "iniciativasOriginadaDesc": initiative_followup_desc
        },
        ignore_index = True
      )
      
  return data_initiatives_followups


def get_initiatives_petitions(initiatives: List) -> pd.DataFrame:
  """ Create a many to many relationship between initiatives and petitions """
  
  data_initiatives_petitions = pd.DataFrame()
  for initiative in initiatives:
    initiative_id = initiative.get("iniId", "")
    initiative_nr = initiative.get("iniNr", "")
    
    initiatives_petitions = initiative.get("peticoes", {}).get("pt_gov_ar_objectos_iniciativas_DadosGeraisOut", [])
    if isinstance(initiatives_petitions, Dict):
      initiatives_petitions = [initiatives_petitions]

    for initiative_petition in initiatives_petitions:
      initiative_petition_id = initiative_petition.get("id", "")
      initiative_petition_nr = initiative_petition.get("numero", "")
      initiative_petition_assunto = initiative_petition.get("assunto", "")
      
      data_initiatives_petitions = data_initiatives_petitions.append(
        {
          "iniciativaId": initiative_id,
          "iniciativaNr": initiative_nr,
          "iniciativasPeticaoId": initiative_petition_id,
          "iniciativasPeticaoNr": initiative_petition_nr,
          "iniciativasPeticaoAssunto": initiative_petition_assunto
        },
        ignore_index = True
      )
      
  return data_initiatives_petitions


if __name__ == "__main__":
    # load data from parlamento API
    initiatives = get_data(PATH)

    data_initiatives_followups = get_initiatives_followups(initiatives)

    data_initiatives_petitions = get_initiatives_petitions(initiatives)