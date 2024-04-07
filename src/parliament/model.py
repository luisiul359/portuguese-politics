from enum import Enum


class Legislatura(str, Enum):
    XV = "XV"
    XVI = "XVI"


supported_legislatures = {Legislatura.XV, Legislatura.XVI}
current_legislature = list(supported_legislatures)[-1]
