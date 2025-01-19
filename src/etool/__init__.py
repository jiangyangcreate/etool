from ._network._speed import SpeedManager
from ._network._share_screen import screen_share
from ._network._share_file import share_file

from ._office._image import ImageManager
from ._office._pdf import PdfManager
from ._office._docx import DocxManager
from ._office._excel import ExcelManager
from ._office._email import EmailManager
from ._office._ipynb import IpynbManager
from ._office._qrcode import QrcodeManager

from ._other._password import PasswordManager
from ._other._scheduler import pocwatch

__all__ = [
    'SpeedManager',
    'screen_share',
    'share_file',
    'ImageManager',
    'PdfManager',
    'DocxManager',
    'ExcelManager',
    'EmailManager',
    'IpynbManager',
    'QrcodeManager',
    'ScreateManager',
    'pocwatch',
    'PasswordManager',
]
