from enum import Enum
from typing import Optional
from app.parliament.model.legislature import Legislatura
from pydantic import BaseModel


class SiglaGrupoParlamentar(str, Enum):
    BE = "BE"
    CDS_PP = "CDS-PP"
    CH = "CH"
    IL = "IL"
    L = "L"
    NI = "NI"
    PAN = "PAN"
    PCP = "PCP"
    PS = "PS"
    PSD = "PSD"


class NomeGrupoParlamentar(str, Enum):
    BE = "Bloco de Esquerda"
    CDS_PP = "Centro Democrático Social - Partido Popular"
    CH = "Chega"
    IL = "Iniciativa Liberal"
    L = "Livre"
    NI = "Não Inscrito"
    PAN = "Partido Animais e Natureza"
    PCP = "Partido Comunista Português"
    PS = "Partido Socialista"
    PSD = "Partido Social Democrata"


class CirculoEleitoral(str, Enum):
    ACORES = "AÇORES"
    AVEIRO = "AVEIRO"
    BEJA = "BEJA"
    BRAGA = "BRAGA"
    BRAGANCA = "BRAGANÇA"
    CASTELO_BRANCO = "CASTELO BRANCO"
    COIMBRA = "COIMBRA"
    EUROPA = "EUROPA"
    EVORA = "ÉVORA"
    FARO = "FARO"
    FORA_EUROPA = "FORA DA EUROPA"
    GUARDA = "GUARDA"
    LEIRIA = "LEIRIA"
    LISBOA = "LISBOA"
    MADEIRA = "MADEIRA"
    PORTALEGRE = "PORTALEGRE"
    PORTO = "PORTO"
    SANTAREM = "SANTARÉM"
    SETUBAL = "SETÚBAL"
    VIANA_DO_CASTELO = "VIANA DO CASTELO"
    VILA_REAL = "VILA REAL"
    VISEU = "VISEU"


class DescricaoCargoDeputado(str, Enum):
    PRESIDENTE = "PRESIDENTE"
    SECRETARIO = "SECRETÁRIO"
    VICE_PRESIDENTE = "VICE-PRESIDENTE"
    VICE_SECRETARIO = "VICE-SECRETÁRIO"


class DescricaoSituacaoDeputado(Enum):
    EFECTIVO = "EFECTIVO"
    EFECTIVO_DEFINITIVO = "EFECTIVO DEFINITIVO"
    EFECTIVO_TEMPORARIO = "EFECTIVO TEMPORÁRIO"
    IMPEDIDO = "IMPEDIDO"
    RENUNCIOU = "RENUNCIOU"
    SUSPENSO_ELEITO = "SUSPENSO ELEITO"
    SUSPENSO_NAO_ELEITO = "SUSPENSO NÃO ELEITO"
    SUPLENTE = "SUPLENTE"


class GrupoParlamentar(BaseModel):
    id: int
    sigla: str
    nome: str
    dataInicio: str
    dataFim: str


class CirculoEleitoralDeputado(BaseModel):
  id: int
  nome: CirculoEleitoral


class SituacaoDeputado(BaseModel):
    descricao: DescricaoSituacaoDeputado
    dataInicio: str
    dataFim: Optional[str]


class CargoDeputado(BaseModel):
    id: int
    descricao: DescricaoCargoDeputado
    dataInicio: str
    dataFim: Optional[str]


class Deputado(BaseModel):
    id: int
    cadastroId: int
    nomeParlamentar: str
    nomeCompleto: str
    grupoParlamentar: list[GrupoParlamentar]
    circuloEleitoral: CirculoEleitoralDeputado
    situacao: list[SituacaoDeputado]
    cargo: Optional[CargoDeputado]
    legislatura: Legislatura
