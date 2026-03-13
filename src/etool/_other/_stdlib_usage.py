import ast
import json
import os
import sys
import sysconfig
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set, Tuple


def _iter_python_files(root: str) -> Iterable[str]:
    """
    Recursively yield all .py files under root, skipping any `.venv` directories.
    """
    for current_root, dirs, files in os.walk(root):
        # Skip .venv directories
        dirs[:] = [d for d in dirs if d != ".venv"]
        for filename in files:
            if filename.endswith(".py"):
                yield os.path.join(current_root, filename)


def _build_stdlib_modules() -> Set[str]:
    """
    Build a set of module names that belong to the current interpreter's standard library.

    This is based on the local Python installation, so different Python versions will
    naturally result in different standard library sets.
    """
    modules: Set[str] = set(sys.builtin_module_names)

    stdlib_path = sysconfig.get_paths().get("stdlib")
    if not stdlib_path or not os.path.isdir(stdlib_path):
        return modules

    for root, dirs, files in os.walk(stdlib_path):
        rel_root = os.path.relpath(root, stdlib_path)
        if rel_root == ".":
            pkg_prefix = ""
        else:
            pkg_prefix = rel_root.replace(os.sep, ".") + "."

        # Packages (directories)
        for d in dirs:
            modules.add(pkg_prefix + d)

        # Simple modules
        for filename in files:
            if not filename.endswith(".py") or filename == "__init__.py":
                continue
            mod_name = pkg_prefix + filename[:-3]
            modules.add(mod_name)

    return modules


def _is_stdlib_module(module_name: str, stdlib_modules: Set[str]) -> bool:
    """
    Check whether a module name belongs to the standard library set.
    """
    if module_name in stdlib_modules:
        return True
    top_level = module_name.split(".", 1)[0]
    return top_level in stdlib_modules


def _analyze_file(
    file_path: str,
    stdlib_modules: Set[str],
    aggregated: Dict[str, Dict[str, int]],
) -> None:
    """
    Analyze a single Python file and update aggregated counts in place.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except (OSError, UnicodeDecodeError):
        return

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return

    # alias -> full module name (e.g. {"os": "os", "op": "os.path"})
    alias_to_module: Dict[str, str] = {}
    # local name -> (module, attr_path) from `from x import y as z`
    name_to_module_attr: Dict[str, Tuple[str, str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                full_name = alias.name  # e.g. "os" or "os.path"
                # bound name is either alias.asname or the first segment of full_name
                bound_name = alias.asname or full_name.split(".", 1)[0]
                if _is_stdlib_module(full_name, stdlib_modules):
                    alias_to_module[bound_name] = full_name

        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            module_name = node.module  # e.g. "os"
            if not _is_stdlib_module(module_name, stdlib_modules):
                continue
            for alias in node.names:
                if alias.name == "*":
                    # Skip star imports; they are ambiguous to resolve statically
                    continue
                bound_name = alias.asname or alias.name
                name_to_module_attr[bound_name] = (module_name, alias.name)

    def _record_call(module_name: str, attr_path: str) -> None:
        top_level = module_name.split(".", 1)[0]
        if not _is_stdlib_module(top_level, stdlib_modules):
            return
        module_bucket = aggregated[top_level]
        module_bucket[attr_path] = module_bucket.get(attr_path, 0) + 1

    def _resolve_attribute(attr: ast.Attribute) -> Tuple[Optional[str], str]:
        """
        Resolve an attribute chain into (base_name, attr_path).

        Example:
            os.path.join -> ("os", "path.join")
            path.join    -> ("path", "join")
        """
        parts: List[str] = []
        current: ast.AST = attr

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if not isinstance(current, ast.Name):
            return None, ""

        base_name = current.id
        parts.reverse()
        attr_path = ".".join(parts) if parts else ""
        return base_name, attr_path

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func

        # Case 1: attribute access, e.g. os.path.join(), sys.exit(), op.join()
        if isinstance(func, ast.Attribute):
            base_name, attr_path = _resolve_attribute(func)
            if not base_name:
                continue

            # Imported via `import x` or `import x.y as z`
            if base_name in alias_to_module:
                full_mod = alias_to_module[base_name]
                # e.g. os.path.join when full_mod == "os.path" and attr_path == "join"
                sub_path = ".".join(full_mod.split(".")[1:])
                if sub_path and attr_path:
                    combined_attr = f"{sub_path}.{attr_path}"
                elif sub_path:
                    combined_attr = sub_path
                else:
                    combined_attr = attr_path or ""

                if combined_attr:
                    _record_call(full_mod, combined_attr)
                continue

            # Imported via `from os import path as p`
            if base_name in name_to_module_attr:
                mod, first_attr = name_to_module_attr[base_name]
                if attr_path:
                    combined_attr = f"{first_attr}.{attr_path}"
                else:
                    combined_attr = first_attr
                _record_call(mod, combined_attr)
                continue

        # Case 2: simple name call, e.g. exit(), path()
        elif isinstance(func, ast.Name):
            name = func.id
            if name in name_to_module_attr:
                mod, attr = name_to_module_attr[name]
                _record_call(mod, attr)


def analyze_stdlib_usage(folder: str) -> Dict[str, Dict[str, int]]:
    """
    Analyze how often standard-library modules and their attributes are called
    within all Python files under the given folder (excluding `.venv`).

    Returns:
        Dict[str, Dict[str, int]]: {module: {attribute_path: count}}
    """
    folder = os.path.abspath(folder)
    stdlib_modules = _build_stdlib_modules()

    aggregated: Dict[str, Dict[str, int]] = defaultdict(dict)

    for file_path in _iter_python_files(folder):
        _analyze_file(file_path, stdlib_modules, aggregated)

    # Convert defaultdict to plain dicts for a clean JSON structure
    return {mod: dict(attrs) for mod, attrs in aggregated.items() if attrs}


class ManagerStdlibUsage:
    """
    Manager-style wrapper for standard library usage analysis.
    """

    @staticmethod
    def analyze(folder: str) -> Dict[str, Dict[str, int]]:
        return analyze_stdlib_usage(folder)

    @staticmethod
    def analyze_to_json(folder: str, indent: int = 2, ensure_ascii: bool = False) -> str:
        data = analyze_stdlib_usage(folder)
        return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)


if __name__ == "__main__":
    """
    Simple CLI usage:

    python -m etool._other._stdlib_usage <folder>
    """
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    print(ManagerStdlibUsage.analyze_to_json(target))

