import json
from threading import Thread

import win32clipboard
import time
import websocket


def on_open():
    print("### connection ###")


class SocketDropClient:
    def __init__(self, path, enableTrance=True):
        self.clip = win32clipboard
        self.type_dict = [self.clip.CF_UNICODETEXT]
        self.client_id = int(time.time())

        self.url = path
        self.ws = None
        self.thread = None
        self.current_clip_type, self.current_clip_data = self.clipboard_get()
        self.form = {"type": "", "data": "", "client_id": self.client_id}
        print("client id", self.client_id)

        websocket.enableTrace(enableTrance)

    def connect(self):
        self.ws = websocket.WebSocketApp(self.url + str(self.client_id),
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_open=self.on_open)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()

    def on_open(self, ws):
        # self.ws.send()
        print("### start connection ###")

    def on_message(self, ws, data):
        data = json.loads(data)
        print("data", data)
        data_type = data.get("type")
        msg = data.get("data")
        send_client_id = data.get("client_id")
        print("client id", send_client_id, self.client_id, data_type)
        if send_client_id != self.client_id:
            print("eee")
            self.current_clip_data = msg
            self.current_clip_type = data_type
            self.clipboard_set(self.clip.CF_UNICODETEXT, msg)

    def on_close(self, ws, states_code, close_msg):
        '''
                on_close: function
            Callback object which is called when connection is closed.
            on_close has 3 arguments.
            The 1st argument is this class object.
            The 2nd argument is close_status_code.
            The 3rd argument is close_msg.
        '''
        print("connection close, please check the internet and reconnect")
        self.ws.close()
        # if self.thread and self.thread.is_alive():
        #     self.ws.close()
        #     self.thread.join()

    def send(self, data):
        self.ws.send(data)

    def clipboard_get(self):
        """获取剪贴板数据"""
        self.clip.OpenClipboard()
        clip_type = self.clip.GetPriorityClipboardFormat(self.type_dict)
        if clip_type != -1:
            clip_data = self.clip.GetClipboardData(clip_type)
        else:
            clip_data = None
        self.clip.CloseClipboard()
        return clip_type, clip_data

    def clipboard_set(self, _type, data):
        """设置剪贴板数据"""
        self.clip.OpenClipboard()
        self.clip.EmptyClipboard()
        self.clip.SetClipboardData(_type, data)
        self.clip.CloseClipboard()

    def listen_clipboard(self):
        while True:
            # 检测间隔（延迟1秒）
            time.sleep(1)
            clip_type, clip_data = self.clipboard_get()
            if self.current_clip_data == clip_data:  # 比较剪切板内容 id 是否发生变化判断剪切板是否更新
                continue
            else:
                log("检测到了剪切板变化")
                self.current_clip_data = clip_data
                if clip_type == 13:
                    self.form["type"] = "text"
                    self.form["data"] = clip_data
                    self.send(json.dumps(self.form))


def log(*args, **kwargs):
    print(args, kwargs)


def main():
    path = 'ws://localhost:8000/ws/msg/'
    ws = SocketDropClient(path)
    ws.connect()
    ws.listen_clipboard()


if __name__ == '__main__':
    main()
