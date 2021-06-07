from typing import Dict, List, Tuple

import six

_EXISTS_CACHE: Dict[six.text_type, Tuple[float, bool]]

def exists(
    path: six.text_type,
    ttl: int = ...,
) -> bool: ...
def get(
    filename: six.text_type,
    first: int,
    last: int,
    ttl: int = ...,
) -> List[int]: ...
