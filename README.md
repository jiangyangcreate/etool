# 安装

使用 pip 安装 etool:

```bash
pip install etool
```

# 功能与使用示例

## 网络

### 测试网络速度

```python
from etool import SpeedManager
SpeedManager.network() # 网络测试
SpeedManager.disk() # 硬盘测试
SpeedManager.memory() # 内存测试
SpeedManager.gpu_memory() # GPU测试
```

### 分享屏幕

```python
from etool import screen_share
screen_share() # 分享屏幕
```

### 分享文件

```python
from etool import share_file
share_file() # 分享文件
```

## 办公

### PDF处理

```python
from etool import PdfManager
pdf_file_path = 'ex1.pdf'# pdf文件路径
watermark_file_path = 'watermark.pdf'# 水印文件路径
PdfManager().create_watermarks(pdf_file_path,watermark_file_path) # 给PDF添加水印
```

### docx处理

```python
from etool import DocxManager
word_path = 'ex1.docx'# docx文件路径
result_path = 'result'# 保存路径
DocxManager().get_pictures(word_path,result_path) # 提取docx中的图片至result文件夹
```

### 邮件发送

```python
from etool import EmailManager
EmailManager().send_email(
    sender='1234567890@qq.com',
    password='1234567890',
    recipients=['1234567890@qq.com'],
    subject='测试邮件',
    message='测试邮件内容',
    file_path='test.txt',
    img_path='test.jpg'
) # 发送邮件
```

### 图片处理

```python
from etool import ImageManager
pics = ['pic1.jpg','pic2.jpg']# 图片路径列表
ImageManager().merge_LR(pics) # 左右拼接
ImageManager().merge_UD(pics) # 上下拼接

```

### 表格处理

```python
from etool import ExcelManager
excel_path = 'ex1.xlsx'# excel文件路径
save_path = 'result.xlsx'# 保存路径
ExcelManager().excel_format(excel_path,save_path) # 复制ex1.xlsx的样式到result.xlsx
```

### 二维码生成

```python
from etool import QrcodeManager
qr_path = 'qr.png'# 保存路径
QrcodeManager().gen_en_qrcode(words='https://www.baidu.com',qr_path) # 生成不含中文的二维码
QrcodeManager().gen_qrcode(path='百度',qr_path) # 生成含中文的二维码
```

### ipynb转换

```python
from etool import JupyterManager
ipynb_dir = 'ipynb_dir'# ipynb文件夹路径
md_dir = 'md'# md文件夹路径

JupyterManager().merge_ipynb(ipynb_dir) # 合并ipynb文件
JupyterManager().ipynb2md(ipynb_dir+'.ipynb',md_dir) # 将ipynb文件转换为md文件
```

## 其他

### 任务调度
```python
from etool import TaskManager
TaskManager().task_schedule() # 任务调度
```

### 密码生成

```python
from etool import PasswordManager
print(PasswordManager().generate_pwd_list(PasswordManager.results['all_letters'] + PasswordManager.results['digits'], 2))
# 生成2位密码的所有可能（可用于密码爆破）
print(PasswordManager().random_pwd(8))
# 随机生成8位密码（随机加密）
```

