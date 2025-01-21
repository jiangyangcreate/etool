import os

os.chdir(".")
import pytest
from etool import ManagerSpeed, ManagerShare
from etool import (
    ManagerImage,
    ManagerEmail,
    ManagerDocx,
    ManagerExcel,
    ManagerPdf,
    ManagerIpynb,
    ManagerQrcode,
)
from etool import ManagerPassword, ManagerScheduler


def test_speed_manager():
    assert ManagerSpeed.network() is not None
    assert ManagerSpeed.disk() is not None
    assert ManagerSpeed.memory() is not None
    assert ManagerSpeed.gpu_memory() is not None


def test_screen_share():
    # 由于 screen_share 是一个长时间运行的服务，测试时可以检查是否能启动
    assert callable(ManagerShare.screen_share)


def test_share_file():
    # 由于 share_file 是一个长时间运行的服务，测试时可以检查是否能启动
    assert callable(ManagerShare.share_file)


# 跳过
@pytest.mark.skip(reason="发送邮件不宜频繁测试，跳过")
def test_email_manager():
    # 假设 send_email 方法返回 True 表示成功
    assert (
        ManagerEmail.send_email(
            sender="1234567890@qq.com",
            password="1234567890",
            recipients=["1234567890@qq.com"],
            subject="测试邮件",
            message="测试邮件内容",
            file_path="test.txt",
            img_path="test.webp",
        )
        is True
    )


@pytest.mark.skip(reason="定时发送不宜频繁测试，跳过")
def test_scheduler_manager():
    # 假设 send_email 方法返回 True 表示成功
    assert (
        ManagerScheduler.send_email(
            sender="1234567890@qq.com",
            password="1234567890",
            recipients=["1234567890@qq.com"],
            subject="测试邮件",
            message="测试邮件内容",
            file_path="test.txt",
            img_path="test.webp",
        )
        is True
    )


def test_image_manager():
    # 假设 merge_LR 和 merge_UD 方法返回合并后的图片路径
    assert ManagerImage.merge_LR(["pic1.webp", "pic2.webp"]) is not None
    assert ManagerImage.merge_UD(["pic1.webp", "pic2.webp"]) is not None
    assert ManagerImage.fill_image("pic1_UD.webp") is not None
    assert isinstance(ManagerImage.cut_image("pic1_UD_fill.webp"), list)
    assert ManagerImage.rename_images("tests", remove=True) is not None


def test_password_manager():
    # 检查生成的密码列表和随机密码是否符合预期
    assert (
        len(
            ManagerPassword.generate_pwd_list(
                ManagerPassword.results["all_letters"]
                + ManagerPassword.results["digits"],
                2,
            )
        )
        > 0
    )
    assert len(ManagerPassword.random_pwd(8)) == 8


def test_qrcode_manager():
    # 假设 gen_en_qrcode 和 gen_qrcode 方法返回生成的二维码路径
    assert (
        ManagerQrcode.generate_english_qrcode("https://www.baidu.com", "qr.png")
        is not None
    )
    assert ManagerQrcode.generate_qrcode("百度", "qr.png") is not None
    assert ManagerQrcode.decode_qrcode("qr.png") is not None


def test_ipynb_manager():
    # 假设 merge_notebooks 和 convert_notebook_to_markdown 方法返回 True 表示成功
    assert ManagerIpynb.merge_notebooks('ipynb_dir') is not None
    assert ManagerIpynb.convert_notebook_to_markdown('ipynb_dir.ipynb', 'md') is not None


def test_docx_manager():
    # 假设 get_pictures 方法返回提取的图片数量
    assert ManagerDocx.replace_words('ex1.docx', '1', '2') is not None
    assert ManagerDocx.change_forward('ex1.docx', 'result.docx') is not None
    assert ManagerDocx.get_pictures('ex1.docx', 'result') is not None

def test_excel_manager():
    # 假设 excel_format 方法返回 True 表示成功
    assert ManagerExcel.excel_format('ex1.xlsx', 'result.xlsx') is not None

@pytest.mark.skip(reason="pdf功能升级，代码重构中，跳过")
def test_pdf_manager():
    # 假设 create_watermarks 方法返回 True 表示成功
    assert ManagerPdf.create_watermarks('ex1.pdf', 'watermark.pdf') is not None
