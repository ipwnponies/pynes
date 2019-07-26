from typing import Any
from typing import List
from typing import Tuple

import pytest


def named_parametrize(argnames: Tuple[str, ...], id_and_argvalues: List[Tuple[Any, ...]]) -> Any:
    single_param = False
    if isinstance(argnames, str) and len(argnames.split(',')) == 1:
        # pytest parametrize argnames passed as comma-separated string
        single_param = True
    elif len(argnames) == 1:
        # pytest parametrize argnames passed as list or tuple
        single_param = True

    return pytest.mark.parametrize(
        argnames,
        argvalues=[
            # Unpack single element tuple, same interface as pytest parametrize
            param[1] if single_param else param[1:]
            for param in id_and_argvalues
        ],
        ids=[param[0] for param in id_and_argvalues],
    )
