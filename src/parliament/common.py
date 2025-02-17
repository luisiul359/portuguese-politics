from typing import Any, List, Union


def to_list(x: Union[Any, List]) -> List:
    return [v for v in (x if isinstance(x, list) else [x]) if v]


def get_most_recent_status(x: Union[Any, List], date_field):
    if not x: return {"carDes": "not found"}

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
