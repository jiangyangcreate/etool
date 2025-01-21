from easyqr import easyqr as qr
from MyQR import myqr
import qrcode
class ManagerQrcode:    

    @staticmethod
    def decode_qrcode(path):
        """
        解析二维码
        :param path: 图片路径
        :return: 解析后的地址
        """
        url = qr.upload(path)
        url = qr.online(url)
        return url
    
    @staticmethod
    def generate_english_qrcode(words, save_path):
        """
        生成英文内容的二维码
        :param words: 二维码内容
        :param save_path: 保存路径
        :return: 二维码路径
        """
        try:
            myqr.run(
                words=words,
                save_name=save_path
            )
            return save_path
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def generate_qrcode(path, save_path):
        """
        生成二维码
        :param path: 二维码内容
        :param save_path: 保存路径
        :return: 二维码路径
        """
        img = qrcode.make(path)
        img.save(save_path)
        return save_path

