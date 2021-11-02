import json
import os.path
from threading import Thread
import urllib.request as request
from urllib import parse
import requests

import win32clipboard
import time
import websocket

import client_config


def on_open():
    print("### connection ###")


class SocketDropClient:
    def __init__(self, path, domain=None, enableTrance=False):
        self.clip = win32clipboard
        self.type_dict = [self.clip.CF_UNICODETEXT, self.clip.CF_HDROP]
        self.client_id = int(time.time())
        self.domain = domain
        self.url = path
        self.ws = None
        self.thread = None
        self.current_clip_type, self.current_clip_data = self.clipboard_get()
        self.form = {"type": "", "data": "", "client_id": self.client_id}
        self.upload_path = client_config.DOMAIN + "/upload/"
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
            if data_type == "text":
                self.current_clip_data = msg
                self.current_clip_type = data_type
                self.clipboard_set(self.clip.CF_UNICODETEXT, msg)
            elif data_type == "file":
                filename = msg
                url = self.domain + "/file/" + filename
                print("url", url)
                self.download_file(url, filename)

    def download_file(self, url, filename):
        save_path = client_config.SAVE_PATH
        if not os.path.exists(save_path):
            print("文件夹不存在，建立文件夹：", save_path)
            os.mkdir(save_path)
        path = os.path.join(save_path, filename)
        print("开始下载, 保存到", path)
        request.urlretrieve(url, path)
        print("下载完成")

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
                if clip_type == self.clip.CF_UNICODETEXT:
                    self.form["type"] = "text"
                    self.form["data"] = clip_data
                    self.send(json.dumps(self.form))
                elif clip_type == self.clip.CF_HDROP:
                    self.form["type"] = "file"
                    filename = clip_data[0].split("\\")[-1]  # 可以多文件一起发送，暂时先发送一个
                    print("filename", filename)
                    files = {'file': (filename, open(clip_data[0], 'rb'))}
                    requests.post(self.upload_path, files=files, params={"client_id": self.client_id})
                    self.form["data"] = filename

                    self.send(json.dumps(self.form))


def log(*args, **kwargs):
    print(args, kwargs)


def main():
    websocket_path = client_config.WEBSOCKET_PATH
    domain = client_config.DOMAIN
    ws = SocketDropClient(websocket_path, domain)
    ws.connect()
    ws.listen_clipboard()


if __name__ == '__main__':
    main()
