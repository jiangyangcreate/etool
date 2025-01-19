from easyqr import easyqr as qr
from MyQR import myqr
import qrcode
class QrcodeManager:    
    def __init__(self):
        pass
    def upload(self, path):
        """
        上传图片
        :param path: 图片路径
        :return: 解析后的地址
        """
        url = qr.upload(path)
        url =qr.online(url)
        return url
    
    def gen_en_qrcode(self,words,save_path):
        """
        生成二维码
        :param path: 二维码内容
        :return: 二维码路径
        """
        myqr.run(
            words=words,
            save_name=save_path
        )

    def gen_qrcode(self, path, save_path):
        """
        生成二维码
        :param path: 二维码内容
        :return: 二维码路径
        """
        img = qrcode.make(path)
        img.save(save_path)
        return save_path

