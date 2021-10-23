import requests
import pandas as pd

from typing import Dict, List, Union
from copy import deepcopy
from collections import defaultdict


# data updated daily
PATH = "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d6c6a6157463061585a68637939595356596c4d6a424d5a57647063327868644856795953394a626d6c6a6157463061585a686331684a566c3971633239754c6e523464413d3d&fich=IniciativasXIV_json.txt&Inline=true"


def get_data(path: str) -> List[Dict]:
    """ Load the most recent data provided by Parlamento """
    
    payload = requests.get(path)
    assert payload.status_code == 200

    return payload.json().get("ArrayOfPt_gov_ar_objectos_iniciativas_DetalhePesquisaIniciativasOut", {}).get("pt_gov_ar_objectos_iniciativas_DetalhePesquisaIniciativasOut", [])


def get_initiatives_followups(raw_initiatives: List) -> pd.DataFrame:
  """ Create a many to many relationship between initiatives (the main initiative and the folow-up) """
  
  data_initiatives_followups = pd.DataFrame()
  for initiative in raw_initiatives:
    # save all the initiative information to be stored
    info_to_store = {}

    info_to_store["iniciativa_id"] = initiative.get("iniId", "")
    info_to_store["iniciativa_nr"] = initiative.get("iniNr", "")
    
    initiatives_followups = initiative.get("iniciativasOriginadas", {}).get("pt_gov_ar_objectos_iniciativas_DadosGeraisOut", [])
    if isinstance(initiatives_followups, Dict):
      initiatives_followups = [initiatives_followups]

    for initiative_followup in initiatives_followups:
      info_to_store_details = deepcopy(info_to_store)

      info_to_store_details["iniciativa_followup_id"] = initiative_followup.get("id", "")
      info_to_store_details["iniciativa_followup_nr"] = initiative_followup.get("numero", "")
      info_to_store_details["iniciativa_followup_assunto"] = initiative_followup.get("assunto", "")
      info_to_store_details["iniciativa_followup_desc"] = initiative_followup.get("descTipo", "")
      
      data_initiatives_followups = data_initiatives_followups.append(
        **info_to_store_details,
        ignore_index = True
      )
      
  return data_initiatives_followups


def get_initiatives_petitions(raw_initiatives: List) -> pd.DataFrame:
  """ Create a many to many relationship between initiatives and petitions """
  
  data_initiatives_petitions = pd.DataFrame()
  for initiative in raw_initiatives:
    # save all the initiative information to be stored
    info_to_store = {}

    info_to_store["iniciativa_id"] = initiative.get("iniId", "")
    info_to_store["iniciativa_nr"] = initiative.get("iniNr", "")
    
    initiatives_petitions = initiative.get("peticoes", {}).get("pt_gov_ar_objectos_iniciativas_DadosGeraisOut", [])
    if isinstance(initiatives_petitions, Dict):
      initiatives_petitions = [initiatives_petitions]

    for initiative_petition in initiatives_petitions:
      info_to_store_details = deepcopy(info_to_store)

      info_to_store_details["iniciativa_petition_id"] = initiative_petition.get("id", "")
      info_to_store_details["iniciativa_petition_nr"] = initiative_petition.get("numero", "")
      info_to_store_details["iniciativa_petition_assunto"] = initiative_petition.get("assunto", "")
      
      data_initiatives_petitions = data_initiatives_petitions.append(
        **info_to_store_details,
        ignore_index = True
      )
      
  return data_initiatives_petitions


def get_initiatives(raw_initiatives: List) -> pd.DataFrame:
  """
  Parse parlamento API and return the main information of each initiative.

  Will return a raw version, i.e., a wide range of information that needs to be further parsed.
  """

  def to_list(x: Union[Dict, List]) -> List:
    return x if isinstance(x, list) else [x]
  
  data_initiatives = pd.DataFrame()
  for initiative in raw_initiatives:
    # save all the initiative information to be stored
    info_to_store = {}

    # initiative
    info_to_store["iniciativa_id"] = initiative.get("iniId", "")
    info_to_store["iniciativa_nr"] = initiative.get("iniNr", "")
    info_to_store["iniciativa_tipo"] = initiative.get("iniDescTipo", "")
    info_to_store["iniciativa_titulo"] = initiative.get("iniTitulo", "")
    info_to_store["iniciativa_url"] = initiative.get("iniLinkTexto", "")
    info_to_store["iniciativa_obs"] = initiative.get("iniObs", "")
    info_to_store["iniciativa_texto_subst"] = initiative.get("iniTextoSubstCampo", "")
    
    # iniAutorGruposParlamentares
    info_to_store["iniciativa_autor_grupos_parlamentares"] = initiative.get("iniAutorGruposParlamentares", {}).get("pt_gov_ar_objectos_AutoresGruposParlamentaresOut", {}).get("GP", "")
    
    # iniAutorOutros
    info_to_store["iniciativa_autor_outros_nome"] = initiative.get("iniAutorOutros", {}).get("nome", "")
    info_to_store["iniciativa_autor_outros_autor_comissao"] = initiative.get("iniAutorOutros", {}).get("iniAutorComissao", "")
    
    # iniAutorDeputados
    autor_deputados = to_list(initiative.get("iniAutorDeputados", {}).get("pt_gov_ar_objectos_iniciativas_AutoresDeputadosOut", []))
    info_to_store["iniciativa_autor_deputados_nomes"] = "|".join([x.get("nome", "") for x in autor_deputados])
    info_to_store["iniciativa_autor_deputados_GPs"] = "|".join([x.get("GP", "") for x in autor_deputados])
    
    # iniAnexos
    anexos = to_list(initiative.get("iniAnexos", {}).get("pt_gov_ar_objectos_iniciativas_AnexosOut", []))
    info_to_store["iniciativa_anexos_nomes"] = "|".join([x.get("anexoNome", "") for x in anexos])
    info_to_store["iniciativa_anexos_URLs"] = "|".join([x.get("anexoFich", "") for x in anexos])
    
    # iniciativasOrigem
    origem = initiative.get("iniciativasOrigem", {}).get("pt_gov_ar_objectos_iniciativas_DadosGeraisOut", {})
    info_to_store["iniciativa_origem_id"] = origem.get("id", "")
    info_to_store["iniciativa_origem_nr"] = origem.get("numero", "")
    info_to_store["iniciativa_origem_assunto"] = origem.get("assunto", "")
    info_to_store["iniciativa_origem_desc"] = origem.get("descTipo", "")
    
    # iniEventos
    #
    # each initiative can go through different stages / events until it is closed. 
    # We will collect different information based on the stage / event
    events = to_list(initiative.get("iniEventos", {}).get("pt_gov_ar_objectos_iniciativas_EventosOut", []))
    for event in events:
      info_to_store_details = deepcopy(info_to_store)

      info_to_store_details["iniciativa_evento_fase"] = event.get("fase", "")
      info_to_store_details["iniciativa_evento_data"] = event.get("dataFase", "")
      info_to_store_details["iniciativa_evento_id"] = event.get("evtId", "")
      
      publicacao_detalhe = event.get("publicacaoFase", {}).get("pt_gov_ar_objectos_PublicacoesOut", {})
      info_to_store_details["iniciativa_publicacao_Tipo"] = publicacao_detalhe.get("pubTipo", "")
      info_to_store_details["iniciativa_publicacao_URL"] = publicacao_detalhe.get("URLDiario", "")
      info_to_store_details["iniciativa_publicacao_Obs"] = publicacao_detalhe.get("obs", "")
      info_to_store_details["iniciativa_publicacao_Pags"] = "|".join(publicacao_detalhe.get("pag", []))
      
      iniciativas_conjuntas = to_list(event.get("iniciativasConjuntas", {}).get("pt_gov_ar_objectos_iniciativas_DiscussaoConjuntaOut", []))
      info_to_store_details["iniciativa_iniciativas_conjuntas_tipo"] = "|".join([x.get("descTipo", "") for x in iniciativas_conjuntas])
      info_to_store_details["iniciativa_iniciativas_conjuntas_titulo"] = "|".join([x.get("titulo", "") for x in iniciativas_conjuntas])
      
      oradores = to_list(event.get("intervencoesdebates", {}).get("pt_gov_ar_objectos_IntervencoesOut", {}).get("oradores", {}).get("pt_gov_ar_objectos_peticoes_OradoresOut", []))
      info_to_store_details["iniciativa_oradores_deputados_nomes"] = "|".join([x.get("deputados", {}).get("nome", "") for x in oradores])
      info_to_store_details["iniciativa_oradores_deputados_gp"] = "|".join([x.get("deputados", {}).get("GP", "") for x in oradores])
      info_to_store_details["iniciativa_oradores_governo_nomes"] = "|".join([x.get("membrosGoverno", {}).get("nome", "") for x in oradores])
      info_to_store_details["iniciativa_oradores_governo_cargo"] = "|".join([x.get("membrosGoverno", {}).get("cargo", "") for x in oradores])
      # government and deputies videos are mixed
      info_to_store_details["iniciativa_oradores_videos"] = "|".join([x.get("linkVideo", {}).get("pt_gov_ar_objectos_peticoes_LinksVideos", {}).get("link", "") for x in oradores])
      
      votacao = event.get("votacao", {}).get("pt_gov_ar_objectos_VotacaoOut", {})
      if (isinstance(votacao, list)):
        # in some situations the same initiative in a certain event can have several votes
        # for now we will consider only the first one
        votacao = votacao[0]
      info_to_store_details["iniciativa_votacao_res"] = votacao.get("resultado", "")
      info_to_store_details["iniciativa_votacao_desc"] = votacao.get("descricao", "")
      info_to_store_details["iniciativa_votacao_tipo_reuniao"] = votacao.get("tipoReuniao", "")
      info_to_store_details["iniciativa_votacao_unanime"] = votacao.get("unanime", "")
      info_to_store_details["iniciativa_votacao_detalhe"] = votacao.get("detalhe", "")
      info_to_store_details["iniciativa_votacao_ausencias"] = votacao.get("ausencias", {}).get("string", "")
      
      anexos = to_list(event.get("anexosFase", {}).get("pt_gov_ar_objectos_iniciativas_AnexosOut", []))
      info_to_store_details["iniciativa_anexo_nome"] = "|".join([x.get("anexoNome", "") for x in anexos])
      info_to_store_details["iniciativa_anexo_url"] = "|".join([x.get("anexoFich", "") for x in anexos])
      
      comissao = event.get("comissao", {}).get("pt_gov_ar_objectos_iniciativas_ComissoesIniOut", {})
      info_to_store_details["iniciativa_comissao_nome"] = comissao.get("nome", "")
      info_to_store_details["iniciativa_comissao_competente"] = comissao.get("competente", "")
      info_to_store_details["iniciativa_comissao_observacao"] = comissao.get("observacao," "")
      info_to_store_details["iniciativa_comissao_data_relatorio"] = comissao.get("dataRelatorio", "")
      info_to_store_details["iniciativa_comissao_pedidos_parecer"] = "|".join([_ for _ in to_list(comissao.get("pedidosParecer", {}).get("string", [])) if isinstance(_, str)])
      info_to_store_details["iniciativa_comissao_pareceres_recebidos"] = "|".join([_ for _ in to_list(comissao.get("pareceresRecebidos", {}).get("string", [])) if isinstance(_, str)])
      
      documentos = to_list(comissao.get("documentos", {}).get("pt_gov_ar_objectos_DocsOut", []))
      info_to_store_details["iniciativa_comissao_documentos_Titulos"] = "|".join([x.get("tituloDocumento", "") for x in documentos])
      info_to_store_details["iniciativa_comissao_documentos_Tipos"] = "|".join([x.get("tipoDocumento", "") for x in documentos])
      info_to_store_details["iniciativa_comissao_documentos_URLs"] = "|".join([x.get("URL", "") for x in documentos])
      
      publicacaoDetalhe = comissao.get("publicacao", {}).get("pt_gov_ar_objectos_PublicacoesOut", {})
      info_to_store_details["iniciativa_comissao_publicacao_Tipo"] = publicacaoDetalhe.get("pubTipo", "")
      info_to_store_details["iniciativa_comissao_publicacao_URL"] = publicacaoDetalhe.get("URLDiario", "")
      info_to_store_details["iniciativa_comissao_publicacao_Obs"] = publicacaoDetalhe.get("obs", "")
      info_to_store_details["iniciativa_comissao_publicacao_Pags"] = "|".join(publicacaoDetalhe.get("pag", ""))
      
      info_to_store_details["iniciativa_comissao_votacao_Res"] = comissao.get("votacao", {}).get("resultado", "")
      info_to_store_details["iniciativa_comissao_votacao_Desc"] = comissao.get("votacao", {}).get("descricao", "")
      info_to_store_details["iniciativa_comissao_votacao_Data"] = comissao.get("votacao", {}).get("data", "")
      info_to_store_details["iniciativa_comissao_votacao_Unanime"] = comissao.get("votacao", {}).get("unanime", "")
      
      # TODO: in event: teor, sumario, publicacao
      # TODO: in comissao:  audicoes, audiencias, distribuicaoSubcomissao, motivoNaoParecer, pareceresRecebidos, pedidosParecer, relatores
      
      data_initiatives = data_initiatives.append(
        **info_to_store_details,
        ignore_index = True
      )
      
  return data_initiatives


def _split_vote_result(vote: str) -> Dict[str, list]:
  """
  Extract vote result from poll

  Return a dicionary with a list of parties for each poll option
  """

  if not vote: return {}

  # clean vote information
  vote = vote.lower().replace(" ", "").replace("<br>", "").replace("</i>", "").replace("<i>", "")
  vote = vote.replace("afavor:", ",afavor,").replace("contra:", ",contra,").replace("ausência:", ",ausência,").replace("abstenção:", ",abstenção,")
  vote = vote.split(",")
  
  result = defaultdict(list)

  # the first entry will always be empty
  current_option = vote[1]
  for party in vote[2:]:

    if party in "afavor,contra,ausência,abstenção":
      current_option = party
    else:
      result[current_option].append(party)

  return result


def get_initiatives_votes(initiatives: pd.DataFrame) -> pd.DataFrame:
  """
  Collect vote information from each initiative.
  """

  # we only need this initiative information regaring votes
  columns_to_keep = ["iniciativa_id","iniciativa_nr","iniciativa_tipo","iniciativa_titulo","iniciativa_evento_fase","iniciativa_evento_data","iniciativa_url","iniciativa_obs","iniciativa_texto_subst","iniciativa_autor_grupos_parlamentares","iniciativa_autor_outros_nome","iniciativa_autor_outros_autor_comissao","iniciativa_autor_deputados_nomes","iniciativa_autor_deputados_GPs"]

  data_initiatives = pd.DataFrame()
  for _, row in initiatives[columns_to_keep].iterrows():
    column_to_store = row.copy()
    
    vote_results = _split_vote_result(row["iniciativa_votacao_detalhe"])

    # create a new column for each party with the respective vote
    for vote, parties in vote_results.items():
      for party in parties:
        column_to_store[f"iniciativa_votacao_{party}"] = vote
      
    data_initiatives = data_initiatives.append(column_to_store)

  return data_initiatives


if __name__ == "__main__":
    # load data from parlamento API
    raw_initiatives = get_data(PATH)

    data_initiatives_followups = get_initiatives_followups(raw_initiatives)

    data_initiatives_petitions = get_initiatives_petitions(raw_initiatives)

    data_initiatives = get_initiatives(raw_initiatives)

    data_initiatives_votes = get_initiatives_votes(data_initiatives)
