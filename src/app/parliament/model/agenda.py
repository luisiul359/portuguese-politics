from enum import Enum
from typing import Optional
from parliament.model.legislature import Legislatura
from pydantic import BaseModel


class SessaoAgendaDescricao(str, Enum):
    COMISSAO_PERMANENTE = "Comissão Permanente"
    AGENDA_PAR = "Agenda do Presidente da Assembleia da República"
    SUBCOMISSAO = "Subcomissão"
    PLENARIO = "Plenário"
    GRUPO_TRABALHO_AR = "Grupo de Trabalho AR"
    CONFERENCIA_PCP = "Conferência dos Presidentes das Comissões Parlamentares"
    COMISSOES_PARLAMENTAR = "Comissões Parlamentares"
    CONFERENCIA_LIDERES = "Conferência de Líderes"
    CONSELHO_ADMINISTRACAO = "Conselho de Administração"
    GRUPO_TRABALHO = "Grupo de Trabalho"
    COMISSAO_PERMANENTE_AGENDAMENTOS_FUTUROS = "Comissão Permanente - Agendamentos Futuros"
    COMISSAO_PERMANENTE_AGENDA_DIA = "Comissão Permanente - Agenda do Dia"
    EVENTOS = "Eventos"
    PLENARIO_AGENDAMENTOS_FUTUROS = "Plenário - Agendamentos Futuros"
    PLENARIO_AGENDA_DIA = "Plenário - Agenda do Dia"
    AGENDA_VICE_PAR = "Agenda da Vice-Presidência da Assembleia da República"
    OUTRAS_INFORMACOES = "Outras Informações"
    PLENARIO_AGENDA_DIA_CARREGAMENTO_MANUAL = "Plenário - Agenda do Dia (carregamento manual)"
    RELACOES_INTERNACIONAIS = "Relações Internacionais"
    VISITAS_PALACIO_SAO_BENTO = "Visitas ao Palácio de S. Bento"
    ASSISTENCIAS_AO_PLENARIO = "Assistências ao Plenário"
    GRUPOS_PARLAMENTARES = "Grupos Parlamentares / Partidos / DURP / Ninsc"
    RESUMO_CALENDARIZACAO = "Resumo da Calendarização"
    GRELHAS_DE_TEMPOS = "Grelhas de Tempos"


class SessaoAgenda(BaseModel):
    id: int
    descricao: SessaoAgendaDescricao


class TemaAgendaDescricao(str, Enum):
    CONFERENCIA_PRESIDENTES_COMISSOES_PARLAMENTARES = "Conferência dos Presidentes das Comissões Parlamentares"
    COMISSOES_PARLAMENTARES = "Comissões Parlamentares"
    COMISSAO_PERMANENTE = "Comissão Permanente"
    CONSELHO_ADMINISTRACAO = "Conselho de Administração"
    CONFERENCIA_LIDERES = "Conferência de Líderes"
    GRUPO_TRABALHO_AR = "Grupo de Trabalho AR"
    PLENARIO = "Plenário"
    AGENDA_PRESIDENTE_AR = "Agenda do Presidente da Assembleia da República"
    CALENDARIZACAO_TRABALHOS_PARLAMENTARES = "CALENDARIZAÇÃO DOS TRABALHOS PARLAMENTARES"
    PRESIDENCIA_AR = "PRESIDÊNCIA DA ASSEMBLEIA DA REPÚBLICA"
    ACTIVIDADES_PARLAMENTARES_EXTERNAS = "ACTIVIDADES PARLAMENTARES EXTERNAS"
    OUTRAS_ACTIVIDADES = "OUTRAS ACTIVIDADES"
    RESUMO_CALENDARIZACAO = "Resumo da Calendarização"
    GRUPOS_PARLAMENTARES = "Grupos Parlamentares / Partidos / DURP / Ninsc"
    VISITAS_PALACIO_SAO_BENTO = "Visitas ao Palácio de S. Bento"
    ASSISTENCIA_AO_PLENARIO = "Assistências ao Plenário"


class TemaAgenda(BaseModel):
    id: int
    descricao: TemaAgendaDescricao


class AnexosAgenda(BaseModel):
    id: int
    tipoDocumento: str
    titulo: str
    link: str


class EventoAgenda(BaseModel):
    id: int
    titulo: str
    subTitulo: Optional[str]
    sessao: SessaoAgenda
    tema: TemaAgenda
    ordem: int
    grupoParlamentarId: int
    dataInicio: str
    horaInicio: Optional[str]
    dataFim: str
    horaFim: Optional[str]
    textoHtml: str
    local: Optional[str]
    orgao: Optional[str]
    numeroReuniao: Optional[int]
    sessaoLegislativa: Optional[int]
    ocorreAposSessaoPlenaria: bool
    anexosComissaoPermanente: Optional[list[AnexosAgenda]]
    anexosPlenario: Optional[list[AnexosAgenda]]
    link: Optional[str]
    duracaoDiaInteiro: bool
    legislatura: Legislatura
