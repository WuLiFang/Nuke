from typing import Optional, Protocol
from wulifang._compat.str import Str

class AutolabelService(Protocol):
    def autolabel(self) -> Optional[Str]: ...
