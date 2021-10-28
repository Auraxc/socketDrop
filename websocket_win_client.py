from threading import Thread

import win32clipboard
import time
import websocket


def on_open():
    print("### connection ###")


class WSClient:
    def __init__(self, path):
        self.url = path
        self.ws = None
        self.thread = None
        websocket.enableTrace(True)

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

    def on_message(self, ws, data, callback=None):
        print("event", data)
        if callback:
            callback(data)

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


def listen_clipboard():
    current = clip.GetClipboardSequenceNumber()
    while True:

        # txt 存放当前剪切板文本
        current_number = clip.GetClipboardSequenceNumber()
        if current == current_number:
            time.sleep(1)
            continue
        txt = clipboard_get()
        current = current_number
        print(txt)
        # 检测间隔（延迟0.2秒）
        time.sleep(1)


def main():
    listen_clipboard()


if __name__ == '__main__':
    main()
