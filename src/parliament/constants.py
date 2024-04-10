from parliament.model import Legislatura


supported_legislatures = {Legislatura.XV, Legislatura.XVI}
current_legislature = list(supported_legislatures)[-1]
