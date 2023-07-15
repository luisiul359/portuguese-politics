from typing import Union, Any, List


def to_list(x: Union[Any, List]) -> List:
    return x if isinstance(x, list) else [x]


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
