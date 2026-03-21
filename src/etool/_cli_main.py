"""Full `etool` CLI: subcommands for major library features with optional --json."""

from __future__ import annotations

import argparse
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

from ._core.errors import EtoolError, ErrorCode, err, ok


def _json_dumps(obj: Any) -> str:
    """Pretty-print JSON for the CLI (valid JSON, 2-space indent; not pprint, so agents can still parse)."""
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


def _emit(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(_json_dumps(payload))
    else:
        if payload.get("ok"):
            data = payload.get("data")
            if isinstance(data, dict) and len(data) == 1 and "message" in data:
                print(data["message"])
            elif data is not None:
                print(_json_dumps(data))
            else:
                print("ok")
        else:
            e = payload.get("error", {})
            print(f"{e.get('code', 'ERROR')}: {e.get('message', '')}", file=sys.stderr)
            if e.get("details"):
                print(_json_dumps(e["details"]), file=sys.stderr)


def _parse_cli_value(s: str) -> Any:
    """Parse scheduler / JSON-like CLI values."""
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        try:
            return int(s)
        except ValueError:
            return s


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="etool",
        description="etool 2.x command-line interface.",
        epilog=(
            "Global: pass --json anywhere in the command line to print the JSON envelope "
            "(success or error) on stdout instead of human-oriented text."
        ),
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the package version and exit (flag; no value).",
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("version", help="Print the package version (same as --version).")

    # password
    p_pw = sub.add_parser("password", help="Password generation and base conversion.")
    pw_sub = p_pw.add_subparsers(dest="pw_cmd", required=True)
    p_rand = pw_sub.add_parser("random", help="Generate a random password string.")
    p_rand.add_argument(
        "--length",
        type=int,
        default=16,
        metavar="N",
        help="Password length in characters (int; default: %(default)s).",
    )
    p_cb = pw_sub.add_parser("convert-base", help="Convert an integer literal between numeric bases.")
    p_cb.add_argument(
        "value",
        help="Number to convert, as a string in the source base (str).",
    )
    p_cb.add_argument(
        "--from-base",
        type=int,
        required=True,
        metavar="B",
        help="Source radix / base (int, 2–36).",
    )
    p_cb.add_argument(
        "--to-base",
        type=int,
        required=True,
        metavar="B",
        help="Target radix / base (int, 2–36).",
    )

    # speed
    p_sp = sub.add_parser("speed", help="Benchmarks: network, disk, or memory throughput.")
    sp_sub = p_sp.add_subparsers(dest="sp_cmd", required=True)
    sp_sub.add_parser(
        "network",
        help="Run speedtest-cli (slow; requires internet). Returns a text report.",
    )
    p_disk = sp_sub.add_parser("disk", help="Disk read/write benchmark using a temporary file.")
    p_disk.add_argument(
        "--file-size-mb",
        type=int,
        default=20,
        metavar="MB",
        help="Temporary file size for the benchmark (int megabytes; default: %(default)s).",
    )
    p_mem = sp_sub.add_parser("memory", help="Memory read/write throughput (stdlib buffers).")
    p_mem.add_argument(
        "--size-mb",
        type=int,
        default=64,
        metavar="MB",
        help="Buffer size for the benchmark (int megabytes; default: %(default)s).",
    )

    # pdf
    p_pdf = sub.add_parser("pdf", help="PDF operations (pypdf + PyMuPDF).")
    pdf_sub = p_pdf.add_subparsers(dest="pdf_cmd", required=True)
    pm = pdf_sub.add_parser("merge", help="Merge multiple PDF files into one.")
    pm.add_argument(
        "--out",
        required=True,
        metavar="PATH",
        help="Output path for the merged PDF (str).",
    )
    pm.add_argument(
        "files",
        nargs="+",
        metavar="PDF",
        help="One or more input PDF paths (str, repeatable).",
    )
    ps = pdf_sub.add_parser("split-pages", help="Split a PDF into chunks of N pages each.")
    ps.add_argument("pdf", help="Input PDF path (str).")
    ps.add_argument(
        "--pages",
        type=int,
        required=True,
        metavar="N",
        help="Page count per output chunk (int).",
    )
    pn = pdf_sub.add_parser("split-num", help="Split a PDF into a fixed number of parts.")
    pn.add_argument("pdf", help="Input PDF path (str).")
    pn.add_argument(
        "--parts",
        type=int,
        required=True,
        metavar="N",
        help="Number of output PDFs (int).",
    )
    pe = pdf_sub.add_parser("encrypt", help="Encrypt a PDF with a password.")
    pe.add_argument("pdf", help="Input PDF path (str).")
    pe.add_argument(
        "--password",
        required=True,
        metavar="STR",
        help="New encryption password (str).",
    )
    pe.add_argument(
        "--old-password",
        metavar="STR",
        help="Previous password if the PDF is already encrypted (str; optional).",
    )
    pe.add_argument(
        "--out",
        metavar="PATH",
        help="Output PDF path (str; optional; default behavior is implementation-defined).",
    )
    pd = pdf_sub.add_parser("decrypt", help="Decrypt a password-protected PDF.")
    pd.add_argument("pdf", help="Input PDF path (str).")
    pd.add_argument(
        "--password",
        required=True,
        metavar="STR",
        help="Current PDF password (str).",
    )
    pd.add_argument(
        "--out",
        metavar="PATH",
        help="Output PDF path (str; optional).",
    )
    pi = pdf_sub.add_parser("insert", help="Insert one PDF after a given page index in another.")
    pi.add_argument("--pdf1", required=True, metavar="PATH", help="Base PDF path (str).")
    pi.add_argument("--pdf2", required=True, metavar="PATH", help="PDF to insert (str).")
    pi.add_argument(
        "--after-page",
        type=int,
        required=True,
        metavar="N",
        help="0-based page index after which to insert (int).",
    )
    pi.add_argument("--out", required=True, metavar="PATH", help="Output PDF path (str).")
    pw = pdf_sub.add_parser("watermark", help="Apply a watermark PDF to each page of target PDF(s).")
    pw.add_argument(
        "--target",
        required=True,
        metavar="PATH",
        help="PDF file or directory of PDFs (str).",
    )
    pw.add_argument(
        "--watermark",
        required=True,
        metavar="PATH",
        help="Watermark PDF path (str).",
    )
    pw.add_argument(
        "--out-dir",
        default="watermarks",
        metavar="DIR",
        help="Output directory for watermarked PDFs (str; default: %(default)s).",
    )
    pt = pdf_sub.add_parser("to-images", help="Rasterize PDF page(s) to PNG image files.")
    pt.add_argument(
        "--input",
        required=True,
        metavar="PATH",
        help="Input PDF file or directory (str).",
    )
    pt.add_argument(
        "--out-dir",
        default="pdf_images",
        metavar="DIR",
        help="Output directory for PNG files (str; default: %(default)s).",
    )
    pt.add_argument(
        "--dpi",
        type=int,
        default=2,
        metavar="N",
        help="Rendering resolution factor passed to the backend (int; default: %(default)s).",
    )

    # docx
    p_dx = sub.add_parser("docx", help="Microsoft Word (.docx) utilities.")
    dx_sub = p_dx.add_subparsers(dest="dx_cmd", required=True)
    dr = dx_sub.add_parser("replace", help="Replace text in a .docx file.")
    dr.add_argument("--path", required=True, metavar="PATH", help="Input .docx path (str).")
    dr.add_argument("--old", required=True, metavar="STR", help="Text to find (str).")
    dr.add_argument("--new", required=True, metavar="STR", help="Replacement text (str).")
    dswap = dx_sub.add_parser("swap-dimensions", help="Swap page width and height.")
    dswap.add_argument("--input", required=True, metavar="PATH", help="Input .docx path (str).")
    dswap.add_argument("--output", required=True, metavar="PATH", help="Output .docx path (str).")
    dg = dx_sub.add_parser("extract-images", help="Extract embedded images from a .docx.")
    dg.add_argument("--input", required=True, metavar="PATH", help="Input .docx path (str).")
    dg.add_argument("--out-dir", required=True, metavar="DIR", help="Directory for extracted images (str).")

    # excel
    p_ex = sub.add_parser("excel", help="Excel spreadsheet utilities.")
    ex_sub = p_ex.add_subparsers(dest="ex_cmd", required=True)
    ef = ex_sub.add_parser("copy-format", help="Copy sheet formatting from a template workbook.")
    ef.add_argument("--source", required=True, metavar="PATH", help="Template .xlsx path (str).")
    ef.add_argument("--output", required=True, metavar="PATH", help="Output .xlsx path (str).")

    # image
    p_im = sub.add_parser("image", help="Image merge, padding, grid crop, and batch rename.")
    im_sub = p_im.add_subparsers(dest="im_cmd", required=True)
    imlr = im_sub.add_parser("merge-lr", help="Merge two images side by side (left | right).")
    imlr.add_argument("left", metavar="PATH", help="Left image path (str).")
    imlr.add_argument("right", metavar="PATH", help="Right image path (str).")
    imlr.add_argument(
        "--out",
        metavar="PATH",
        help="Output image path (str; optional; default is derived by the implementation).",
    )
    imud = im_sub.add_parser("merge-ud", help="Merge two images vertically (top over bottom).")
    imud.add_argument("top", metavar="PATH", help="Top image path (str).")
    imud.add_argument("bottom", metavar="PATH", help="Bottom image path (str).")
    imud.add_argument("--out", metavar="PATH", help="Output image path (str; optional).")
    imf = im_sub.add_parser("fill-square", help="Pad an image to a square canvas.")
    imf.add_argument("path", metavar="PATH", help="Input image path (str).")
    imf.add_argument("--out", metavar="PATH", help="Output image path (str; optional).")
    imc = im_sub.add_parser("cut-grid", help="Cut an image into a 3×3 grid of tiles.")
    imc.add_argument("path", metavar="PATH", help="Input image path (str).")
    imr = im_sub.add_parser("rename-webp", help="Rename images in a folder to WebP with EXIF-based names.")
    imr.add_argument("folder", metavar="DIR", help="Directory containing images (str).")
    imr.add_argument(
        "--remove-original",
        action="store_true",
        help="Delete original files after conversion (flag; no value).",
    )

    # qrcode
    p_qr = sub.add_parser("qrcode", help="QR code generation and decoding.")
    qr_sub = p_qr.add_subparsers(dest="qr_cmd", required=True)
    qg = qr_sub.add_parser("generate", help="Write QR code payload to a PNG file.")
    qg.add_argument("--text", required=True, metavar="STR", help="Data to encode (str).")
    qg.add_argument("--out", required=True, metavar="PATH", help="Output PNG path (str).")
    qd = qr_sub.add_parser("decode", help="Read QR payload from an image file.")
    qd.add_argument("image", metavar="PATH", help="Input image path (str).")

    # ipynb
    p_nb = sub.add_parser("ipynb", help="Jupyter notebook utilities.")
    nb_sub = p_nb.add_subparsers(dest="nb_cmd", required=True)
    nbm = nb_sub.add_parser("merge-dir", help="Merge all .ipynb files in a directory into one notebook.")
    nbm.add_argument("directory", metavar="DIR", help="Directory to scan (str).")
    nb2 = nb_sub.add_parser("to-markdown", help="Convert a .ipynb file to Markdown.")
    nb2.add_argument("notebook", metavar="PATH", help="Input .ipynb path (str).")
    nb2.add_argument(
        "--out-dir",
        default="",
        metavar="DIR",
        help="Output directory for the .md file (str; empty uses implementation default).",
    )

    # markdown
    p_md = sub.add_parser("md", help="Markdown conversion utilities.")
    md_sub = p_md.add_subparsers(dest="md_cmd", required=True)
    m1 = md_sub.add_parser("to-docx", help="Convert Markdown to Word (.docx).")
    m1.add_argument("md", metavar="PATH", help="Input .md path (str).")
    m1.add_argument("--out", required=True, metavar="PATH", help="Output .docx path (str).")
    m2 = md_sub.add_parser("to-html", help="Convert Markdown to HTML.")
    m2.add_argument("md", metavar="PATH", help="Input .md path (str).")
    m2.add_argument("--out", required=True, metavar="PATH", help="Output .html path (str).")
    m3 = md_sub.add_parser("tables-to-xlsx", help="Extract Markdown tables to an Excel workbook.")
    m3.add_argument("md", metavar="PATH", help="Input .md path (str).")
    m3.add_argument("--out", required=True, metavar="PATH", help="Output .xlsx path (str).")

    # stdlib
    p_st = sub.add_parser("stdlib", help="Analyze standard-library call usage in a Python tree.")
    st_sub = p_st.add_subparsers(dest="st_cmd", required=True)
    sta = st_sub.add_parser(
        "analyze",
        help=(
            "Scan .py files under a folder (skips .venv) and count stdlib calls. "
            "Use --json-string to return the same data as a single JSON text field."
        ),
    )
    sta.add_argument(
        "folder",
        metavar="DIR",
        help="Project root directory to scan recursively (str).",
    )
    sta.add_argument(
        "--json-string",
        action="store_true",
        help=(
            "If set, JSON envelope data uses key 'json' (str): a formatted JSON text blob of the analysis. "
            "If omitted, data uses key 'result' (object): nested dict module → attr → count (flag; no value)."
        ),
    )

    # install
    p_in = sub.add_parser("install-reqs", help="Install packages from a requirements file via pip.")
    p_in.add_argument(
        "--file",
        default="requirements.txt",
        metavar="PATH",
        help="Requirements file path (str; default: %(default)s).",
    )
    p_in.add_argument(
        "--failed-file",
        default="failed_requirements.txt",
        metavar="PATH",
        help="Where to record failed package lines (str; default: %(default)s).",
    )
    p_in.add_argument(
        "--retry",
        type=int,
        default=2,
        metavar="N",
        help="Retry count for failed installs (int; default: %(default)s).",
    )

    # scheduler (parse only)
    p_sc = sub.add_parser("scheduler", help="Scheduler helper utilities.")
    sc_sub = p_sc.add_subparsers(dest="sc_cmd", required=True)
    scp = sc_sub.add_parser("parse", help="Parse a schedule value and print the debug description.")
    scp.add_argument(
        "value",
        metavar="VAL",
        help=(
            "Schedule input: JSON value, integer seconds, or time string (str). "
            "Parsed with json.loads where applicable."
        ),
    )

    # email
    p_em = sub.add_parser("email", help="Send email via SMTP.")
    em_sub = p_em.add_subparsers(dest="em_cmd", required=True)
    es = em_sub.add_parser("send", help="Send one email with optional attachments.")
    es.add_argument("--sender", required=True, metavar="ADDR", help="SMTP login / From address (str).")
    es.add_argument("--password", required=True, metavar="STR", help="SMTP password (str).")
    es.add_argument("--recipient", required=True, metavar="ADDR", help="Recipient email address (str).")
    es.add_argument("--message", required=True, metavar="STR", help="Email body text (str).")
    es.add_argument("--subject", default="", metavar="STR", help="Subject line (str; default: empty).")
    es.add_argument(
        "--sender-show",
        metavar="STR",
        help="Display name for sender in headers (str; optional).",
    )
    es.add_argument(
        "--recipient-show",
        metavar="STR",
        help="Display name for recipient in headers (str; optional).",
    )
    es.add_argument(
        "--file",
        action="append",
        dest="files",
        metavar="PATH",
        help="Attachment file path (str; repeat for multiple files).",
    )
    es.add_argument("--image", metavar="PATH", help="Inline image path (str; optional).")

    return parser


def main_dispatch(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in argv
    if as_json:
        argv = [a for a in argv if a != "--json"]

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.version:
        from etool import get_version

        _emit(ok({"version": get_version()}), as_json=as_json)
        return 0

    if args.cmd is None:
        parser.print_help()
        return 1

    if args.cmd == "version":
        from etool import get_version

        _emit(ok({"version": get_version()}), as_json=as_json)
        return 0

    if args.cmd == "password":
        from etool import ManagerPassword

        if args.pw_cmd == "random":
            if args.length < 1:
                _emit(err(EtoolError(ErrorCode.VALIDATION_ERROR, "length must be >= 1")), as_json=as_json)
                return 1
            pwd = ManagerPassword.random_pwd(args.length)
            _emit(ok({"password": pwd}), as_json=as_json)
            return 0
        if args.pw_cmd == "convert-base":
            try:
                out = ManagerPassword.convert_base(args.value, args.from_base, args.to_base)
            except ValueError as e:
                _emit(err(EtoolError(ErrorCode.VALIDATION_ERROR, str(e))), as_json=as_json)
                return 1
            _emit(ok({"result": out}), as_json=as_json)
            return 0

    if args.cmd == "speed":
        from etool import ManagerSpeed

        if args.sp_cmd == "network":
            text = ManagerSpeed.network()
            _emit(ok({"report": text}), as_json=as_json)
            return 0
        if args.sp_cmd == "disk":
            text = ManagerSpeed.disk(file_size_mb=args.file_size_mb)
            _emit(ok({"report": text}), as_json=as_json)
            return 0
        if args.sp_cmd == "memory":
            text = ManagerSpeed.memory(size_mb=args.size_mb)
            _emit(ok({"report": text}), as_json=as_json)
            return 0

    if args.cmd == "pdf":
        from etool import ManagerPdf

        buf = io.StringIO()
        if args.pdf_cmd == "merge":
            with redirect_stdout(buf):
                ManagerPdf.merge_pdfs(list(args.files), args.out)
            _emit(ok({"merged": args.out, "log": buf.getvalue().strip()}), as_json=as_json)
            return 0
        if args.pdf_cmd == "split-pages":
            with redirect_stdout(buf):
                ManagerPdf.split_by_pages(args.pdf, args.pages)
            _emit(ok({"source": args.pdf, "log": buf.getvalue().strip()}), as_json=as_json)
            return 0
        if args.pdf_cmd == "split-num":
            with redirect_stdout(buf):
                ManagerPdf.split_by_num(args.pdf, args.parts)
            _emit(ok({"source": args.pdf, "log": buf.getvalue().strip()}), as_json=as_json)
            return 0
        if args.pdf_cmd == "encrypt":
            out = Path(args.out) if args.out else None
            with redirect_stdout(buf):
                ManagerPdf.encrypt_pdf(args.pdf, args.password, old_password=args.old_password, encrypted_filename=out)
            _emit(ok({"log": buf.getvalue().strip()}), as_json=as_json)
            return 0
        if args.pdf_cmd == "decrypt":
            out = Path(args.out) if args.out else None
            with redirect_stdout(buf):
                ManagerPdf.decrypt_pdf(args.pdf, args.password, decrypted_filename=out)
            _emit(ok({"log": buf.getvalue().strip()}), as_json=as_json)
            return 0
        if args.pdf_cmd == "insert":
            with redirect_stdout(buf):
                ManagerPdf.insert_pdf(
                    args.pdf1,
                    args.pdf2,
                    args.after_page,
                    args.out,
                )
            _emit(ok({"output": args.out, "log": buf.getvalue().strip()}), as_json=as_json)
            return 0
        if args.pdf_cmd == "watermark":
            with redirect_stdout(buf):
                ManagerPdf.create_watermarks(args.target, args.watermark, args.out_dir)
            _emit(ok({"log": buf.getvalue().strip()}), as_json=as_json)
            return 0
        if args.pdf_cmd == "to-images":
            with redirect_stdout(buf):
                ManagerPdf.pdf_to_images(args.input, args.out_dir, args.dpi)
            _emit(ok({"log": buf.getvalue().strip()}), as_json=as_json)
            return 0

    if args.cmd == "docx":
        from etool import ManagerDocx

        if args.dx_cmd == "replace":
            path = ManagerDocx.replace_words(args.path, args.old, args.new)
            _emit(ok({"path": path}), as_json=as_json)
            return 0
        if args.dx_cmd == "swap-dimensions":
            path = ManagerDocx.change_forward(args.input, args.output)
            _emit(ok({"path": path}), as_json=as_json)
            return 0
        if args.dx_cmd == "extract-images":
            path = ManagerDocx.get_pictures(args.input, args.out_dir)
            _emit(ok({"path": path}), as_json=as_json)
            return 0

    if args.cmd == "excel":
        from etool import ManagerExcel

        if args.ex_cmd == "copy-format":
            path = ManagerExcel.excel_format(args.source, args.output)
            _emit(ok({"path": path}), as_json=as_json)
            return 0

    if args.cmd == "image":
        from etool import ManagerImage

        if args.im_cmd == "merge-lr":
            path = ManagerImage.merge_LR([args.left, args.right], args.out)
            _emit(ok({"path": path}), as_json=as_json)
            return 0
        if args.im_cmd == "merge-ud":
            path = ManagerImage.merge_UD([args.top, args.bottom], args.out)
            _emit(ok({"path": path}), as_json=as_json)
            return 0
        if args.im_cmd == "fill-square":
            path = ManagerImage.fill_image(args.path, args.out)
            _emit(ok({"path": path}), as_json=as_json)
            return 0
        if args.im_cmd == "cut-grid":
            paths = ManagerImage.cut_image(args.path)
            _emit(ok({"paths": paths}), as_json=as_json)
            return 0
        if args.im_cmd == "rename-webp":
            info = ManagerImage.rename_images(args.folder, remove=args.remove_original)
            _emit(ok({"info": info}), as_json=as_json)
            return 0

    if args.cmd == "qrcode":
        from etool import ManagerQrcode

        if args.qr_cmd == "generate":
            path = ManagerQrcode.generate_qrcode(args.text, args.out)
            _emit(ok({"path": path}), as_json=as_json)
            return 0
        if args.qr_cmd == "decode":
            text = ManagerQrcode.decode_qrcode(args.image)
            _emit(ok({"text": text}), as_json=as_json)
            return 0

    if args.cmd == "ipynb":
        from etool import ManagerIpynb

        if args.nb_cmd == "merge-dir":
            path = ManagerIpynb.merge_notebooks(args.directory)
            if path is None:
                _emit(err(EtoolError(ErrorCode.RUNTIME_ERROR, "no notebooks found")), as_json=as_json)
                return 1
            _emit(ok({"path": path}), as_json=as_json)
            return 0
        if args.nb_cmd == "to-markdown":
            path = ManagerIpynb.convert_notebook_to_markdown(args.notebook, args.out_dir)
            _emit(ok({"path": path}), as_json=as_json)
            return 0

    if args.cmd == "md":
        from etool import ManagerMd

        if args.md_cmd == "to-docx":
            msg = ManagerMd.convert_md_to_docx(args.md, args.out)
            _emit(ok({"message": msg}), as_json=as_json)
            return 0
        if args.md_cmd == "to-html":
            msg = ManagerMd.convert_md_to_html(args.md, args.out)
            _emit(ok({"message": msg}), as_json=as_json)
            return 0
        if args.md_cmd == "tables-to-xlsx":
            msg = ManagerMd.extract_tables_to_excel(args.md, args.out)
            _emit(ok({"message": msg}), as_json=as_json)
            return 0

    if args.cmd == "stdlib":
        from etool import ManagerStdlibUsage, analyze_stdlib_usage

        if args.st_cmd == "analyze":
            if args.json_string:
                s = ManagerStdlibUsage.analyze_to_json(args.folder)
                _emit(ok({"json": s}), as_json=as_json)
            else:
                data = analyze_stdlib_usage(args.folder)
                _emit(ok({"result": data}), as_json=as_json)
            return 0

    if args.cmd == "install-reqs":
        from etool import ManagerInstall

        ok_install = ManagerInstall.install(
            requirements_file=args.file,
            failed_file=args.failed_file,
            retry=args.retry,
        )
        if not ok_install:
            _emit(err(EtoolError(ErrorCode.RUNTIME_ERROR, "some packages failed to install")), as_json=as_json)
            return 1
        _emit(ok({"success": True}), as_json=as_json)
        return 0

    if args.cmd == "scheduler":
        from etool import ManagerScheduler

        if args.sc_cmd == "parse":
            val = _parse_cli_value(args.value)
            buf = io.StringIO()
            with redirect_stdout(buf):
                ManagerScheduler.parse_schedule_time(val)
            _emit(ok({"log": buf.getvalue().strip()}), as_json=as_json)
            return 0

    if args.cmd == "email":
        from etool import ManagerEmail

        if args.em_cmd == "send":
            r = ManagerEmail.send_email(
                sender=args.sender,
                password=args.password,
                message=args.message,
                recipient=args.recipient,
                subject=args.subject or None,
                sender_show=args.sender_show,
                recipient_show=args.recipient_show,
                file_path=args.files,
                image_path=args.image,
            )
            _emit(ok({"result": r}), as_json=as_json)
            return 0

    parser.print_help()
    return 1


def main(argv: list[str] | None = None) -> int:
    return main_dispatch(argv)
