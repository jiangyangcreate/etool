from PyPDF2 import PdfWriter, PdfReader, PdfMerger, PdfFileReader, PdfFileWriter
from pathlib import Path
import os
from pathlib import Path
from win32com.client import Dispatch, gencache, DispatchEx
import win32com.client
import time
import ctypes
from ctypes import wintypes
from pdf2docx import Converter
# 定义类


class PDFConverter:
    def __init__(self, pathname,outpath):
        self._handle_postfix = ['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx']
        self._filename_list = list()
        self._export_folder = os.path.join(os.path.abspath('.'), outpath)
        if not os.path.exists(self._export_folder):
            os.mkdir(self._export_folder)
        self._enumerate_filename(pathname)


    def _enumerate_filename(self, pathname):
        full_pathname = os.path.abspath(pathname)
        if os.path.isfile(full_pathname):
            if self._is_legal_postfix(full_pathname):
                self._filename_list.append(full_pathname)
            else:
                raise TypeError('文件 {} 后缀名不合法！仅支持如下文件类型：{}。'.format(
                    pathname, '、'.join(self._handle_postfix)))
        elif os.path.isdir(full_pathname):
            for relpath, _, files in os.walk(full_pathname):
                for name in files:
                    filename = os.path.join(full_pathname, relpath, name)
                    if self._is_legal_postfix(filename):
                        self._filename_list.append(os.path.join(filename))
        else:
            raise TypeError('文件/文件夹 {} 不存在或不合法！'.format(pathname))

    def _is_legal_postfix(self, filename):
        return filename.split('.')[-1].lower() in self._handle_postfix and not os.path.basename(filename).startswith('~')

    def run_conver(self):
        '''
        进行批量处理，根据后缀名调用函数执行转换
        '''
        print('需要转换的文件数：', len(self._filename_list))
        for filename in self._filename_list:
            postfix = filename.split('.')[-1].lower()
            funcCall = getattr(self, postfix)
            print('原文件：', filename)
            funcCall(filename)
        print('转换完成！')

    def get_short_path_name(self, long_path):
        """
        将给定绝对路径转换为短路径（DOS 8.3 格式）。
        若转换失败或未启用短路径，则仍然返回原路径。
        """
        GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
        GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        GetShortPathNameW.restype = wintypes.DWORD
        
        buffer_size = 260
        output_buf = ctypes.create_unicode_buffer(buffer_size)
        result = GetShortPathNameW(long_path, output_buf, buffer_size)
        
        if result > 0 and result < buffer_size:
            return output_buf.value
        else:
            return long_path

    def doc(self, filename):
        '''
        doc 和 docx 文件转换
        '''
        name = os.path.basename(filename).split('.')[0] + '.pdf'
        word = None
        doc = None
        
        try:
            # 初始化 Word COM 对象
            gencache.EnsureModule('{00020905-0000-0000-C000-000000000046}', 0, 8, 4)
            word = DispatchEx('Word.Application')
            word.Visible = 0
            word.DisplayAlerts = 0
            
            # 转换文件路径为绝对路径短路径
            abs_path = os.path.abspath(filename)
            abs_short_path = self.get_short_path_name(abs_path)

            pdf_file = os.path.join(self._export_folder, name)
            pdf_short_path = self.get_short_path_name(pdf_file)

            # 添加重试机制
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    doc = word.Documents.Open(
                        abs_short_path,
                        ReadOnly=True,
                        Visible=False,
                        ConfirmConversions=False
                    )
                    # 保存到短路径
                    doc.SaveAs(pdf_short_path, FileFormat=17)
                    print(f'成功转换: {filename}')
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        print(f"在 {max_retries} 次尝试后仍然失败: {filename}")
                        raise
                    print(f"第 {retry_count} 次尝试失败，准备重试...")
                    time.sleep(2)  # 等待2秒后重试
                    
        except Exception as e:
            print(f"转换文件失败 {filename}: {str(e)}")
            raise
        
        finally:
            # 确保清理所有 COM 对象
            if doc:
                try:
                    doc.Close(SaveChanges=False)
                except:
                    pass
            
            if word:
                try:
                    word.Quit()
                except:
                    pass
                
            # 强制清理 COM 对象
            if doc:
                del doc
            if word:
                del word
                
            # 强制垃圾回收
            import gc
            gc.collect()

    def docx(self, filename):
        self.doc(filename)

    def xls(self, filename):
        '''
        xls 和 xlsx 文件转换，并设置为缩放到单页（横向）
        '''
        name = os.path.basename(filename).split('.')[0] + '.pdf'
        exportfile = os.path.join(self._export_folder, name)
        xlApp = DispatchEx("Excel.Application")
        xlApp.Visible = False
        xlApp.DisplayAlerts = 0
        books = xlApp.Workbooks.Open(filename, False)

        for sheet in books.Worksheets:
            # 先禁用 Zoom，以便适应多页缩放生效
            sheet.PageSetup.Zoom = False
            
            # 将内容限制在1页宽、1页高
            sheet.PageSetup.FitToPagesWide = 1
            sheet.PageSetup.FitToPagesTall = 1
            
            # 设置横向打印
            # xlOrientationPortrait = 1, xlOrientationLandscape = 2
            sheet.PageSetup.Orientation = 2
            
            # 可根据需要设置页边距
            sheet.PageSetup.LeftMargin = 0
            sheet.PageSetup.RightMargin = 0
            sheet.PageSetup.TopMargin = 0
            sheet.PageSetup.BottomMargin = 0
            
            # 根据需要设置纸张大小，比如 A4
            # from win32com.client import constants
            # sheet.PageSetup.PaperSize = constants.xlPaperA4

        books.ExportAsFixedFormat(0, exportfile)
        books.Close(False)
        print('保存 PDF 文件：', exportfile)
        xlApp.Quit()

    def xlsx(self, filename):
        self.xls(filename)

    def ppt(self,filename):
        """
        PPT文件导出为pdf格式
        :param filename: PPT文件的名称
        :param output_filename: 导出的pdf文件的名称
        :return:
        """
        name = os.path.basename(filename).split('.')[0] + '.pdf'
        exportfile = os.path.join(self._export_folder, name)
        ppt_app = win32com.client.Dispatch('PowerPoint.Application')
        ppt = ppt_app.Presentations.Open(filename)
        ppt.SaveAs(exportfile, 32)
        print('保存 PDF 文件：', exportfile)
        ppt_app.Quit()

    def pptx(self, filename):
        self.ppt(filename)

    def pdf2docx(self, filename):
        '''
        pdf转docx,纯文字+图片的PDF识别效果最好，超链接等其他格式将不被保留 
        '''
        cv = Converter(filename)
        cv.convert(filename.replace('.pdf', '.docx'), start=0, end=None)
        cv.close()

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



    def create_watermarks(pdf_file_path,watermark_file_path):
        """
        给pdf文件添加水印
        :param pdf_file_path: pdf文件路径
        :param watermark_file_path: 水印文件路径
        :return:
        """

        def create_watermark(input_pdf, output_pdf, watermark):
            # 获取水印
            watermark_obj = PdfFileReader(watermark, strict=False)
            watermark_page = watermark_obj.getPage(0)

            # 创建读取对象和写入对象
            pdf_reader = PdfFileReader(input_pdf, strict=False)
            pdf_writer = PdfFileWriter()

            # 给所有页面添加水印，并新建pdf文件
            for page in range(pdf_reader.getNumPages()):
                page = pdf_reader.getPage(page)
                page.mergePage(watermark_page)
                pdf_writer.addPage(page)

            with open(output_pdf, 'wb') as out:
                pdf_writer.write(out)

        for pdf_file in os.listdir(pdf_file_path):
            if pdf_file[-3:] == 'pdf':
                input_pdf = pdf_file_path + '/' + pdf_file
                output_pdf = './水印版物料/'+pdf_file[0:-3]+'pdf'
                create_watermark(
                    input_pdf=input_pdf, output_pdf=output_pdf, watermark=watermark_file_path)



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