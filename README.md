# 安装

使用 pip 安装 etool:

```bash
pip install -U etool
```

# 功能与使用示例

## 网络

### 测试网络速度

```python
from etool import ManagerSpeed
ManagerSpeed.network() # 网络测试
ManagerSpeed.disk() # 硬盘测试
ManagerSpeed.memory() # 内存测试
ManagerSpeed.gpu_memory() # GPU测试
```

## 屏幕与文件分享

### 分享屏幕

```python
from etool import ManagerShare
ManagerShare.screen_share() # 分享屏幕
```

### 分享文件

```python
from etool import ManagerShare
ManagerShare.share_file() # 分享文件
```

## 办公

### PDF处理

```python
from etool import ManagerPdf
# 功能升级，代码重构中
```

### docx处理

```python
from etool import ManagerDocx
word_path = 'ex1.docx' # docx文件路径
result_path = 'result' # 保存路径
ManagerDocx.replace_words(word_path, '1', '2') # 替换文档中的文字
ManagerDocx.change_forward(word_path, 'result.docx') # 更改文档格式
ManagerDocx.get_pictures(word_path, result_path) # 提取docx中的图片至result文件夹
```

### 邮件发送

```python
from etool import ManagerEmail
ManagerEmail.send_email(
    sender='1234567890@qq.com',
    password='1234567890',
    recipients=['1234567890@qq.com'],
    subject='测试邮件',
    message='测试邮件内容',
    file_path='test.txt',
    img_path='test.webp'
) # 发送邮件
```

### 图片处理

```python
from etool import ManagerImage
pics = ['pic1.webp', 'pic2.webp'] # 图片路径列表
ManagerImage.merge_LR(pics) # 左右拼接
ManagerImage.merge_UD(pics) # 上下拼接
ManagerImage.fill_image('pic1_UD.webp') # 填充图片
ManagerImage.cut_image('pic1_UD_fill.webp') # 裁剪图片
ManagerImage.rename_images('tests', remove=True) # 重命名图片
```

### 表格处理

```python
from etool import ManagerExcel
excel_path = 'ex1.xlsx' # excel文件路径
save_path = 'result.xlsx' # 保存路径
ManagerExcel.excel_format(excel_path, save_path) # 复制ex1.xlsx的样式到result.xlsx
```

### 二维码生成

```python
from etool import ManagerQrcode
qr_path = 'qr.png' # 保存路径
ManagerQrcode.generate_english_qrcode(words='https://www.baidu.com', qr_path) # 生成不含中文的二维码
ManagerQrcode.generate_qrcode(words='百度', qr_path) # 生成含中文的二维码
ManagerQrcode.decode_qrcode(qr_path) # 解码二维码
```

### ipynb转换

```python
from etool import ManagerIpynb
ipynb_dir = 'ipynb_dir' # ipynb文件夹路径
md_dir = 'md' # md文件夹路径

ManagerIpynb.merge_notebooks(ipynb_dir) # 合并ipynb文件
ManagerIpynb.convert_notebook_to_markdown(ipynb_dir+'.ipynb', md_dir) # 将ipynb文件转换为md文件
```

## 其他

### 任务调度

```python
from etool import ManagerScheduler
# 由于定时发送不宜频繁测试，功能未在README中详细列出
```

### 密码生成

```python
from etool import ManagerPassword
print(ManagerPassword.generate_pwd_list(ManagerPassword.results['all_letters'] + ManagerPassword.results['digits'], 2))
# 生成2位密码的所有可能（可用于密码爆破）
print(ManagerPassword.random_pwd(8))
# 随机生成8位密码（随机加密）
```

