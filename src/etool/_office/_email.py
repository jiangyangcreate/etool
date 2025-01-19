from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

class EmailManager:     
    def __init__(self):
        pass

    def send_mail(self, message, to_addrs, sender,sender_show=None, recipient_show=None, Subject=None,filelanguage = 'cn',filepath=None,imagepath=None, cc_show='',password=None)->str:
        """
        :param sender: str 发件人
        :param message: str 邮件内容
        :param Subject: str 邮件主题描述
        :param sender_show: str 发件人显示，不起实际作用如："xxx"
        :param recipient_show: str 收件人显示，不起实际作用 多个收件人用','隔开如："xxx,xxxx"
        :param to_addrs: str 实际收件人
        :param cc_show: str 抄送人显示，不起实际作用，多个抄送人用','隔开如："xxx,xxxx"
        """
        # 填写真实的发邮件服务器用户名、密码
        if not to_addrs.endswith(','):
            to_addrs = to_addrs + ','
        if not password:
            password = os.getenv('EMAIL_PASSWORD')
        #发送附件的方法定义为一个变量
        msg=MIMEMultipart()                             
        # 邮件内容
        content= message+ "<br><br>" + "来自 Allen 的 AI Agent 的邮件，有问题请联系我。"
        #发送正文
        msg.attach(MIMEText(content,'html', 'utf-8'))  
        #调用传送附件模块，传送附件
        if filepath:
            att=MIMEText(open(filepath,'rb').read(),'base64','utf-8')    
            #修改下方filename为文件名（文本型，不支持中文）
            att["Content-Type"]='application/octet-stream' 
            if filelanguage == 'cn':
                show_file_name = filepath.split('/')[-1] # 填写你希望展示出来的附件名称
                att.add_header("Content-Disposition", "attachment", filename=("gbk", "", show_file_name))
            else:
                show_file_name = filepath.split('/')[-1] # 填写你希望展示出来的附件名称
                att["Content-Disposition"]=f'attachment;filename="{show_file_name}"' 
            
            msg.attach(att)#发送附件

        if imagepath:
            # 批量添加图片时需要修改值
            mime_images = '<p><img src="cid:imageid" alt="imageid"></p>'
            with open(imagepath, 'rb') as img_file:
                mime_img = MIMEImage(img_file.read())
            mime_img.add_header('Content-ID', '<imageid>')  # 注意这里的格式
            # 上传图片至缓存空间
            msg.attach(mime_img)
            # 上传正文
            mime_html = MIMEText('<html><body>{0}</body></html>'.format(mime_images), 'html', 'utf-8')
            # 添加附图至正文
            msg.attach(mime_html)
        # 邮件主题描述
        msg["Subject"] = Subject if Subject else "来自 AI 的邮件"
        # 发件人显示，不起实际作用
        msg["from"] = sender_show if sender_show else sender
        # 收件人显示，不起实际作用
        msg["to"] = recipient_show if recipient_show else to_addrs
        # 抄送人显示，不起实际作用
        msg["Cc"] = cc_show

        # 循环这个列表，剔除空数据
        to_addrs = [addr for addr in to_addrs.split(',') if addr]
        print(to_addrs)
        try:
            with SMTP_SSL(host="smtp.qq.com", port=465) as smtp:
                # 登录发邮件服务器
                smtp.login(user=sender, password=password)
                # 实际发送、接收邮件配置
                smtp.sendmail(from_addr=sender, to_addrs=to_addrs, msg=msg.as_string())
        except Exception as e:
            if e.smtp_code != -1 :
                return f"send error.{e}"
        return "send ok."