import json
from threading import Thread

import win32clipboard
import time
import websocket


def on_open():
    print("### connection ###")


class WSClient:
    def __init__(self, path, enableTrance=False):
        self.url = path
        self.ws = None
        self.thread = None
        websocket.enableTrace(enableTrance)

    def connect(self):
        self.ws = websocket.WebSocketApp(self.url,
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_open=self.on_open)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()

    def on_open(self, ws):
        self.ws.send("Hi")
        print("### start connection ###")

    def on_message(self, ws, data):
        print("event", data)
        data = json.loads(data)
        data_type = data.get("type")
        msg = data.get("data")
        if data_type == "text":
            clipboard_set(clip.CF_UNICODETEXT, msg)

    def on_close(self):
        if self.thread and self.thread.isAlive():
            print('connection close')
            self.ws.close()
            self.thread.join()

    def send(self, data):
        self.ws.send(data)


clip = win32clipboard


def log(*args, **kwargs):
    print(args, kwargs)


type_dict = [clip.CF_UNICODETEXT]


def clipboard_get():
    """获取剪贴板数据"""
    clip.OpenClipboard()
    is_available = clip.GetPriorityClipboardFormat(type_dict)
    print("is available", is_available)
    if is_available != -1:
        data = clip.GetClipboardData(is_available)
    else:
        data = None
    clip.CloseClipboard()
    return data


def clipboard_set(format_type, data):
    """设置剪贴板数据"""
    clip.OpenClipboard()
    clip.EmptyClipboard()

    clip.SetClipboardData(format_type, data)
    clip.CloseClipboard()


def listen_clipboard(ws):
    current = clip.GetClipboardSequenceNumber()  # 获取当前剪切板内容的 id
    while True:
        # 检测间隔（延迟1秒）
        time.sleep(1)
        _number = clip.GetClipboardSequenceNumber()
        if current == _number:  # 比较剪切板内容 id 是否发生变化判断剪切板是否更新
            continue
        clip_data = clipboard_get()  # 获取剪切板内容
        current = _number  # 更新 id
        print(clip_data)


def main():
    path = 'ws://localhost:8000/ws/msg/12345'
    ws = WSClient(path)
    ws.connect()

    listen_clipboard(ws)


if __name__ == '__main__':
    main()
