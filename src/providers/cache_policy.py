from dataclasses import dataclass


@dataclass(frozen=True)
class CachePolicy:
    enabled: bool = False
    keep_download: bool = False