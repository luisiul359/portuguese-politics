import pandas as pd
import json

from pathlib import Path
from typing import Optional
from fastapi import FastAPI

from parliament.extract import extract_data, get_initiatives_votes
from app.apis import votes


app = FastAPI()


data_initiatives = extract_data()
#if Path("data_initiatives_votes.pkl").is_file():
#    data_initiatives_votes = pd.read_pickle("data_initiatives_votes.pkl")
#else:
data_initiatives_votes = get_initiatives_votes(data_initiatives)
#    pd.to_pickle(data_initiatives_votes, "data_initiatives_votes.pkl")


@app.get("/party-approvals")
def get_party_approvals(type: Optional[str] = None, dt_ini: Optional[str] = None, dt_fin: Optional[str] = None):
    return json.loads(votes.get_party_approvals(data_initiatives_votes).to_json(orient="index"))
