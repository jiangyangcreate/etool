import os
from PIL import Image
import skimage.io as io
import numpy as np

class ManagerImage:

    @staticmethod
    def merge_LR(pics:list,save_path:str=None)->str: #左右拼接
        if save_path is None:
            # 自动读取pics[0]的文件名
            save_path = os.path.splitext(pics[0])[0]+'_LR'+os.path.splitext(pics[0])[1]
        LR_save_path = save_path#合并后图片的名字
        #横向拼接
        图片1 = io.imread(pics[0])   # np.ndarray, [h, w, c], 值域(0, 255), RGB
        图片2 = io.imread(pics[1])   # np.ndarray, [h, w, c], 值域(0, 255), RGB
        #print(图片1.dtype)
        图片1_h = 图片1.shape[0]   #查看图片的大小
        图片1_w = 图片1.shape[1]
        图片1_c = 图片1.shape[2]
        图片2_h = 图片2.shape[0]   #查看图片的大小
        图片2_w = 图片2.shape[1]
        if 图片1_h >= 图片2_h :
            pj1 = np.zeros((图片1_h,图片1_w+图片2_w,图片1_c))   #横向拼接
        else:
            pj1 = np.zeros((图片2_h,图片1_w+图片2_w,图片1_c))  #横向拼接
        pj1[:,:图片1_w,:] = 图片1.copy()   #图片图片1在左
        pj1[:,图片2_w:,:] = 图片2.copy()   #图片图片2在右
        pj1=np.array(pj1,dtype=np.uint8)   #将pj1数组元素数据类型的改为"uint8"
        io.imsave(LR_save_path, pj1)   #保存拼接后的图片
        return LR_save_path

    @staticmethod
    def merge_UD(pics:list,save_path:str=None)->str: #上下拼接
        if save_path is None:
            # 自动读取pics[0]的文件名
            save_path = os.path.splitext(pics[0])[0]+'_UD'+os.path.splitext(pics[0])[1]
        UD_save_path = save_path
        # 上面与下面拼接
        图片1 = io.imread(pics[0])   # np.ndarray, [h, w, c], 值域(0, 255), RGB
        图片2 = io.imread(pics[1])   # np.ndarray, [h, w, c], 值域(0, 255), RGB
        图片1_h = 图片1.shape[0]   #查看图片的大小
        图片1_w = 图片1.shape[1]
        图片1_c = 图片1.shape[2]
        图片2_h = 图片2.shape[0]   #查看图片的大小
        图片2_w = 图片2.shape[1]
        if 图片1_w >= 图片2_w :
            pj = np.zeros((图片1_h+图片2_h,图片1_w,图片1_c))   #竖向拼接
        else:
            pj = np.zeros((图片2_h+图片2_h,图片2_w,图片1_c))  #竖向拼接
        #计算最终图片的像素大小
        pj[:图片1_h,:,:] = 图片1.copy()   #图片图片1在左
        pj[图片2_h:,:,:] = 图片2.copy()   #图片图片2在右
        pj=np.array(pj,dtype=np.uint8)   #将pj数组元素数据类型的改为"uint8"
        io.imsave(UD_save_path, pj)   #保存拼接后的图片
        return UD_save_path

    @staticmethod
    def fill_image(image_path:str,save_path:str=None)->str:
        """
        将图片填充为正方形
        """
        if save_path is None:
            save_path = os.path.splitext(image_path)[0]+'_fill'+os.path.splitext(image_path)[1]
        image = Image.open(image_path)
        width, height = image.size
        #选取长和宽中较大值作为新图片的
        new_image_length = width if width > height else height
        #生成新图片[白底]
        new_image = Image.new(image.mode, (new_image_length, new_image_length), color='white')
        #将之前的图粘贴在新图上，居中
        if width > height:#原图宽大于高，则填充图片的竖直维度
            new_image.paste(image, (0, int((new_image_length - height) / 2)))#(x,y)二元组表示粘贴上图相对下图的起始位置
        else:
            new_image.paste(image, (int((new_image_length - width) / 2),0))
        new_image.save(save_path)
        return save_path
    
    @staticmethod
    def cut_image(image_path:str)->list[str]:
        """
        将图片切成九宫格
        """
        image = Image.open(image_path)
        width, height = image.size
        item_width = int(width / 3)
        image_list = []
        for i in range(0,3):
            for j in range(0,3):
                save_path = os.path.splitext(image_path)[0]+'_cut'+str(i)+str(j)+os.path.splitext(image_path)[1]
                box = (j*item_width,i*item_width,(j+1)*item_width,(i+1)*item_width)
                image.crop(box).save(save_path)
                image_list.append(save_path)
        return image_list
    
    @staticmethod
    def rename_images(image_folder:str,remove:bool=False)->str:
        """
        将图片重命名为日期-宽度-高度.webp，并返回图片信息
        param:
            image_folder: 图片文件夹路径
            remove: 是否删除原图片
        return:
            infos: 图片信息
        """
        # 定义备份文件夹路径
        backup_folder = image_folder
        infos = ""
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
                if remove:
                    os.remove(img_path)
                # 获取照片的拍摄日期
                exif_data = img._getexif()
                if exif_data:
                    # 36867 是 DateTimeOriginal 的标签
                    date_taken = exif_data.get(36867)
                    if date_taken:
                        # 转换日期格式为 YYYYMMDD_HHMMSS
                        date_time_parts = date_taken.split()
                        date_part = date_time_parts[0].replace(':', '')
                        time_part = date_time_parts[1].replace(':', '')
                        date_part = f"{date_part}{time_part}"
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
                        info = "{"+info+"},"+"\n"
                        infos += info

        return infos
