from websocket_win_client import clipboard_set, clip, WSClient


def test_set():
    path = r"C:\Users\vt\PycharmProjects\socketDrop\websocket_server.py"
    clipboard_set(clip.CF_UNICODETEXT, path)
    # clipboard_set(path)
    # print("set result", result)


def test_websocket():
    path = 'ws://localhost:8000/ws/msg/12345'
    ws = WSClient(path, enableTrance=True)
    ws.connect()
    ws.send("test")


if __name__ == '__main__':
    test_websocket()
