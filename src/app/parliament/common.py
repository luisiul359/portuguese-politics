<<<<<<< HEAD
from .model.legislature import Legislatura
=======
from src.app.parliament.model.legislature import Legislatura
>>>>>>> branch 'add-agenda' of git@github.com:luisiul359/portuguese-politics.git


supported_legislatures = [Legislatura.XIV, Legislatura.XV, Legislatura.XVI]
current_legislature = list(supported_legislatures)[-1]
