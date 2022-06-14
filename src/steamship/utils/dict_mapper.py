"""Helper classes for mapping third-party API response objects into Steamship model objects.

Many third-party APIs produce data that is isomorphic, but differently structured, than Steamship plugin responses.
These utility classes reduce the required conversion to a declarative specification, enabling faster, simpler, and more
error-robust construction of Steamship Plugins which wrap third-party services.

For a usage example, see the documentation on the `reshape_array_of_dicts` function below.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel

from steamship import SteamshipError


def get_value_at_keypath(
    input_dict: Optional[Dict],
    keypath: List[Union[str, int]],
    expect_type: Optional[Any] = None,
    required: bool = True,
) -> Optional[Any]:
    """Extracts value at the provided `keypath` from `dict`.

    - If `expect_type` is not None, requires that any non-None return type match that type.
    - if `throw_on_missing` is True (default), will throw if the return value is None
    """
    pointer = input_dict
    traversed_keypath = []
    for key in keypath:
        if pointer is None:
            if required:
                raise SteamshipError(
                    message=f"[get_keypath] After traversing keypath {traversed_keypath} in object, found null instead of container for expected key {key}."
                )
            return None

        if isinstance(pointer, dict):
            if key not in pointer:
                if required:
                    raise SteamshipError(
                        message=f"[get_keypath] After traversing keypath {traversed_keypath} in object, unable to find expected key {key}."
                    )
                return None
            traversed_keypath.append(key)
            pointer = pointer.get(key, None)
        elif isinstance(pointer, list):
            if key < 0 or key >= len(pointer):
                if required:
                    raise SteamshipError(
                        message=f"[get_keypath] After traversing keypath {traversed_keypath} in object, key {key} was out of range of list of length {len(pointer)}."
                    )
                return None
            traversed_keypath.append(key)
            pointer = pointer[key]

    # Final check for None
    if pointer is None:
        if required:
            raise SteamshipError(
                message=f"[get_keypath] After traversing keypath {traversed_keypath} in object, object was None."
            )
        return None

    # It's not None. If there's a expected type, check for it.
    if expect_type is not None:
        if not isinstance(pointer, expect_type):
            raise SteamshipError(
                message=f"Attempting to unwrap tags from response but type of tag list was f{type(expect_type)}."
            )

    return pointer


@dataclass
class Mapping:
    """A mapping into some external object type, such as a third-party API response.

    Behavior:
        - If `const` is not None, the mapping always resolves to that value.
        - If `keypath` is not None, the mapping applies `get_value_at_keypath` against the dict
        - If both are None, an error is thrown.
    """

    keypath: Optional[List[Union[str, int]]] = None
    expect_type: Optional[Any] = None
    required: bool = True
    const: Optional[Any] = None

    def resolve_against(self, input_dict: Dict) -> Optional[Any]:
        """Resolves this mapping against a dictionary."""

        if self.const is not None:
            return self.const
        elif self.keypath is not None:
            return get_value_at_keypath(
                input_dict=input_dict,
                keypath=self.keypath,
                expect_type=self.expect_type,
                required=self.required,
            )
        else:
            raise SteamshipError(message="Either `const` or `keypath` must be not None.")


def reshape_dict(
    input_dict: Dict,
    mappings: Dict[str, Mapping],
    into_base_model: Optional[Type[BaseModel]] = None,
) -> Union[Dict, BaseModel]:
    """Produces a new, 1-level deep, dictionary or BaseModel from a set of mappings against `input_dict`

    - If `into_pydantic` is not None, the resulting dictionary will be parsed into the provided Pydantic class.
    """
    ret = {key: mapping.resolve_against(input_dict) for key, mapping in mappings.items()}

    if into_base_model is not None:
        return into_base_model(**ret)
    return ret if into_base_model is None else into_base_model(**ret)


def reshape_array_of_dicts(
    input_dict: Dict,
    array_keypath: List[Union[str, int]],
    array_required: bool,
    mappings: Dict[str, Mapping],
    into_base_model: Optional[Type[BaseModel]] = None,
) -> List[Dict]:
    """Produces an array of new dictionaries from a set of mappings against the items at `keypath` in `input_dict`

    For example, to reshape the object:

       {
          "entities": [
             {
               "entity": {
                  "entityTag": "ORG",
                  "start": 1,
                  "end": 5
               }
            }
          ]
      }

    Into an array containing the Steamship Tag.CreateRequest objects, one can write:

       reshape_array_of_dicts(
         input_dict: input_dict,
         array_keypath: ["entities"],
         array_required: True,
         mappings: {
            "kind": Mapping(const="NER"),
            "name": Mapping(keypath=["entity", "entityTag"]),
            "start_idx": Mapping(keypath=["entity", "start"]),
            "end_idx": Mapping(keypath=["entity", "start"])
         },
         into_base_model: Tag.CreateRequest
       )

    Producing the following output:

       [
         Tag.CreateRequest(
            kind="NER",
            name="ORG",
            start_idx=1,
            end_idx=5
         )
       ]
    """

    input_array = get_value_at_keypath(
        input_dict=input_dict, keypath=array_keypath, expect_type=list, required=array_required
    )

    return [
        reshape_dict(inner_dict, mappings, into_base_model=into_base_model)
        for inner_dict in input_array or []
    ]
