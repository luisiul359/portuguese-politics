from typing import Any, List, Union

from parliament.models.legislature import Legislatura


supported_legislatures = {Legislatura.XIV, Legislatura.XV, Legislatura.XVI}
current_legislature = list(supported_legislatures)[-1]


def to_list(x: Union[Any, List]) -> List:
    return x if isinstance(x, list) else [x]


def get_most_recent_status(x: Union[Any, List], date_field):
    obj_as_list = to_list(x)
    return list(sorted(obj_as_list, key=lambda x: x[date_field]))[-1]


class MyDict(dict):
    """
    If the get value of a key is None we ruturn the default value instead.
    """

    def get(self, key: Any, default: Any):
        value = super().get(key, default)

        if value:
            return MyDict(value) if isinstance(value, dict) else value
        else:
            return default
