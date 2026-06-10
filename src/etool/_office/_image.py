import os
from PIL import Image


class ManagerImage:

    @staticmethod
    def merge_LR(pics: list, save_path: str = None) -> str:  # left and right merge
        if save_path is None:
            # automatically read the file name of pics[0]

            save_path = (
                os.path.splitext(pics[0])[0] + "_LR" + os.path.splitext(pics[0])[1]
            )
        LR_save_path = save_path  # the name of the merged image
        with Image.open(pics[0]) as im1, Image.open(pics[1]) as im2:
            image1 = im1.convert("RGB")
            image2 = im2.convert("RGB")
            w = image1.width + image2.width
            h = max(image1.height, image2.height)
            # black canvas keeps parity with the historical numpy zeros() behavior
            merged = Image.new("RGB", (w, h))
            merged.paste(image1, (0, 0))  # img1 on the left
            merged.paste(image2, (image1.width, 0))  # img2 on the right
            merged.save(LR_save_path)

        return LR_save_path

    @staticmethod
    def merge_UD(pics: list, save_path: str = None) -> str:  # up and down merge
        if save_path is None:
            # automatically read the file name of pics[0]

            save_path = (
                os.path.splitext(pics[0])[0] + "_UD" + os.path.splitext(pics[0])[1]
            )
        UD_save_path = save_path
        with Image.open(pics[0]) as im1, Image.open(pics[1]) as im2:
            image1 = im1.convert("RGB")
            image2 = im2.convert("RGB")
            w = max(image1.width, image2.width)
            h = image1.height + image2.height
            merged = Image.new("RGB", (w, h))
            merged.paste(image1, (0, 0))  # img1 on top
            merged.paste(image2, (0, image1.height))  # img2 below
            merged.save(UD_save_path)

        return UD_save_path

    @staticmethod
    def fill_image(image_path: str, save_path: str = None) -> str:
        """
        fill the image to a square
        """
        if save_path is None:
            save_path = (
                os.path.splitext(image_path)[0]
                + "_fill"
                + os.path.splitext(image_path)[1]
            )
        image = Image.open(image_path)

        width, height = image.size
        # select the larger value as the new image size
        new_image_length = width if width > height else height
        # generate a new image[white background]
        new_image = Image.new(
            image.mode, (new_image_length, new_image_length), color="white"
        )
        # paste the previous image to the new image, centered
        if (
            width > height
        ):  # the original image width is greater than the height, then fill the vertical dimension of the image

            new_image.paste(
                image, (0, int((new_image_length - height) / 2))
            )  # (x,y)tuple represents the starting position of pasting the upper image relative to the lower image
        else:
            new_image.paste(image, (int((new_image_length - width) / 2), 0))
        new_image.save(save_path)
        return save_path

    @staticmethod
    def cut_image(image_path: str) -> list[str]:
        """
        cut the image into a grid
        """
        image = Image.open(image_path)
        width, height = image.size
        item_width = int(width / 3)

        image_list = []
        for i in range(0, 3):
            for j in range(0, 3):
                save_path = (
                    os.path.splitext(image_path)[0]
                    + "_cut"
                    + str(i)
                    + str(j)
                    + os.path.splitext(image_path)[1]
                )
                box = (
                    j * item_width,
                    i * item_width,
                    (j + 1) * item_width,
                    (i + 1) * item_width,
                )
                image.crop(box).save(save_path)
                image_list.append(save_path)
        return image_list

    @staticmethod
    def rename_images(image_folder: str, remove: bool = False) -> str:
        """
        rename the image to date-width-height.webp, and return the image information
        param:
            image_folder: image folder path
            remove: whether to delete the original image

        return:
            infos: image information
        """
        # define the backup folder path
        backup_folder = image_folder
        infos = ""
        # read all images in the backup folder
        for filename in os.listdir(backup_folder):

            if filename.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
                # open the image
                img_path = os.path.join(backup_folder, filename)
                img = Image.open(img_path)

                # convert the image to a lossless webp format
                output_path = os.path.join(
                    backup_folder, f"{os.path.splitext(filename)[0]}.webp"
                )

                img.save(output_path, "webp", lossless=True)
                if remove:
                    os.remove(img_path)
                # get the shooting date of the photo
                exif_data = img._getexif()
                if exif_data:
                    date_taken = exif_data.get(36867)
                    if date_taken:
                        # convert the date format to YYYYMMDD_HHMMSS
                        date_time_parts = date_taken.split()
                        date_part = date_time_parts[0].replace(":", "")
                        time_part = date_time_parts[1].replace(":", "")
                        date_part = f"{date_part}{time_part}"
                        # get the image size
                        width, height = img.size

                        # construct a new file name, including the date and size
                        new_filename = f"{date_part}-{width}-{height}.webp"
                        # get the complete file path
                        new_file_path = os.path.join(backup_folder, new_filename)
                        # rename the file
                        os.rename(output_path, new_file_path)

                        # construct a dictionary and add it to the list
                        info = '''id: {file_id},
            width: {width},
            height: {height},
            title: "None", 
            description: "None"'''.format(
                            file_id=date_part, width=width, height=height
                        )

                        info = "{" + info + "}," + "\n"
                        infos += info

        return infos
