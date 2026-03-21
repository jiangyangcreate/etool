"""
etool — cross-platform utility toolkit (2.x), AI-friendly envelopes in etool._core.
"""

from __future__ import annotations

import warnings
from typing import Dict, List, Tuple

from ._core.errors import ErrorCode, EtoolError, err, is_ok, ok

__all__: List[str] = [
    "ErrorCode",
    "EtoolError",
    "err",
    "is_ok",
    "ok",
]
_failed_imports: List[Tuple[str, str]] = []

# Network
try:
    from ._network._speed import ManagerSpeed

    __all__.append("ManagerSpeed")
except ImportError as e:
    _failed_imports.append(("ManagerSpeed", str(e)))
    warnings.warn(f"Failed to import ManagerSpeed: {e}", ImportWarning, stacklevel=2)

# Other
try:
    from ._other._password import ManagerPassword

    __all__.append("ManagerPassword")
except ImportError as e:
    _failed_imports.append(("ManagerPassword", str(e)))
    warnings.warn(f"Failed to import ManagerPassword: {e}", ImportWarning, stacklevel=2)

try:
    from ._other._scheduler import ManagerScheduler

    __all__.append("ManagerScheduler")
except ImportError as e:
    _failed_imports.append(("ManagerScheduler", str(e)))
    warnings.warn(f"Failed to import ManagerScheduler: {e}", ImportWarning, stacklevel=2)

try:
    from ._other._install import ManagerInstall

    __all__.append("ManagerInstall")
except ImportError as e:
    _failed_imports.append(("ManagerInstall", str(e)))
    warnings.warn(f"Failed to import ManagerInstall: {e}", ImportWarning, stacklevel=2)

try:
    from ._other._stdlib_usage import ManagerStdlibUsage, analyze_stdlib_usage

    __all__.append("ManagerStdlibUsage")
    __all__.append("analyze_stdlib_usage")
except ImportError as e:
    _failed_imports.append(("ManagerStdlibUsage", str(e)))
    warnings.warn(f"Failed to import ManagerStdlibUsage: {e}", ImportWarning, stacklevel=2)

# Office
try:
    from ._office._image import ManagerImage

    __all__.append("ManagerImage")
except ImportError as e:
    _failed_imports.append(("ManagerImage", str(e)))
    warnings.warn(f"Failed to import ManagerImage: {e}", ImportWarning, stacklevel=2)

try:
    from ._office._email import ManagerEmail

    __all__.append("ManagerEmail")
except ImportError as e:
    _failed_imports.append(("ManagerEmail", str(e)))
    warnings.warn(f"Failed to import ManagerEmail: {e}", ImportWarning, stacklevel=2)

try:
    from ._office._docx import ManagerDocx

    __all__.append("ManagerDocx")
except ImportError as e:
    _failed_imports.append(("ManagerDocx", str(e)))
    warnings.warn(f"Failed to import ManagerDocx: {e}", ImportWarning, stacklevel=2)

try:
    from ._office._excel import ManagerExcel

    __all__.append("ManagerExcel")
except ImportError as e:
    _failed_imports.append(("ManagerExcel", str(e)))
    warnings.warn(f"Failed to import ManagerExcel: {e}", ImportWarning, stacklevel=2)

try:
    from ._office._ipynb import ManagerIpynb

    __all__.append("ManagerIpynb")
except ImportError as e:
    _failed_imports.append(("ManagerIpynb", str(e)))
    warnings.warn(f"Failed to import ManagerIpynb: {e}", ImportWarning, stacklevel=2)

try:
    from ._office._qrcode import ManagerQrcode

    __all__.append("ManagerQrcode")
except ImportError as e:
    _failed_imports.append(("ManagerQrcode", str(e)))
    warnings.warn(f"Failed to import ManagerQrcode: {e}", ImportWarning, stacklevel=2)

try:
    from ._office._pdf import ManagerPdf

    __all__.append("ManagerPdf")
except ImportError as e:
    _failed_imports.append(("ManagerPdf", str(e)))
    warnings.warn(f"Failed to import ManagerPdf: {e}", ImportWarning, stacklevel=2)

# Markdown
try:
    from ._md._md_to_docx import ManagerMd

    __all__.append("ManagerMd")
except ImportError as e:
    _failed_imports.append(("ManagerMd", str(e)))
    warnings.warn(f"Failed to import ManagerMd: {e}", ImportWarning, stacklevel=2)


def get_import_status() -> Dict[str, List]:
    """Return which submodules loaded and which failed."""
    return {
        "available": __all__.copy(),
        "failed": _failed_imports.copy(),
    }


def is_available(module_name: str) -> bool:
    return module_name in __all__


def get_version() -> str:
    return "2.1.0"
