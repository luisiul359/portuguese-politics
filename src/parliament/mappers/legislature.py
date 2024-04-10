from parliament.model import Legislatura


def map_to_legislature(leg: str) -> Legislatura:
    match leg:
        case "XV":
            return Legislatura.XV
        case "XVI":
            return Legislatura.XVI
