from ._network._speed import ManagerSpeed
from ._network._share import ManagerShare

from ._other._password import ManagerPassword
from ._other._scheduler import ManagerScheduler

from ._office._image import ManagerImage
from ._office._email import ManagerEmail
from ._office._docx import ManagerDocx
from ._office._excel import ManagerExcel
from ._office._ipynb import ManagerIpynb
from ._office._qrcode import ManagerQrcode
from ._office._pdf import ManagerPdf

__all__ = [
    "ManagerSpeed",
    "ManagerShare",
    "ManagerPassword",
    "ManagerScheduler",
    "ManagerImage",
    "ManagerEmail",
    "ManagerDocx",
    "ManagerExcel",
    "ManagerIpynb",
    "ManagerQrcode",
    "ManagerPdf",
]
