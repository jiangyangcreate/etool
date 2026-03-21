"""Tests for etool 2.x (cross-platform; no GPU/share/COM)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
sys.path.insert(0, os.path.join(project_root, "src"))

os.chdir(test_dir)

from etool import (  # noqa: E402
    ManagerDocx,
    ManagerExcel,
    ManagerImage,
    ManagerInstall,
    ManagerIpynb,
    ManagerMd,
    ManagerPassword,
    ManagerPdf,
    ManagerQrcode,
    ManagerSpeed,
    analyze_stdlib_usage,
    get_version,
    ok,
)
from etool._core.errors import ErrorCode, EtoolError, err  # noqa: E402
from pypdf import PdfWriter  # noqa: E402


def test_version():
    assert get_version() == "2.0.0"


def test_result_envelope():
    assert ok({"a": 1})["ok"] is True
    e = EtoolError(ErrorCode.VALIDATION_ERROR, "bad")
    assert err(e)["ok"] is False


def test_speed_disk_memory():
    assert ManagerSpeed.disk(file_size_mb=2) is not None
    assert ManagerSpeed.memory(size_mb=4) is not None


@patch("speedtest.Speedtest")
def test_speed_network_mocked(mock_st):
    mock_inst = mock_st.return_value
    mock_inst.get_best_server.return_value = None
    mock_inst.download.return_value = 10_000_000
    mock_inst.upload.return_value = 5_000_000
    mock_inst.results = MagicMock(ping=10.0)
    assert "Mbps" in ManagerSpeed.network()


@pytest.mark.skip(reason="发送邮件不宜频繁测试，跳过")
def test_email_manager():
    pass


@pytest.mark.skip(reason="定时发送不宜频繁测试，跳过")
def test_scheduler_manager():
    pass


def test_image_manager():
    assert ManagerImage.merge_LR(["pic1.webp", "pic2.webp"]) is not None
    assert ManagerImage.merge_UD(["pic1.webp", "pic2.webp"]) is not None
    assert ManagerImage.fill_image("pic1_UD.webp") is not None
    assert isinstance(ManagerImage.cut_image("pic1_UD_fill.webp"), list)
    assert ManagerImage.rename_images("image_dir", remove=True) is not None


def test_password_manager():
    assert (
        len(
            ManagerPassword.generate_pwd_list(
                ManagerPassword.results["all_letters"] + ManagerPassword.results["digits"],
                2,
            )
        )
        > 0
    )
    assert len(ManagerPassword.random_pwd(8)) == 8


def test_password_manager_convert_base():
    assert ManagerPassword.convert_base("A1F", 16, 2) == "101000011111"
    assert ManagerPassword.convert_base("-1101", 2, 16) == "-D"
    assert ManagerPassword.convert_base("Z", 36, 10) == "35"


def test_qrcode_manager():
    assert ManagerQrcode.generate_english_qrcode("https://www.baidu.com", "qr.png") is not None
    assert ManagerQrcode.generate_qrcode("百度", "qr.png") is not None
    assert ManagerQrcode.decode_qrcode("qr.png") is not None


def test_ipynb_manager():
    assert ManagerIpynb.merge_notebooks("ipynb_dir") is not None
    out = ManagerIpynb.convert_notebook_to_markdown("ipynb_dir.ipynb", "")
    assert out is not None
    assert Path(out).is_file()


def test_docx_manager():
    assert ManagerDocx.replace_words("ex1.docx", "1", "2") is not None
    assert ManagerDocx.change_forward("ex1.docx", "result.docx") is not None
    assert ManagerDocx.get_pictures("ex1.docx", "result") is not None


def test_md_docx_manager():
    assert ManagerMd.convert_md_to_docx("test.md", "test.docx") is not None
    assert ManagerMd.convert_md_to_html("test.md", "test.html") is not None
    assert ManagerMd.extract_tables_to_excel("test.md", "test.xlsx") is not None


def test_excel_manager():
    assert ManagerExcel.excel_format("ex1.xlsx", "result.xlsx") is not None


def test_pdf_merge_split_encrypt(tmp_path: Path):
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    w = PdfWriter()
    w.add_blank_page(width=200, height=200)
    w.write(a.open("wb"))
    w2 = PdfWriter()
    w2.add_blank_page(width=200, height=200)
    w2.write(b.open("wb"))

    merged = tmp_path / "merged.pdf"
    ManagerPdf.merge_pdfs([str(a), str(b)], str(merged))
    assert merged.is_file()

    ManagerPdf.split_by_pages(merged, 1)
    part1 = tmp_path / "merged_part_by_page1.pdf"
    assert part1.is_file()

    enc = tmp_path / "enc.pdf"
    ManagerPdf.encrypt_pdf(str(part1), "secret", encrypted_filename=enc)
    assert enc.is_file()
    dec = tmp_path / "dec.pdf"
    ManagerPdf.decrypt_pdf(str(enc), "secret", decrypted_filename=dec)
    assert dec.is_file()


def test_cli_password_json():
    exe = sys.executable
    r = subprocess.run(
        [exe, "-m", "etool", "--json", "password", "random", "--length", "12"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(r.stdout.strip())
    assert data["ok"] is True
    assert len(data["data"]["password"]) == 12


def test_cli_version_json():
    exe = sys.executable
    r = subprocess.run(
        [exe, "-m", "etool", "--json", "version"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(r.stdout.strip())
    assert data["ok"] and data["data"]["version"] == "2.0.0"


def test_install_manager_mock_pip():
    with patch("etool._other._install.subprocess.run") as run:
        run.return_value = SimpleNamespace(returncode=0)
        req = os.path.join(test_dir, "requirements.txt")
        failed = os.path.join(test_dir, "failed_requirements_tmp.txt")
        assert ManagerInstall.install_requirements(req, failed) is True
        args = run.call_args[0][0]
        assert args[0] == sys.executable
        assert list(args[1:4]) == ["-m", "pip", "install"]


def test_analyze_stdlib_usage_tmpdir(tmp_path):
    project_dir = tmp_path / "proj"
    project_dir.mkdir()

    file1 = project_dir / "a.py"
    file1.write_text(
        "import os\n"
        "from sys import exit as sys_exit\n"
        "from math import sqrt\n"
        "\n"
        "os.path.join('a', 'b')\n"
        "os.listdir('.')\n"
        "sys_exit(0)\n"
        "sqrt(4)\n",
        encoding="utf-8",
    )

    file2 = project_dir / "b.py"
    file2.write_text(
        "import numpy as np\n"
        "from somepkg import foo\n"
        "\n"
        "np.array([1, 2, 3])\n"
        "foo()\n",
        encoding="utf-8",
    )

    result = analyze_stdlib_usage(str(project_dir))

    assert "os" in result
    assert result["os"]["path.join"] >= 1
    assert result["os"]["listdir"] >= 1

    assert "sys" in result
    assert result["sys"]["exit"] >= 1

    assert "math" in result
    assert result["math"]["sqrt"] >= 1

    assert "numpy" not in result
