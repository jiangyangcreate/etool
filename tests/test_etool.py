import pytest
from etool import SpeedManager, screen_share, share_file
from etool import PdfManager, DocxManager, EmailManager
from etool import ImageManager, ExcelManager, QrcodeManager
from etool import IpynbManager, PasswordManager

def test_speed_manager():
    # 假设 SpeedManager 的方法返回某种结果
    assert SpeedManager.network() is not None
    assert SpeedManager.disk() is not None
    assert SpeedManager.memory() is not None
    assert SpeedManager.gpu_memory() is not None

def test_screen_share():
    # 由于 screen_share 是一个长时间运行的服务，测试时可以检查是否能启动
    assert callable(screen_share)

def test_share_file():
    # 同样，share_file 是一个长时间运行的服务，测试时可以检查是否能启动
    assert callable(share_file)

def test_pdf_manager():
    pdf_manager = PdfManager()
    # 假设 create_watermarks 方法返回 True 表示成功
    assert pdf_manager.create_watermarks('ex1.pdf', 'watermark.pdf') is True

def test_docx_manager():
    docx_manager = DocxManager()
    # 假设 get_pictures 方法返回提取的图片数量
    assert docx_manager.get_pictures('ex1.docx', 'result') > 0

def test_email_manager():
    email_manager = EmailManager()
    # 假设 send_email 方法返回 True 表示成功
    assert email_manager.send_email(
        sender='1234567890@qq.com',
        password='1234567890',
        recipients=['1234567890@qq.com'],
        subject='测试邮件',
        message='测试邮件内容',
        file_path='test.txt',
        img_path='test.jpg'
    ) is True

def test_image_manager():
    image_manager = ImageManager()
    # 假设 merge_LR 和 merge_UD 方法返回合并后的图片路径
    assert image_manager.merge_LR(['pic1.jpg', 'pic2.jpg']) is not None
    assert image_manager.merge_UD(['pic1.jpg', 'pic2.jpg']) is not None

def test_excel_manager():
    excel_manager = ExcelManager()
    # 假设 excel_format 方法返回 True 表示成功
    assert excel_manager.excel_format('ex1.xlsx', 'result.xlsx') is True

def test_qrcode_manager():
    qrcode_manager = QrcodeManager()
    # 假设 gen_en_qrcode 和 gen_qrcode 方法返回生成的二维码路径
    assert qrcode_manager.gen_en_qrcode('https://www.baidu.com', 'qr.png') is not None
    assert qrcode_manager.gen_qrcode('百度', 'qr.png') is not None

def test_ipynb_manager():
    ipynb_manager = IpynbManager()
    # 假设 merge_ipynb 和 ipynb2md 方法返回 True 表示成功
    assert ipynb_manager.merge_ipynb('ipynb_dir') is True
    assert ipynb_manager.ipynb2md('ipynb_dir.ipynb', 'md') is True

def test_password_manager():
    password_manager = PasswordManager()
    # 检查生成的密码列表和随机密码是否符合预期
    assert len(password_manager.generate_pwd_list(password_manager.results['all_letters'] + password_manager.results['digits'], 2)) > 0
    assert len(password_manager.random_pwd(8)) == 8 