from parliament.common import current_legislature
from src.app.parliament.model.legislature import Legislatura


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
