# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Versioned JSON schemas, validated at export and at import (fail closed)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema

SCHEMA_DIR = Path(__file__).with_name("schemas")
RESULT_SCHEMA = "result-1.0.0.json"
RESULT_SCHEMA_VERSION = "1.0.0"


class SchemaError(ValueError):
    """An instance does not conform to its schema."""


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / name
    if not path.is_file():
        raise SchemaError(f"unknown schema: {name}")
    schema = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return schema


def validate_instance(instance: Any, schema_name: str) -> None:
    validator = jsonschema.Draft202012Validator(load_schema(schema_name))
    errs = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    if errs:
        first = errs[0]
        where = "/".join(str(x) for x in first.absolute_path) or "<root>"
        raise SchemaError(f"{schema_name}: {len(errs)} error(s); first at {where}: {first.message}")


def write_result(result: dict[str, Any], path: str | Path) -> Path:
    """Validate, then write. Nothing is written if validation fails."""
    validate_instance(result, RESULT_SCHEMA)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(result, indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(p)
    return p


def read_result(path: str | Path) -> dict[str, Any]:
    """Read and validate a result file; raises SchemaError on malformed or missing content."""
    p = Path(path)
    if not p.is_file():
        raise SchemaError(f"result file not found: {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SchemaError(f"result file is not valid JSON: {p}: {exc}") from exc
    validate_instance(data, RESULT_SCHEMA)
    return data
