import json
import os
from typing import List


class ManagerIpynb:
    @staticmethod
    def merge_notebooks(directory_path: str) -> str | None:
        """
        Merge multiple ipynb files into a single file.

        :param directory_path: The path to the folder containing the ipynb files
        :return: The path to the merged ipynb file
        """
        if not directory_path.endswith("/"):
            directory_path += "/"
        base_path: str = directory_path.rstrip("/")

        notebook_files: List[str] = [
            os.path.join(directory_path, f)
            for f in os.listdir(directory_path)
            if f.endswith(".ipynb")
        ]

        if not notebook_files:
            return None

        with open(notebook_files[0], "r", encoding="utf-8") as f:
            main_notebook: dict = json.load(f)
        for notebook_file in notebook_files[1:]:
            with open(notebook_file, "r", encoding="utf-8") as f:
                current_notebook: dict = json.load(f)
            main_notebook["cells"].extend(current_notebook["cells"])

        out_path = f"{base_path}.ipynb"
        with open(out_path, "w", encoding="utf-8") as output_file:
            json.dump(main_notebook, output_file)

        return out_path

    @staticmethod
    def convert_notebook_to_markdown(notebook_path: str, output_directory: str = "") -> str:
        """
        Convert an ipynb file to Markdown format and save it.

        :param notebook_path: The path to the ipynb file
        :param output_directory: The directory to save the Markdown file
        :return: The path to the saved Markdown file
        """
        base = os.path.splitext(os.path.basename(notebook_path))[0]
        if output_directory:
            os.makedirs(output_directory, exist_ok=True)
            markdown_file_name = os.path.join(output_directory, base + ".md")
        else:
            markdown_file_name = notebook_path.replace(".ipynb", ".md")

        markdown_content = ""
        try:
            with open(notebook_path, "r", encoding="utf-8") as f:
                notebook_content: dict = json.load(f)

            for cell in notebook_content["cells"]:
                if cell["cell_type"] == "markdown":
                    markdown_content += "\n" + "".join(cell["source"]) + "\n\n"
                elif cell["cell_type"] == "code":
                    src = "".join(cell["source"])
                    markdown_content += "\n```\n" + src + "\n```\n\n"
        except Exception as error:
            raise RuntimeError(f"failed to convert notebook: {error}") from error

        with open(markdown_file_name, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return markdown_file_name
