"""Web utilities: page text extraction, RSS/Atom parsing, IP masking (stdlib + bs4)."""

from __future__ import annotations

import ipaddress
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from .._core.errors import ErrorCode, EtoolError

_USER_AGENT = "etool/2.x (+https://github.com/jiangyangcreate/etool)"


class ManagerWeb:
    @staticmethod
    def fetch_html(url: str, timeout: int = 30) -> str:
        """Fetch a URL and return the response body as text."""
        request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset, errors="replace")
        except urllib.error.HTTPError as e:
            raise EtoolError(
                ErrorCode.RUNTIME_ERROR, f"fetch failed with HTTP {e.code}", {"url": url}
            ) from e
        except urllib.error.URLError as e:
            raise EtoolError(
                ErrorCode.RUNTIME_ERROR, f"fetch failed: {e.reason}", {"url": url}
            ) from e

    @staticmethod
    def html_to_text(html: str) -> str:
        """Extract readable text from HTML (drops script/style/nav noise)."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "template"]):
            tag.decompose()
        lines = (line.strip() for line in soup.get_text("\n").splitlines())
        return "\n".join(line for line in lines if line)

    @classmethod
    def fetch_text(cls, url: str, timeout: int = 30) -> str:
        """Fetch a page and return its readable text content."""
        text = cls.html_to_text(cls.fetch_html(url, timeout=timeout))
        if not text:
            raise EtoolError(
                ErrorCode.RUNTIME_ERROR, "no readable text found in page", {"url": url}
            )
        return text

    @classmethod
    def rss_entries(cls, source: str, timeout: int = 30) -> list[dict[str, str]]:
        """Parse an RSS 2.0 or Atom feed (URL, file path, or XML string).

        :return: list of {"title", "link", "published", "summary"} dicts
        """
        if source.lstrip().startswith("<"):
            xml_text = source
        elif source.startswith(("http://", "https://")):
            xml_text = cls.fetch_html(source, timeout=timeout)
        elif Path(source).exists():
            xml_text = Path(source).read_text(encoding="utf-8")
        else:
            raise EtoolError(
                ErrorCode.NOT_FOUND, "feed source is not a URL, file, or XML", {"source": source}
            )

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            raise EtoolError(ErrorCode.RUNTIME_ERROR, f"feed XML parse error: {e}") from e

        def text_of(parent: ET.Element, *names: str) -> str:
            for name in names:
                node = parent.find(name)
                if node is not None and node.text:
                    return node.text.strip()
            return ""

        entries: list[dict[str, str]] = []
        # RSS 2.0: <rss><channel><item>
        for item in root.iter("item"):
            entries.append(
                {
                    "title": text_of(item, "title"),
                    "link": text_of(item, "link"),
                    "published": text_of(item, "pubDate", "{http://purl.org/dc/elements/1.1/}date"),
                    "summary": text_of(item, "description"),
                }
            )
        if entries:
            return entries

        # Atom: <feed><entry>
        atom = "{http://www.w3.org/2005/Atom}"
        for entry in root.iter(f"{atom}entry"):
            link = ""
            for node in entry.findall(f"{atom}link"):
                if node.get("rel") in (None, "alternate"):
                    link = node.get("href", "")
                    break
            entries.append(
                {
                    "title": text_of(entry, f"{atom}title"),
                    "link": link,
                    "published": text_of(entry, f"{atom}published", f"{atom}updated"),
                    "summary": text_of(entry, f"{atom}summary", f"{atom}content"),
                }
            )
        return entries

    @staticmethod
    def mask_ip(ip: str) -> str:
        """Anonymize an IP for display: IPv4 a.b.x.d, IPv6 keeps head/tail groups."""
        try:
            parsed = ipaddress.ip_address(ip.strip())
        except ValueError as e:
            raise EtoolError(ErrorCode.VALIDATION_ERROR, f"invalid IP address: {ip}") from e
        if parsed.version == 4:
            parts = str(parsed).split(".")
            return f"{parts[0]}.{parts[1]}.x.{parts[3]}"
        parts = parsed.exploded.split(":")
        return ":".join(parts[:2] + ["xxxx"] * 4 + parts[-2:])

    @staticmethod
    def is_public_ip(ip: str) -> bool:
        """True when the address is globally routable (not private/loopback/link-local)."""
        try:
            return ipaddress.ip_address(ip.strip()).is_global
        except ValueError as e:
            raise EtoolError(ErrorCode.VALIDATION_ERROR, f"invalid IP address: {ip}") from e
