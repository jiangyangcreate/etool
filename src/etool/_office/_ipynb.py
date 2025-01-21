import os
import json
from typing import List

class ManagerIpynb:
    @staticmethod
    def merge_notebooks(directory_path: str) -> str:
        """
        合并多个ipynb文件到一个文件中。
        
        :param directory_path: 包含ipynb文件的文件夹路径
        :return: 合并后的ipynb文件路径
        """
        if not directory_path.endswith("/"):
            directory_path += "/"
        base_path: str = directory_path.rstrip("/")

        notebook_files: List[str] = [
            os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(".ipynb")
        ]

        if not notebook_files:
            return None

        main_notebook: dict = json.load(open(notebook_files[0], "r", encoding="utf-8"))
        for notebook_file in notebook_files[1:]:
            current_notebook: dict = json.load(open(notebook_file, "r", encoding="utf-8"))
            main_notebook["cells"].extend(current_notebook["cells"])

        with open(f"{base_path}.ipynb", "w", encoding="utf-8") as output_file:
            json.dump(main_notebook, output_file)

        return f"{base_path}.ipynb"

    @staticmethod
    def convert_notebook_to_markdown(notebook_path: str, output_directory: str = "") -> str:
        """
        将ipynb文件转换为Markdown格式并保存。
        
        :param notebook_path: ipynb文件路径
        :param output_directory: 保存Markdown文件的目录
        :return: 保存的Markdown文件路径
        """
        markdown_file_name: str = os.path.join(output_directory, notebook_path.replace(".ipynb", ".md"))

        try:
            notebook_content: dict = json.load(open(notebook_path, "r", encoding="utf-8"))
            markdown_content: str = ""

            for cell in notebook_content["cells"]:
                if cell["cell_type"] == "markdown":
                    markdown_content += "\n" + "".join(cell["source"]) + "\n\n"
                elif cell["cell_type"] == "code":
                    markdown_content += "\n" + "".join(cell["source"]) + "\n\n"
        except Exception as error:
            print(error)
        return markdown_file_name