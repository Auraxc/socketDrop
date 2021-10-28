import win32clipboard
import time

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


def test_set():
    path = r"C:\Users\vt\PycharmProjects\socketDrop\websocket_server.py"
    clipboard_set(clip.CF_UNICODETEXT, path)
    # clipboard_set(path)
    # print("set result", result)


if __name__ == '__main__':
    main()
    # test_set()
