from parliament.models.legislature import Legislatura
from parliament.common import current_legislature

def map_to_legislature(leg: str) -> Legislatura:
    match leg:
        case "XIV":
            return Legislatura.XIV
        case "XV":
            return Legislatura.XV
        case "XVI":
            return Legislatura.XVI
        case _:
            return current_legislature
