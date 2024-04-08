import aiohttp
import json

from typing import Any

from .common import PARLIAMENT_INITIATIVES_XV
from .initiative_model import AnexoFaseIniciativa, AnexoIniciativa, FaseIniciativa, Iniciativa, IniciativaAutor, IniciativaAutorDeputado, OrigemAutorIniciativa, ProjectoPropostaLei, TipoIniciativa
from ..parliament_model import Legislature


async def get_initiative(id: int, legislature: Legislature) -> Iniciativa:
    initiative = await find_initiative(id, legislature)
    return build_initiative_based_on_type(initiative)


async def find_initiative(id: int, legislature: Legislature) -> json:
    data = await get_parliament_data()
    initiatives = data["ArrayOfPt_gov_ar_objectos_iniciativas_DetalhePesquisaIniciativasOut"]["pt_gov_ar_objectos_iniciativas_DetalhePesquisaIniciativasOut"]
    filtered_initiatives = [initiative for initiative in initiatives if is_valid_initiative(initiative, id, legislature)]

    if (len(filtered_initiatives) > 1):
        raise ValueError(f"We have found {len(filtered_initiatives)} with this {id}")
    return filtered_initiatives[0]


def is_valid_initiative(initiative: json, id: int, legislature: Legislature):
    return int(initiative["iniId"]) == id and initiative["iniLeg"] == str(legislature.value) and legislature == Legislature.XV


async def get_parliament_data() -> json:
    async with aiohttp.ClientSession() as client:    
        async with client.get(PARLIAMENT_INITIATIVES_XV) as response:
            if response.status != 200:
                raise ValueError(f"{response.status} - /parlamento.pt is not available")
            return await response.json()
  

def build_initiative_based_on_type(initiative: json) -> Iniciativa:
    if initiative["iniTipo"] == "J" or initiative["iniTipo"] == "P":
        return build_projecto_or_proposta_de_lei(initiative)
    raise NotImplementedError(f"Initiative {initiative['iniDescTipo']} not supported. Only Propostas de Lei e Projectos de Lei are implemented")
    

def build_projecto_or_proposta_de_lei(initiative: json) -> ProjectoPropostaLei:    
    attachment = initiative["iniAnexos"]["pt_gov_ar_objectos_iniciativas_AnexosOut"]

    return ProjectoPropostaLei(
        id=int(initiative["iniId"]),
        numero=int(initiative["iniNr"]),
        titulo=initiative["iniTitulo"],
        tipo=map_initiative_type(initiative["iniTipo"]),
        autor=IniciativaAutor(
            origem=map_author_origin(initiative["iniAutorOutros"]["sigla"]),
            deputados=map_initiative_deputies(initiative)
        ),
        fases=map_stages(initiative["iniEventos"]["pt_gov_ar_objectos_iniciativas_EventosOut"]),
        documento_url=initiative["iniLinkTexto"],
        anexo=AnexoIniciativa(
            nome=attachment["anexoNome"],
            ficheiro_url=attachment["anexoFich"]
        ),
        legislatura=initiative["iniLeg"]
    )


def map_initiative_deputies(initiative: Iniciativa) -> IniciativaAutorDeputado:
    author_deputies = initiative["iniAutorDeputados"]["pt_gov_ar_objectos_iniciativas_AutoresDeputadosOut"]

    return [IniciativaAutorDeputado(
        id=dep["idCadastro"],
        nome=dep["nome"],
        sigla_grupo_parlamentar=dep["GP"]
    ) for dep in author_deputies]


def map_author_origin(origin_acronym: str) -> OrigemAutorIniciativa:
    if origin_acronym == "G":
        return OrigemAutorIniciativa.GRUPO_PARLAMENTAR
    elif origin_acronym == "Z":
        return OrigemAutorIniciativa.CIDADAOS
    else:
        return OrigemAutorIniciativa.GOVERNO


def map_initiative_type(ini_type: str):
    if ini_type == "J":
        return TipoIniciativa.PROJECTO_LEI
    if ini_type == "P":
        return TipoIniciativa.PROPOSTA_LEI
    else:
        raise ValueError(f"Initiative type {ini_type} is not implemented.")


def map_stages(initiative_stages: [Any]):
    return [FaseIniciativa(
        id=stage["oevId"],
        data=stage["dataFase"],
        evento=stage["fase"],
        nota_evento=stage["obsFase"] if "obsFase" in stage else None,
        fase_publicacao=None,
        anexo=AnexoFaseIniciativa(
            nome=stage["anexosFase"]["pt_gov_ar_objectos_iniciativas_AnexosOut"]["anexoNome"],
            documento_url=stage["anexosFase"]["pt_gov_ar_objectos_iniciativas_AnexosOut"]["anexoFich"]
        ) if "anexosFase" in stage else None 
    ) for stage in initiative_stages]
