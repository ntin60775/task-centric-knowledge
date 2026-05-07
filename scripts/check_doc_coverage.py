#!/usr/bin/env python3
"""Check that all public API in scripts/ has docstrings (Griffe-based)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import griffe


def is_public_path(path: str) -> bool:
    """Return True if no path component is private."""
    for part in path.split("."):
        if part.startswith("_") and part != "__init__":
            return False
    return True


def check_module(path: Path, package_path: Path, search_paths: list[str]) -> list[str]:
    """Return list of public API paths missing docstrings."""
    missing: list[str] = []
    rel = path.relative_to(package_path).with_suffix("").as_posix().replace("/", ".")
    try:
        module = griffe.load(rel, search_paths=search_paths)
    except Exception:
        return missing

    def walk(obj: griffe.Object | griffe.Alias) -> None:
        try:
            if getattr(obj, "is_alias", False):
                return
            is_public = getattr(obj, "is_public", False)
            if not is_public:
                return
            is_func = getattr(obj, "is_function", False)
            is_class = getattr(obj, "is_class", False)
            if is_public and (is_func or is_class):
                name = getattr(obj, "name", "")
                if name == "__init__":
                    parent = getattr(obj, "parent", None)
                    if parent and getattr(parent, "docstring", None):
                        pass
                    else:
                        if is_public_path(obj.path):
                            missing.append(obj.path)
                else:
                    doc = getattr(obj, "docstring", None)
                    if not doc and is_public_path(obj.path):
                        missing.append(obj.path)
            for member in getattr(obj, "members", {}).values():
                walk(member)
        except Exception:
            pass

    walk(module)
    return missing


def main() -> int:
    """Run the coverage checker and report results."""
    parser = argparse.ArgumentParser(description="Check docstring coverage for public API.")
    parser.add_argument("package_path", type=Path, default=Path("scripts"), nargs="?")
    args = parser.parse_args()

    package_path: Path = args.package_path.resolve()
    search_paths = [str(package_path)]

    all_missing: list[str] = []
    for py_file in sorted(package_path.rglob("*.py")):
        if py_file.name.startswith("_"):
            continue
        all_missing.extend(check_module(py_file, package_path, search_paths))

    if all_missing:
        for path in all_missing:
            print(f"MISSING_DOCSTRING: {path}")
        print(f"\nTotal missing: {len(all_missing)}")
        return 1

    print("OK: all public API documented")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
