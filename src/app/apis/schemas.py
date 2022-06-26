from typing import List, Dict
from pydantic import BaseModel


class PartyApprovals(BaseModel):
    id: str
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