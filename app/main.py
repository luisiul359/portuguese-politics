import pandas as pd
import json

from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from datetime import date

from parliament.extract import extract_data, get_initiatives_votes, _get_author_deputy
from app.apis import votes, schemas



tags_metadata = [
    {"name": "Parliament", "description": "Information from Portuguese Parliament API."},
    {"name": "Elections", "description": "Information from Portuguese previous elections."},
]

app = FastAPI(openapi_tags=tags_metadata)


#data_initiatives = extract_data()
#if Path("data_initiatives_votes.pkl").is_file():
data_initiatives_votes = pd.read_pickle("data_initiatives_votes.pkl")
#data_initiatives_votes["iniciativa_evento_data"] = pd.to_datetime(data_initiatives_votes["iniciativa_evento_data"])
#data_initiatives_votes["iniciativa_autor_deputado"] = data_initiatives_votes.apply(_get_author_deputy, axis="columns")
#else:
#data_initiatives_votes = get_initiatives_votes(data_initiatives)
#pd.to_pickle(data_initiatives_votes, "data_initiatives_votes.pkl")


@app.get("/parliament/party-approvals", response_model=schemas.PartyApprovalsOut, tags=["Parliament"])
def get_party_approvals(type: Optional[str] = None, dt_ini: Optional[date] = None, dt_fin: Optional[date] = None):

    data_initiatives_votes_ = data_initiatives_votes
    
    if dt_ini:
        data_initiatives_votes_ = data_initiatives_votes_[data_initiatives_votes_["iniciativa_evento_data"].dt.date >= dt_ini]

    if dt_fin:
        data_initiatives_votes_ = data_initiatives_votes_[data_initiatives_votes_["iniciativa_evento_data"].dt.date <= dt_fin]

    if type:
        data_initiatives_votes_ = data_initiatives_votes_[data_initiatives_votes_["iniciativa_tipo"] == type]
    
    party_approvals = votes.get_party_approvals(data_initiatives_votes_).to_json(orient="index")
    
    # transform to the expected schema
    approvals = []
    for autor, value in json.loads(party_approvals).items():

        data = {
            "id": autor.lower().replace(" ", "-").replace("cristina-rodrigues", "cr").replace("joacine-katar-moreira", "jkm"),
            "nome": autor,
            "total_iniciativas": value["total_iniciativas"],
            "total_iniciativas_aprovadas": value["total_iniciativas_aprovadas"],
        }

        data["aprovacoes"] = {k.replace("iniciativa_votacao_", ""): v for k, v in value.items() if k.startswith("iniciativa_votacao_")}

        approvals.append(data)

    return {'autores': approvals}


@app.get("/parliament/party-correlations", response_model=schemas.PartyCorrelationsOut, tags=["Parliament"])
def get_party_correlations(dt_ini: Optional[date] = None, dt_fin: Optional[date] = None):
    
    data_initiatives_votes_ = data_initiatives_votes
    
    if dt_ini:
        data_initiatives_votes_ = data_initiatives_votes_[data_initiatives_votes_["iniciativa_evento_data"].dt.date >= dt_ini]

    if dt_fin:
        data_initiatives_votes_ = data_initiatives_votes_[data_initiatives_votes_["iniciativa_evento_data"].dt.date <= dt_fin]

    party_corr = votes.get_party_correlations(data_initiatives_votes_).to_json(orient="index")

    # transform to the expected schema
    res = []
    for party, corr in json.loads(party_corr).items():
        res.append({
            "nome": party.replace("iniciativa_votacao_", ""),
            "correlacoes": {k.replace("iniciativa_votacao_", ""): v for k, v in corr.items()}
        })

    return {"partido": res}


@app.get("/parliament/initiatives", tags=["Parliament"])
def get_initiatives(name_filter: Optional[str] = None, party: Optional[str] = None, deputy: Optional[str] = None,  dt_ini: Optional[date] = None, dt_fin: Optional[date] = None, limit: Optional[int] = 20, offset: Optional[int] = 0):
    
    data_initiatives_votes_ = data_initiatives_votes
    
    if dt_ini:
        data_initiatives_votes_ = data_initiatives_votes_[data_initiatives_votes_["iniciativa_evento_data"].dt.date >= dt_ini]

    if dt_fin:
        data_initiatives_votes_ = data_initiatives_votes_[data_initiatives_votes_["iniciativa_evento_data"].dt.date <= dt_fin]

    if name_filter:
        data_initiatives_votes_ = data_initiatives_votes_[data_initiatives_votes_["iniciativa_titulo"].str.lower().str.contains(name_filter.lower())]

    if party:
        data_initiatives_votes_ = data_initiatives_votes_[data_initiatives_votes_["iniciativa_autor"].str.lower() == party.lower()]

    if deputy:
        data_initiatives_votes_ = data_initiatives_votes_[data_initiatives_votes_["iniciativa_autor_deputado"].str.lower().str.contains(deputy.lower())]

    initiatives = votes.get_initiatives(data_initiatives_votes_).sort_values("iniciativa_data").head(limit+offset).tail(limit).to_json(orient="index")

    # transform to the expected schema
    res = []
    for _, initiative in json.loads(initiatives).items():
        res.append(initiative)

    return {"initiativas": res}
