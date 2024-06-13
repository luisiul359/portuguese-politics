from enum import Enum


class Legislatura(str, Enum):
    XV = "XV"
    XVI = "XVI"


supported_legislatures = {Legislatura.XV, Legislatura.XVI}
