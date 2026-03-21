"""PDF utilities using pypdf and PyMuPDF only (no Windows COM)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter


class ManagerPdf:
    """PDF merge/split/encrypt/decrypt/watermark/rasterize (cross-platform)."""

    @staticmethod
    def create_watermarks(
        pdf_file_path: str,
        watermark_file_path: str,
        save_path: str = "watermarks",
    ) -> None:
        """Add watermark PDF to each page of target PDF(s)."""

        def create_watermark(input_pdf: str, watermark: str, output_pdf: str) -> None:
            watermark_obj = PdfReader(watermark, strict=False)
            watermark_page = watermark_obj.pages[0]

            pdf_reader = PdfReader(input_pdf, strict=False)
            pdf_writer = PdfWriter()

            for page in pdf_reader.pages:
                page.merge_page(watermark_page)
                pdf_writer.add_page(page)

            with open(output_pdf, "wb") as out:
                pdf_writer.write(out)

        if os.path.isfile(pdf_file_path):
            os.makedirs(save_path, exist_ok=True)
            create_watermark(
                pdf_file_path,
                watermark_file_path,
                os.path.join(save_path, os.path.basename(pdf_file_path)),
            )
        else:
            for pdf_file in os.listdir(pdf_file_path):
                if pdf_file.endswith(".pdf"):
                    input_pdf = os.path.join(pdf_file_path, pdf_file)
                    os.makedirs(save_path, exist_ok=True)
                    create_watermark(
                        input_pdf,
                        watermark_file_path,
                        os.path.join(save_path, os.path.basename(pdf_file)),
                    )

    @staticmethod
    def open_pdf_file(filename: Path, mode: str = "rb"):
        return filename.open(mode)

    @staticmethod
    def get_reader(filename: Path, password: str | None = None) -> PdfReader | None:
        try:
            pdf_reader = PdfReader(filename, strict=False)
            if pdf_reader.is_encrypted:
                if password is None or not pdf_reader.decrypt(password):
                    print(f"{filename} is encrypted or the password is incorrect!")
                    return None
            return pdf_reader
        except Exception as err:
            print(f"failed to open the file: {err}")
            return None

    @staticmethod
    def write_pdf(writer: PdfWriter, filename: Path) -> None:
        with filename.open("wb") as output_file:
            writer.write(output_file)

    @staticmethod
    def encrypt_pdf(
        filename: str,
        new_password: str,
        old_password: str | None = None,
        encrypted_filename: Path | None = None,
    ) -> None:
        pdf_reader = ManagerPdf.get_reader(Path(filename), old_password)
        if pdf_reader is None:
            return

        pdf_writer = PdfWriter()
        pdf_writer.append_pages_from_reader(pdf_reader)
        pdf_writer.encrypt(new_password)

        if encrypted_filename is None:
            encrypted_filename = Path(filename).with_name(f"{Path(filename).stem}_encrypted.pdf")

        ManagerPdf.write_pdf(pdf_writer, encrypted_filename)
        print(f"encrypted file saved as: {encrypted_filename}")

    @staticmethod
    def decrypt_pdf(
        filename: str,
        password: str,
        decrypted_filename: Path | None = None,
    ) -> None:
        pdf_reader = ManagerPdf.get_reader(Path(filename), password)
        if pdf_reader is None:
            return

        if not pdf_reader.is_encrypted:
            print("the file is not encrypted, no operation needed!")
            return

        pdf_writer = PdfWriter()
        pdf_writer.append_pages_from_reader(pdf_reader)

        if decrypted_filename is None:
            decrypted_filename = Path(filename).with_name(f"{Path(filename).stem}_decrypted.pdf")

        ManagerPdf.write_pdf(pdf_writer, decrypted_filename)
        print(f"decrypted file saved as: {decrypted_filename}")

    @staticmethod
    def split_by_pages(
        filename: str | Path,
        pages_per_split: int,
        password: str | None = None,
    ) -> None:
        if isinstance(filename, str):
            filename = Path(filename)
        pdf_reader = ManagerPdf.get_reader(filename, password)

        if pdf_reader is None:
            return

        total_pages = len(pdf_reader.pages)
        if pages_per_split < 1:
            print("each file must contain at least 1 page!")
            return

        num_splits = (total_pages + pages_per_split - 1) // pages_per_split
        print(
            f"the PDF file will be split into {num_splits} parts, each part contains at most {pages_per_split} pages."
        )

        for split_num in range(num_splits):
            pdf_writer = PdfWriter()
            start = split_num * pages_per_split
            end = min(start + pages_per_split, total_pages)
            for page in range(start, end):
                pdf_writer.add_page(pdf_reader.pages[page])

            split_filename = filename.with_name(f"{filename.stem}_part_by_page{split_num + 1}.pdf")
            ManagerPdf.write_pdf(pdf_writer, split_filename)
            print(f"generated: {split_filename}")

    @staticmethod
    def split_by_num(
        filename: str | Path,
        num_splits: int,
        password: str | None = None,
    ) -> None:
        if isinstance(filename, str):
            filename = Path(filename)

        try:
            pdf_reader = ManagerPdf.get_reader(filename, password)
            if pdf_reader is None:
                return

            total_pages = len(pdf_reader.pages)
            if num_splits < 2:
                print("the number of parts cannot be less than 2!")
                return
            if total_pages < num_splits:
                print(
                    f"the number of parts({num_splits}) should not be greater than the total number of pages({total_pages})!"
                )
                return

            pages_per_split = total_pages // num_splits
            extra_pages = total_pages % num_splits
            print(
                f"the PDF has {total_pages} pages, will be split into {num_splits} parts, each part contains at most {pages_per_split} pages."
            )

            start = 0
            for split_num in range(1, num_splits + 1):
                pdf_writer = PdfWriter()
                end = start + pages_per_split + (1 if split_num <= extra_pages else 0)
                for page in range(start, end):
                    pdf_writer.add_page(pdf_reader.pages[page])

                split_filename = filename.with_name(f"{filename.stem}_part_by_num{split_num}.pdf")
                ManagerPdf.write_pdf(pdf_writer, split_filename)
                print(f"generated: {split_filename}")
                start = end

        except Exception as e:
            print(f"error occurred when splitting the PDF: {e}")

    @staticmethod
    def merge_pdfs(
        filenames: str | list[str],
        merged_name: str,
        passwords: list | None = None,
    ) -> None:
        if passwords and len(passwords) != len(filenames):
            print("the length of the password list must be the same as the length of the file list!")
            return

        writer = PdfWriter()

        if isinstance(filenames, str):
            if os.path.isfile(filenames):
                filenames = [filenames]
            elif os.path.isdir(filenames):
                filenames = [str(path) for path in Path(filenames).rglob("*.pdf")]

        for idx, file in enumerate(filenames):
            password = passwords[idx] if passwords else None
            pdf_reader = ManagerPdf.get_reader(Path(file), password)
            if not pdf_reader:
                print(f"skip file: {file}")
                continue
            for page in pdf_reader.pages:
                writer.add_page(page)

            print(f"merged: {file}")

        with Path(merged_name).open("wb") as f_out:
            writer.write(f_out)

        print(f"merged file saved as: {merged_name}")

    @staticmethod
    def insert_pdf(
        pdf1: str | Path,
        pdf2: str | Path,
        insert_page_num: int,
        merged_name: str | Path,
        password1: str | None = None,
        password2: str | None = None,
    ) -> None:
        if isinstance(pdf1, str):
            pdf1 = Path(pdf1)
        if isinstance(pdf2, str):
            pdf2 = Path(pdf2)
        if isinstance(merged_name, str):
            merged_name = Path(merged_name)

        pdf1_reader = ManagerPdf.get_reader(pdf1, password1)
        pdf2_reader = ManagerPdf.get_reader(pdf2, password2)
        if not pdf1_reader or not pdf2_reader:
            return

        total_pages_pdf1 = len(pdf1_reader.pages)
        if not (0 <= insert_page_num <= total_pages_pdf1):
            print(
                f"the insertion position is abnormal, the insertion page number is: {insert_page_num}, the PDF1 file has: {total_pages_pdf1} pages!"
            )
            return

        writer = PdfWriter()
        with ManagerPdf.open_pdf_file(pdf1, "rb") as f_pdf1:
            writer.append(f_pdf1, pages=(0, insert_page_num))
        with ManagerPdf.open_pdf_file(pdf2, "rb") as f_pdf2:
            writer.append(f_pdf2)
        with ManagerPdf.open_pdf_file(pdf1, "rb") as f_pdf1:
            writer.append(f_pdf1, pages=(insert_page_num, len(pdf1_reader.pages)))

        with merged_name.open("wb") as f_out:
            writer.write(f_out)
        print(f"inserted file saved as: {merged_name}")

    @staticmethod
    def pdf_to_images(
        pathname: str,
        output_dir: str = "pdf_images",
        dpi: int = 2,
    ) -> None:
        """Rasterize PDF pages to PNG using PyMuPDF."""
        if sys.platform == "win32":
            os.environ.setdefault("PYTHONIOENCODING", "utf-8")

        pathname = Path(pathname)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if pathname.is_file():
            if pathname.suffix.lower() == ".pdf":
                pdf_files = [pathname]
            else:
                print(f"file {pathname} is not a valid PDF file!")
                return
        elif pathname.is_dir():
            pdf_files = list(pathname.glob("*.pdf"))
            if not pdf_files:
                print(f"no PDF files found in folder: {pathname}")
                return
        else:
            print(f"path {pathname} does not exist!")
            return

        print(f"found {len(pdf_files)} PDF file(s)")
        print(f"output directory: {output_dir}")

        success_count = 0
        fail_count = 0

        for pdf_file in pdf_files:
            try:
                print(f"\n{'=' * 60}")
                print(f"processing: {pdf_file.name}")
                print(f"{'=' * 60}")

                doc = fitz.open(pdf_file)

                for page_num in range(len(doc)):
                    page = doc[page_num]

                    mat = fitz.Matrix(dpi, dpi)
                    pix = page.get_pixmap(matrix=mat)

                    if len(doc) == 1:
                        output_path = output_dir / f"{pdf_file.stem}.png"
                    else:
                        output_path = output_dir / f"{pdf_file.stem}_page_{page_num + 1}.png"

                    pix.save(str(output_path))
                    print(f"[OK] saved page {page_num + 1}/{len(doc)}: {output_path.name}")

                doc.close()
                success_count += 1

            except Exception as e:
                print(f"[ERROR] converting {pdf_file.name}: {e}")
                fail_count += 1

        print(f"\n{'=' * 60}")
        print("conversion summary")
        print(f"{'=' * 60}")
        print(f"total files: {len(pdf_files)}")
        print(f"successful: {success_count}")
        print(f"failed: {fail_count}")
        print(f"output location: {output_dir.resolve()}")
