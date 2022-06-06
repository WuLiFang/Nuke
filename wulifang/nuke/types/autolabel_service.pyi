from typing import Optional, Protocol

class AutolabelService(Protocol):
    def autolabel(self) -> Optional[bytes]: ...
