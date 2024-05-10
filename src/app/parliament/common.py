from .model.legislature import Legislatura


supported_legislatures = [Legislatura.XIV, Legislatura.XV, Legislatura.XVI]
current_legislature = list(supported_legislatures)[-1]
