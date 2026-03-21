"""QR code generation and local decoding (cross-platform; no online APIs)."""

from __future__ import annotations

import qrcode


class ManagerQrcode:
    @staticmethod
    def decode_qrcode(path: str) -> str | None:
        """
        Decode a QR code image file using OpenCV (offline).

        :param path: Image file path
        :return: Decoded string, or None if decoding fails
        """
        import cv2

        img = cv2.imread(path)
        if img is None:
            return None
        det = cv2.QRCodeDetector()
        val, _, _ = det.detectAndDecode(img)
        return val if val else None

    @staticmethod
    def generate_english_qrcode(words: str, save_path: str) -> str:
        """Generate a QR code image (same as generate_qrcode)."""
        return ManagerQrcode.generate_qrcode(words, save_path)

    @staticmethod
    def generate_qrcode(content: str, save_path: str) -> str:
        """
        Generate a QR code image.

        :param content: Text or URL to encode
        :param save_path: Output image path
        """
        img = qrcode.make(content)
        img.save(save_path)
        return save_path
