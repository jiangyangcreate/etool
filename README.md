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

# doc、xlsx等转换为pdf(转换一个)
ManagerPdf.pdfconverter(os.path.join(os.path.dirname(__file__),'pdf','ex1.docx'),os.path.join(os.path.dirname(__file__),'pdf_out'))
# doc、xlsx等转换为pdf(转换一个目录下的所有文件)
ManagerPdf.pdfconverter(os.path.join(os.path.dirname(__file__),'pdf'),os.path.join(os.path.dirname(__file__),'pdf_out'))

# 给pdf文件添加水印（一个文件）
ManagerPdf.create_watermarks(os.path.join(os.path.dirname(__file__),'pdf_out','ex1.pdf'),os.path.join(os.path.dirname(__file__),'pdf_out','watermarks.pdf'),os.path.join(os.path.dirname(__file__),'pdf_out_watermark'))
# 给pdf文件添加水印（一个目录下的所有文件）
ManagerPdf.create_watermarks(os.path.join(os.path.dirname(__file__),'pdf_out'),os.path.join(os.path.dirname(__file__),'pdf_out','watermarks.pdf'),os.path.join(os.path.dirname(__file__),'pdf_out_watermark'))


# 加密pdf文件
ManagerPdf.encrypt_pdf(os.path.join(os.path.dirname(__file__),'pdf_out','ex1.pdf'),r"1234567890")
# 解密pdf文件
ManagerPdf.decrypt_pdf(os.path.join(os.path.dirname(__file__),'pdf_out','ex1_encrypted.pdf'),r"1234567890")

# 拆分pdf文件（按页数）每3页一份
ManagerPdf.split_by_pages(os.path.join(os.path.dirname(__file__),'pdf_out','merged.pdf'),3)
# 拆分pdf文件（按份数）生成2份
ManagerPdf.split_by_num(os.path.join(os.path.dirname(__file__),'pdf_out','merged.pdf'),2)

# 将pdf ex2插入到pdf ex1的指定页后
ManagerPdf.insert_pdf(os.path.join(os.path.dirname(__file__),'pdf_out','ex1.pdf'),os.path.join(os.path.dirname(__file__),'pdf_out','ex2.pdf'),0,os.path.join(os.path.dirname(__file__),'pdf_out','pdf_insert.pdf'))
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
    recipient='1234567890@qq.com',
    subject='测试邮件',
    message='测试邮件内容',
    file_path='test.txt',
    image_path='test.webp'
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

def job():
    print("job")
    raise Exception("error")

def func_success():
    print("success")

def func_failure():
    print("failure")

ManagerScheduler.pocwatch(job, 2, func_success, func_failure)
"""
- `job`: 任务函数
- `schedule_time`: 执行时间
- `func_success`: 任务成功时的回调函数
- `func_failure`: 任务失败时的回调函数

`schedule_time`的格式如下：

如果是数字则默认单位是秒，每间隔`schedule_time`秒执行一次，例如`120`，则每2分钟执行一次。

如果是字符串则默认是时间点，请遵从`HH:MM`的格式，例如`08:00`，每天在这个时间点执行一次。

如果是列表，则默认是多个时间点，例如`["08:00", "12:00", "16:00"]`，每天在这些时间点执行一次。

如果传入的是字典，则解析字典的键：

如果字典的键为数字，则默认是日期，对应字典的值遵从上方数字、字符串、列表的判断。

如果字典的键为字符串，则默认是星期几（以周一为例，支持的写法包括：`1`、`monday`、`Monday`、`MONDAY`、`mon`、`mon.`、`m`，以此类推），对应字典的值遵从上方数字、字符串、列表的判断。

例如下面是1号的8点、2号的8点、12点、16点、3号每隔一个小时执行一次、每周一的8点执行一次。

schedule_time = {
1: "08:00",
2: ["08:00", "12:00", "16:00"],
3: 216000,
"1": "08:00",
}

"""
# 如果你不确定调度时间，可以先使用parse_schedule_time函数，确认一下
ManagerScheduler.parse_schedule_time(120)
ManagerScheduler.parse_schedule_time("08:00")
ManagerScheduler.parse_schedule_time(["08:00", "12:00", "16:00"])
ManagerScheduler.parse_schedule_time({1: "08:00", 2: ["08:00", "12:00", "16:00"], 3: 216000, "1": "08:00"})

```

### 密码生成

```python
from etool import ManagerPassword
print(ManagerPassword.generate_pwd_list(ManagerPassword.results['all_letters'] + ManagerPassword.results['digits'], 2))
# 生成2位密码的所有可能（可用于密码爆破）
print(ManagerPassword.random_pwd(8))
# 随机生成8位密码（随机加密）
```

