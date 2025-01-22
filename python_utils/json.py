from typing import Mapping, Sequence, TypedDict, Union

JSONSerializableType = Union[
    str,
    int,
    float,
    bool,
    Sequence["JSONSerializableType"],
    Mapping[str, "JSONSerializableType"],
    TypedDict,
    None,
]
JsonDict = dict[str, JSONSerializableType]
