from typing import Optional
import pytest
from httpx import AsyncClient

from src.app.main import parliament_app


base_url = "http://test"


@pytest.mark.anyio
async def test_request_agenda_endpoint_with_success():
    async with AsyncClient(app=parliament_app, base_url=base_url) as ac:
        response = await ac.get("/agenda")
    
    assert response.status_code == 200

    response = response.json()
    assert isinstance(response, list)

    if len(response) > 0:
        event = response[0]
        assert "id" in event
        assert isinstance(event["id"], int)
        
        assert "titulo" in event
        assert isinstance(event["titulo"], str)
        
        assert "subTitulo" in event
        assert isinstance(event["subTitulo"], Optional[str])
        
        assert "sessao" in event
        sessao = event["sessao"]
        assert "descricao" in sessao
        assert "id" in sessao
        assert isinstance(sessao["descricao"], str)
        assert isinstance(sessao["id"], int)
        
        assert "tema" in event
        tema = event["tema"]
        assert "descricao" in tema
        assert "id" in tema
        assert isinstance(tema["descricao"], str)
        assert isinstance(tema["id"], int)

        assert "ordem" in event
        assert isinstance(event["ordem"], int)

        assert "grupoParlamentarId" in event
        assert isinstance(event["grupoParlamentarId"], int)
        
        assert "dataInicio" in event
        assert isinstance(event["dataInicio"], str)

        assert "horaInicio" in event
        assert isinstance(event["horaInicio"], Optional[str])
        
        assert "dataFim" in event
        assert isinstance(event["dataFim"], str)

        assert "horaFim" in event
        assert isinstance(event["horaFim"], Optional[str])
        
        assert "textoHtml" in event
        assert isinstance(event["textoHtml"], str)

        assert "local" in event
        assert isinstance(event["local"], Optional[str])

        assert "orgao" in event
        assert isinstance(event["orgao"], Optional[str])
        
        assert "numeroReuniao" in event
        assert isinstance(event["numeroReuniao"], Optional[int])
        
        assert "sessaoLegislativa" in event
        assert isinstance(event["sessaoLegislativa"], Optional[int])
        
        assert "ocorreAposSessaoPlenaria" in event
        assert isinstance(event["ocorreAposSessaoPlenaria"], bool)
        
        assert "anexosComissaoPermanente" in event
        anexos_cm = event["anexosComissaoPermanente"]
        assert isinstance(event["anexosComissaoPermanente"], Optional[list])
        if anexos_cm is not None:
            anexo = anexos_cm[0]
            assert "id" in anexo
            assert isinstance(anexo["id"], int)
            assert "tipoDocumento" in anexo
            assert isinstance(anexo["tipoDocumento"], str)
            assert "titulo" in anexo
            assert isinstance(anexo["titulo"], str)
            assert "link" in anexo
            assert isinstance(anexo["link"], str)

        assert "anexosPlenario" in event
        anexos_p = event["anexosPlenario"]
        assert isinstance(event["anexosPlenario"], Optional[list])
        if anexos_p is not None:
            anexo = anexos_p[0]
            assert "id" in anexo
            assert isinstance(anexo["id"], int)
            assert "tipoDocumento" in anexo
            assert isinstance(anexo["tipoDocumento"], str)
            assert "titulo" in anexo
            assert isinstance(anexo["titulo"], str)
            assert "link" in anexo
            assert isinstance(anexo["link"], str)
        
        assert "link" in event
        assert isinstance(event["link"], Optional[str])
        
        assert "duracaoDiaInteiro" in event
        assert isinstance(event["duracaoDiaInteiro"], bool)
        
        assert "legislatura" in event
        assert isinstance(event["legislatura"], Optional[str])
    else:
        assert response == []
