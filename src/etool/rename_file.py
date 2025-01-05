import os
from PIL import Image
import re

def rename_images(path):
    # 定义备份文件夹路径
    backup_folder = path

    filename_dict = {}
    # 读取备份文件夹下所有图片
    for filename in os.listdir(backup_folder):
        if filename.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
            # 打开图片
            img_path = os.path.join(backup_folder, filename)
            img = Image.open(img_path)

            # 将图片转为无损webp格式
            output_path = os.path.join(
                backup_folder, f"{os.path.splitext(filename)[0]}.webp"
            )
            img.save(output_path, "webp", lossless=True)
            os.remove(img_path)
            # 匹配文件名中的日期部分
            match = re.match(r"IMG_(\d{8})_\d+", filename)
            if match:
                # 提取日期部分
                date_part = match.group(1)
                if date_part in filename_dict:
                    date_part = date_part + str(filename_dict[date_part])
                    filename_dict[date_part] += 1
                else:
                    filename_dict[date_part] = 1
                # 获取图片尺寸
                width, height = img.size

                # 构造新的文件名，包含日期和尺寸
                new_filename = f"{date_part}-{width}-{height}.webp"

                # 获取完整的文件路径
                new_file_path = os.path.join(backup_folder, new_filename)

                # 重命名文件
                
                os.rename(output_path, new_file_path)

                # 构造字典并添加到列表中
                info = '''id: {file_id},
    width: {width},
    height: {height},
    title: "None", 
    description: "None"'''.format(file_id=date_part, width=width, height=height)
                infos = "{"+info+"},"

                return infos
