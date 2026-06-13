from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Type

from query_expansion.types import QueryExpansionProvider

_PROVIDER_REGISTRY: Dict[str, Type[QueryExpansionProvider]] = {}


def register_provider(provider_cls: Type[QueryExpansionProvider]) -> Type[QueryExpansionProvider]:
    name = getattr(provider_cls, "name", None)
    if not name:
        raise ValueError("Provider class must define a non-empty name")
    _PROVIDER_REGISTRY[name] = provider_cls
    return provider_cls


def get_registered_providers() -> List[Type[QueryExpansionProvider]]:
    return list(_PROVIDER_REGISTRY.values())


def discover_providers() -> None:
    package_name = __name__
    package_dir = Path(__file__).resolve().parent
    for module in pkgutil.iter_modules([str(package_dir)]):
        if module.ispkg or module.name.startswith("_"):
            continue
        importlib.import_module(f"{package_name}.{module.name}")
