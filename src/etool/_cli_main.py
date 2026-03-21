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
    parser = argparse.ArgumentParser(prog="etool", description="etool 2.x command-line interface")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("version", help="show package version")

    # password
    p_pw = sub.add_parser("password", help="password utilities")
    pw_sub = p_pw.add_subparsers(dest="pw_cmd", required=True)
    p_rand = pw_sub.add_parser("random", help="random password")
    p_rand.add_argument("--length", type=int, default=16)
    p_cb = pw_sub.add_parser("convert-base", help="convert number between bases")
    p_cb.add_argument("value")
    p_cb.add_argument("--from-base", type=int, required=True)
    p_cb.add_argument("--to-base", type=int, required=True)

    # speed
    p_sp = sub.add_parser("speed", help="benchmarks (network / disk / memory)")
    sp_sub = p_sp.add_subparsers(dest="sp_cmd", required=True)
    sp_sub.add_parser("network", help="speedtest-cli network test (slow, needs internet)")
    p_disk = sp_sub.add_parser("disk", help="disk read/write benchmark")
    p_disk.add_argument("--file-size-mb", type=int, default=20)
    p_mem = sp_sub.add_parser("memory", help="memory throughput (stdlib)")
    p_mem.add_argument("--size-mb", type=int, default=64)

    # pdf
    p_pdf = sub.add_parser("pdf", help="PDF operations (pypdf + PyMuPDF)")
    pdf_sub = p_pdf.add_subparsers(dest="pdf_cmd", required=True)
    pm = pdf_sub.add_parser("merge", help="merge PDFs")
    pm.add_argument("--out", required=True, help="output merged PDF path")
    pm.add_argument("files", nargs="+", help="input PDF files")
    ps = pdf_sub.add_parser("split-pages", help="split by page count per chunk")
    ps.add_argument("pdf")
    ps.add_argument("--pages", type=int, required=True)
    pn = pdf_sub.add_parser("split-num", help="split into N parts")
    pn.add_argument("pdf")
    pn.add_argument("--parts", type=int, required=True)
    pe = pdf_sub.add_parser("encrypt", help="encrypt PDF")
    pe.add_argument("pdf")
    pe.add_argument("--password", required=True)
    pe.add_argument("--old-password")
    pe.add_argument("--out")
    pd = pdf_sub.add_parser("decrypt", help="decrypt PDF")
    pd.add_argument("pdf")
    pd.add_argument("--password", required=True)
    pd.add_argument("--out")
    pi = pdf_sub.add_parser("insert", help="insert pdf2 after page index in pdf1")
    pi.add_argument("--pdf1", required=True)
    pi.add_argument("--pdf2", required=True)
    pi.add_argument("--after-page", type=int, required=True)
    pi.add_argument("--out", required=True)
    pw = pdf_sub.add_parser("watermark", help="apply watermark PDF to pages")
    pw.add_argument("--target", required=True, help="PDF file or directory of PDFs")
    pw.add_argument("--watermark", required=True, help="watermark PDF path")
    pw.add_argument("--out-dir", default="watermarks", help="output directory")
    pt = pdf_sub.add_parser("to-images", help="rasterize PDF(s) to PNG")
    pt.add_argument("--input", required=True, help="PDF file or directory")
    pt.add_argument("--out-dir", default="pdf_images")
    pt.add_argument("--dpi", type=int, default=2)

    # docx
    p_dx = sub.add_parser("docx", help="Word documents")
    dx_sub = p_dx.add_subparsers(dest="dx_cmd", required=True)
    dr = dx_sub.add_parser("replace", help="replace text in docx")
    dr.add_argument("--path", required=True)
    dr.add_argument("--old", required=True)
    dr.add_argument("--new", required=True)
    dswap = dx_sub.add_parser("swap-dimensions", help="swap page width/height")
    dswap.add_argument("--input", required=True)
    dswap.add_argument("--output", required=True)
    dg = dx_sub.add_parser("extract-images", help="extract embedded images")
    dg.add_argument("--input", required=True)
    dg.add_argument("--out-dir", required=True)

    # excel
    p_ex = sub.add_parser("excel", help="Excel")
    ex_sub = p_ex.add_subparsers(dest="ex_cmd", required=True)
    ef = ex_sub.add_parser("copy-format", help="copy sheet style from template")
    ef.add_argument("--source", required=True)
    ef.add_argument("--output", required=True)

    # image
    p_im = sub.add_parser("image", help="image merge / grid / rename")
    im_sub = p_im.add_subparsers(dest="im_cmd", required=True)
    imlr = im_sub.add_parser("merge-lr", help="merge two images left-right")
    imlr.add_argument("left")
    imlr.add_argument("right")
    imlr.add_argument("--out")
    imud = im_sub.add_parser("merge-ud", help="merge two images top-bottom")
    imud.add_argument("top")
    imud.add_argument("bottom")
    imud.add_argument("--out")
    imf = im_sub.add_parser("fill-square", help="pad image to square")
    imf.add_argument("path")
    imf.add_argument("--out")
    imc = im_sub.add_parser("cut-grid", help="3x3 grid crop")
    imc.add_argument("path")
    imr = im_sub.add_parser("rename-webp", help="rename images in folder to webp + EXIF names")
    imr.add_argument("folder")
    imr.add_argument("--remove-original", action="store_true")

    # qrcode
    p_qr = sub.add_parser("qrcode", help="QR code")
    qr_sub = p_qr.add_subparsers(dest="qr_cmd", required=True)
    qg = qr_sub.add_parser("generate", help="generate QR PNG")
    qg.add_argument("--text", required=True)
    qg.add_argument("--out", required=True)
    qd = qr_sub.add_parser("decode", help="decode QR from image file")
    qd.add_argument("image")

    # ipynb
    p_nb = sub.add_parser("ipynb", help="Jupyter notebooks")
    nb_sub = p_nb.add_subparsers(dest="nb_cmd", required=True)
    nbm = nb_sub.add_parser("merge-dir", help="merge all .ipynb in directory")
    nbm.add_argument("directory")
    nb2 = nb_sub.add_parser("to-markdown", help="convert .ipynb to .md")
    nb2.add_argument("notebook")
    nb2.add_argument("--out-dir", default="")

    # markdown
    p_md = sub.add_parser("md", help="Markdown conversions")
    md_sub = p_md.add_subparsers(dest="md_cmd", required=True)
    m1 = md_sub.add_parser("to-docx")
    m1.add_argument("md")
    m1.add_argument("--out", required=True)
    m2 = md_sub.add_parser("to-html")
    m2.add_argument("md")
    m2.add_argument("--out", required=True)
    m3 = md_sub.add_parser("tables-to-xlsx")
    m3.add_argument("md")
    m3.add_argument("--out", required=True)

    # stdlib
    p_st = sub.add_parser("stdlib", help="stdlib usage analysis")
    st_sub = p_st.add_subparsers(dest="st_cmd", required=True)
    sta = st_sub.add_parser("analyze", help="analyze Python project folder")
    sta.add_argument("folder")
    stj = st_sub.add_parser("analyze-json", help="same as analyze, JSON string output")
    stj.add_argument("folder")

    # install
    p_in = sub.add_parser("install-reqs", help="pip install from requirements file")
    p_in.add_argument("--file", default="requirements.txt")
    p_in.add_argument("--failed-file", default="failed_requirements.txt")
    p_in.add_argument("--retry", type=int, default=2)

    # scheduler (parse only)
    p_sc = sub.add_parser("scheduler", help="scheduler helpers")
    sc_sub = p_sc.add_subparsers(dest="sc_cmd", required=True)
    scp = sc_sub.add_parser("parse", help="print parsed schedule description (debug)")
    scp.add_argument("value", help="JSON, integer seconds, or time string")

    # email
    p_em = sub.add_parser("email", help="send email (SMTP)")
    em_sub = p_em.add_subparsers(dest="em_cmd", required=True)
    es = em_sub.add_parser("send")
    es.add_argument("--sender", required=True)
    es.add_argument("--password", required=True)
    es.add_argument("--recipient", required=True)
    es.add_argument("--message", required=True)
    es.add_argument("--subject", default="")
    es.add_argument("--sender-show")
    es.add_argument("--recipient-show")
    es.add_argument("--file", action="append", dest="files")
    es.add_argument("--image")

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
            data = analyze_stdlib_usage(args.folder)
            _emit(ok({"result": data}), as_json=as_json)
            return 0
        if args.st_cmd == "analyze-json":
            s = ManagerStdlibUsage.analyze_to_json(args.folder)
            _emit(ok({"json": s}), as_json=as_json)
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
