from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class TipoIniciativa(str, Enum):
    PROJECTO_LEI = "Projecto de Lei"
    PROPOSTA_LEI = "Proposta de Lei"
    # Existem mais tipos de iniciativas, mas para já foram definidos estes para o objectivo da pagina de Iniciativa

class OrigemAutorIniciativa(str, Enum):
    CIDADAOS = "Grupo Cidadãos"
    GOVERNO = "Governo"
    GRUPO_PARLAMENTAR = "Grupo Parlamentar"

class EventoIniciativa(str, Enum):
    ENTRADA = "Entrada"

class PublicacaoIniciativa(BaseModel):
    id: int
    type: str
    date: str
    pages: str
    source: str

class IniciativaAutorDeputado(BaseModel):
    id: int
    nome: str
    sigla_grupo_parlamentar: str

class IniciativaAutor(BaseModel):
    origem: OrigemAutorIniciativa
    deputados: Optional[List[IniciativaAutorDeputado]]
    # grupos_parlamentares: Optional[List[str]]

class AnexoFaseIniciativa(BaseModel):
    nome: str
    documento_url: str

class FaseIniciativa(BaseModel):
  id: int
  evento: str #EventoIniciativa
  nota_evento: Optional[str]
  data: str
  fase_publicacao: Optional[PublicacaoIniciativa]
  anexo: Optional[AnexoFaseIniciativa]

class AnexoIniciativa(BaseModel):
    nome: str
    ficheiro_url: str

class Iniciativa(BaseModel):
    id: int

class ProjectoPropostaLei(Iniciativa):
    numero: int
    titulo: str
    tipo: TipoIniciativa
    autor: IniciativaAutor
    fases: List[FaseIniciativa]
    documento_url: str
    anexo: AnexoIniciativa
    legislatura: str
