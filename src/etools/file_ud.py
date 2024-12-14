from flask import Flask, request, send_from_directory, render_template_string
import os
def file_ud(port=8099):


    app = Flask(__name__)

    # 设置桌面路径和文件夹名称
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    etool_folder = os.path.join(desktop_path, "etool")

    # 如果文件夹不存在，则创建
    if not os.path.exists(etool_folder):
        os.makedirs(etool_folder)

    # 首页模板
    index_template = '''
    <!doctype html>
    <title>eTool 文件上传</title>
    <h1>上传新文件</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=上传>
    </form>
    <h2>文件列表</h2>
    <ul>
    {% for filename in files %}
      <li><a href="{{ url_for('download_file', filename=filename) }}">{{ filename }}</a></li>
    {% endfor %}
    </ul>
    '''

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # 获取上传的文件
            file = request.files['file']
            if file:
                # 保存文件到etool文件夹
                file.save(os.path.join(etool_folder, file.filename))
        # 获取文件夹中的文件列表
        files = os.listdir(etool_folder)
        return render_template_string(index_template, files=files)

    @app.route('/uploads/<filename>')
    def download_file(filename):
        return send_from_directory(etool_folder, filename)

    app.run(host='0.0.0.0', port=port)
