from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI
from loguru import logger

from common.dependencies.mapping import dependencies_map


def _pretty_log(dependencies: dict, indent=0):
    for key, value in dependencies.items():
        logger.info("\t" * indent + str(key))
        if isinstance(value, dict):
            _pretty_log(value, indent + 1)
        else:
            logger.info("\t" * (indent + 1) + str(value))


def setup_dependencies(app: FastAPI, mapper: Optional[Dict[Any, Callable]] = None):
    """Переопределение интерфейсов реальными экземплярами фабрик классов"""
    if mapper is None:
        mapper = dependencies_map
    for interface, dependency in mapper.items():
        app.dependency_overrides[interface] = dependency

    logger.info("\nDependencies mapping: %s", _pretty_log(app.dependency_overrides))

    return None
