
from flask import Flask, Response,render_template_string
from io import BytesIO
from PIL import ImageGrab
import time
import threading
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent(object):
    def __init__(self):
        self.events = {}

    def wait(self):
        ident = get_ident()
        if ident not in self.events:
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        now = time.time()
        remove = None
        try:
            for ident, event in self.events.items():
                if not event[0].isSet():
                    event[0].set()
                    event[1] = now
            else:
                if now - event[1] > 5:
                    remove = ident
            if remove:
                del self.events[remove]
        except Exception as e:
            print(e)

    def clear(self):
        self.events[get_ident()][0].clear()


class BaseCamera(object):
    thread = None
    frame = None
    last_access = 0
    event = CameraEvent()

    def __init__(self):
        if BaseCamera.thread is None:
            BaseCamera.last_access = time.time()

            BaseCamera.thread = threading.Thread(target=self._thread)
            BaseCamera.thread.start()

            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        BaseCamera.last_access = time.time()

        BaseCamera.event.wait()
        BaseCamera.event.clear()

        return BaseCamera.frame

    @staticmethod
    def frames():
        raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def _thread(cls):
        print('Starting camera thread.')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            BaseCamera.frame = frame
            BaseCamera.event.set()
            if time.time() - BaseCamera.last_access > 10:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break
        BaseCamera.thread = None



class Camera(BaseCamera):
    video_source = 0


    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        fps = 24  # 限制帧率
        frame_interval = 1.0 / fps
        while True:
            time.sleep(frame_interval - 0.001)
            image = ImageGrab.grab()  # 获取屏幕数据
            # w, h = image.size
            output_buffer = BytesIO()  # 创建二进制对象
            image.save(output_buffer, format='JPEG', quality=100)  # quality提升图片分辨率
            frame = output_buffer.getvalue()  # 获取二进制数据
            yield frame  # 生成器返回一张图片的二进制数据

app = Flask(__name__)


@app.route('/')
def index():
    return render_template_string('''<html>
<head>
    <title>屏幕共享</title>
    <script>
        // 定期清理旧图片，防止内存占用过大
        function setupImageCleaning() {
            const img = document.querySelector('img');
            setInterval(() => {
                img.src = img.src.split('?')[0] + '?t=' + new Date().getTime();
            }, 5000); // 每5秒刷新一次
        }
    </script>
</head>
<body>
    <img src="{{ url_for('video_feed') }}" onload="setupImageCleaning()">
</body>
</html>''')


def gen(camera):
    """
    流媒体发生器
    """
    while True:
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """流媒体数据"""
    response = Response(gen(Camera()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


def screen_share(port=8900):
    app.run(threaded=True, host='0.0.0.0', port=port,debug=True)
