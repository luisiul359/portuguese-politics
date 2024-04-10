from parliament.models.legislature import Legislatura


def map_to_legislature(leg: str) -> Legislatura:
    match leg:
        case "XIV":
            return Legislatura.XIV
        case "XV":
            return Legislatura.XV
        case "XVI":
            return Legislatura.XVI
