import pandas as pd
import json

from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from datetime import date

from parliament.extract import extract_data, get_initiatives_votes
from app.apis import votes, schemas


app = FastAPI()


#data_initiatives = extract_data()
#if Path("data_initiatives_votes.pkl").is_file():
data_initiatives_votes = pd.read_pickle("data_initiatives_votes.pkl")
data_initiatives_votes["iniciativa_evento_data"] = pd.to_datetime(data_initiatives_votes["iniciativa_evento_data"])
#else:
#data_initiatives_votes = get_initiatives_votes(data_initiatives)
#pd.to_pickle(data_initiatives_votes, "data_initiatives_votes.pkl")


@app.get("/party-approvals", response_model=schemas.PartyApprovalsOut)
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


@app.get("/party-correlations", response_model=schemas.PartyCorrelationsOut)
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