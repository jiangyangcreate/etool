from PyPDF2 import PdfWriter, PdfReader, PdfMerger
from pathlib import Path
import os


class PdfManager:

    '''
    PDF 文件管理器，提供加密、解密、分割、合并等功能
    
    manager = PdfManager()
    manager.encrypt_pdf(Path('ex1.pdf'), new_password='leafage')
    manager.decrypt_pdf(Path('ex1123_encrypted.pdf'), password='leafage')
    manager.split_by_pages(Path('ex1.pdf'), pages_per_split=5)
    manager.split_by_num(Path('A类小作文范文52篇（24年新版）.pdf'), num_splits=122)
    manager.merge_pdfs(
        filenames=[Path('ex1.pdf'), Path('ex2.pdf')],
        merged_name=Path('merged.pdf')
    )
    manager.insert_pdf(
        pdf1=Path('ex1.pdf'),
        pdf2=Path('ex2.pdf'),
        insert_page_num=10,
        merged_name=Path('pdf12.pdf')
    )
    manager.auto_merge(Path("PDF"))
    '''


    def __init__(self):
        pass

    @staticmethod
    def open_pdf_file(filename: Path, mode: str = "rb"):
        """使用上下文管理器打开PDF文件"""
        return filename.open(mode)

    @staticmethod
    def get_reader(filename: Path, password: str = None) -> PdfReader:
        """获取PDF阅读器实例"""
        try:
            pdf_reader = PdfReader(filename, strict=False)
            if pdf_reader.is_encrypted:
                if password is None or not pdf_reader.decrypt(password):
                    print(f"{filename} 文件被加密或密码不正确！")
                    return None
            return pdf_reader
        except Exception as err:
            print(f"文件打开失败！{err}")
            return None

    @staticmethod
    def write_pdf(writer: PdfWriter, filename: Path):
        """写入PDF文件"""
        with filename.open("wb") as output_file:
            writer.write(output_file)

    def encrypt_pdf(
        self,
        filename: Path,
        new_password: str,
        old_password: str = None,
        encrypted_filename: Path = None,
    ):
        """对PDF文件进行加密"""
        pdf_reader = self.get_reader(filename, old_password)
        if pdf_reader is None:
            return

        pdf_writer = PdfWriter()
        pdf_writer.append_pages_from_reader(pdf_reader)
        pdf_writer.encrypt(new_password)

        if encrypted_filename is None:
            encrypted_filename = filename.with_name(f"{filename.stem}_encrypted.pdf")

        self.write_pdf(pdf_writer, encrypted_filename)
        print(f"加密后的文件保存为: {encrypted_filename}")

    def decrypt_pdf(
        self,
        filename: Path,
        password: str,
        decrypted_filename: Path = None,
    ):
        """将加密的PDF文件解密"""
        pdf_reader = self.get_reader(filename, password)
        if pdf_reader is None:
            return

        if not pdf_reader.is_encrypted:
            print("文件没有被加密，无需操作！")
            return

        pdf_writer = PdfWriter()
        pdf_writer.append_pages_from_reader(pdf_reader)

        if decrypted_filename is None:
            decrypted_filename = filename.with_name(f"{filename.stem}_decrypted.pdf")

        self.write_pdf(pdf_writer, decrypted_filename)
        print(f"解密后的文件保存为: {decrypted_filename}")

    def split_by_pages(
        self,
        filename: Path,
        pages_per_split: int,
        password: str = None,
    ):
        """将PDF文件按照页数进行分割"""
        pdf_reader = self.get_reader(filename, password)
        if pdf_reader is None:
            return

        total_pages = len(pdf_reader.pages)
        if pages_per_split < 1:
            print("每份文件必须至少包含1页！")
            return

        num_splits = (total_pages + pages_per_split - 1) // pages_per_split
        print(f"PDF 文件将被分为 {num_splits} 份，每份最多 {pages_per_split} 页。")

        for split_num in range(num_splits):
            pdf_writer = PdfWriter()
            start = split_num * pages_per_split
            end = min(start + pages_per_split, total_pages)
            for page in range(start, end):
                pdf_writer.add_page(pdf_reader.pages[page])

            split_filename = filename.with_name(f"{filename.stem}_part{split_num + 1}.pdf")
            self.write_pdf(pdf_writer, split_filename)
            print(f"生成: {split_filename}")

    def split_by_num(
        self,
        filename: Path,
        num_splits: int,
        password: str = None,
    ):
        """将PDF文件分为指定份数"""
        try:
            pdf_reader = self.get_reader(filename, password)
            if pdf_reader is None:
                return

            total_pages = len(pdf_reader.pages)
            if num_splits < 2:
                print("份数不能小于2！")
                return
            if total_pages < num_splits:
                print(f"份数({num_splits})不应该大于PDF总页数({total_pages})！")
                return

            pages_per_split = total_pages // num_splits
            extra_pages = total_pages % num_splits
            print(
                f"PDF 共有 {total_pages} 页，将分为 {num_splits} 份，每份基本有 {pages_per_split} 页。"
            )

            start = 0
            for split_num in range(1, num_splits + 1):
                pdf_writer = PdfWriter()
                # 分配多余的页面到前几个分割
                end = start + pages_per_split + (1 if split_num <= extra_pages else 0)
                for page in range(start, end):
                    pdf_writer.add_page(pdf_reader.pages[page])

                split_filename = filename.with_name(f"{filename.stem}_part{split_num}.pdf")
                self.write_pdf(pdf_writer, split_filename)
                print(f"生成: {split_filename}")
                start = end

        except Exception as e:
            print(f"分割PDF时发生错误: {e}")

    def merge_pdfs(
        self,
        filenames: list,
        merged_name: Path,
        passwords: list = None,
    ):
        """将多个PDF文件合并为一个"""
        if passwords and len(passwords) != len(filenames):
            print("密码列表长度必须与文件列表长度一致！")
            return

        merger = PdfMerger()

        for idx, file in enumerate(filenames):
            password = passwords[idx] if passwords else None
            pdf_reader = self.get_reader(file, password)
            if not pdf_reader:
                print(f"跳过文件: {file}")
                continue
            merger.append(pdf_reader)
            print(f"已合并: {file}")

        with merged_name.open("wb") as f_out:
            merger.write(f_out)
        print(f"合并后的文件保存为: {merged_name}")

    def insert_pdf(
        self,
        pdf1: Path,
        pdf2: Path,
        insert_page_num: int,
        merged_name: Path,
        password1: str = None,
        password2: str = None,
    ):
        """将pdf2插入到pdf1的指定页后"""
        pdf1_reader = self.get_reader(pdf1, password1)
        pdf2_reader = self.get_reader(pdf2, password2)
        if not pdf1_reader or not pdf2_reader:
            return

        total_pages_pdf1 = len(pdf1_reader.pages)
        if not (0 <= insert_page_num <= total_pages_pdf1):
            print(
                f"插入位置异常，插入页数为：{insert_page_num}，PDF1文件共有：{total_pages_pdf1} 页！"
            )
            return

        merger = PdfMerger()
        with PdfManager.open_pdf_file(pdf1, "rb") as f_pdf1:
            merger.append(f_pdf1, pages=(0, insert_page_num))
        with PdfManager.open_pdf_file(pdf2, "rb") as f_pdf2:
            merger.append(f_pdf2)
        with PdfManager.open_pdf_file(pdf1, "rb") as f_pdf1:
            merger.append(f_pdf1, pages=(insert_page_num, len(pdf1_reader.pages)))

        with merged_name.open("wb") as f_out:
            merger.write(f_out)
        print(f"插入后的文件保存为: {merged_name}")

    def auto_merge(self, path: Path, result_name: Path = None):
        """自动合并指定目录下的所有PDF文件"""
        if not path.is_dir():
            print(f"{path} 不是一个有效的目录！")
            return

        merged_filename = result_name or path / "合并.pdf"
        merger = PdfMerger()

        pdf_files = sorted(path.glob("*.pdf"))
        for pdf in pdf_files:
            pdf_reader = self.get_reader(pdf)
            if pdf_reader is None:
                print(f"忽略加密文件或无法读取的文件: {pdf}")
                continue
            merger.append(pdf_reader, import_outline=True)
            print(f"已合并: {pdf}")

        with merged_filename.open("wb") as f_out:
            merger.write(f_out)
        print(f"\n合并完成，文件保存为: {merged_filename}")
