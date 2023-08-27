from enum import Enum
from typing import List, Dict, Union, Optional
from datetime import date

from pydantic import BaseModel, AnyHttpUrl, EmailStr, Field


class PartyApprovals(BaseModel):
    id: str = Field(description="name of student")
    nome: str
    total_iniciativas: int
    total_iniciativas_aprovadas: float
    aprovacoes: Dict[str, float]


class PartyApprovalsOut(BaseModel):
    autores: List[PartyApprovals]


class PartyCorrelations(BaseModel):
    nome: str
    correlacoes: Dict[str, float]


class PartyCorrelationsOut(BaseModel):
    partido: List[PartyCorrelations]


class EventPhase(str, Enum):
    GENERALIDADE = "Votação na generalidade"
    ESPECIALIDADE = "Votação na especialidade"
    ALL = "Todos"
    FINAL = "Votação final global"


class Legislature(str, Enum):
    XIV = "XIV"
    XV = "XV"


class Initiative(BaseModel):
    iniciativa_evento_fase: str
    iniciativa_titulo: str
    iniciativa_url: AnyHttpUrl
    iniciativa_url_res: AnyHttpUrl
    iniciativa_autor: str
    iniciativa_autor_deputados_nomes: str
    iniciativa_evento_data: date
    iniciativa_tipo: str
    iniciativa_votacao_res: str


class InitiativesOut(BaseModel):
    initiativas: List[Initiative]


class Party(BaseModel):
    name: str
    description: str
    description_source: AnyHttpUrl
    email: Optional[EmailStr]
    facebook: Optional[AnyHttpUrl]
    instagram: Optional[AnyHttpUrl]
    logo: Optional[AnyHttpUrl]
    twitter: Optional[AnyHttpUrl]
    website: Optional[AnyHttpUrl]
    manifesto: Optional[Union[List[AnyHttpUrl],AnyHttpUrl]]


class PartiesOut(BaseModel):
    parties: Dict[str, Party]


class CandidateType(str, Enum):
    MAIN = "main"
    SECUNDARY = "secundary"


class Candidate(BaseModel):
    party: str
    district: str
    name: str
    position: int
    type: CandidateType
    biography: Optional[str]
    biography_source: Optional[AnyHttpUrl]
    link_parlamento: Optional[AnyHttpUrl]
    photo: Optional[AnyHttpUrl]
    photo_source: Optional[Union[str, AnyHttpUrl]]


class CandidatesOut(BaseModel):
    candidates: List[Candidate]
