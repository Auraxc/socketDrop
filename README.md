# socketDrop
使用中间服务器，通过 websocket 在设备之间分享文件和文本，支持网页版，也可使用客户端自动共享剪切板，自动复制文件
share files and text with all device, windows, mac, ios


# 网页版：
  - 建立 websocket 连接
  - 发送消息给所有客户端
  - 上传文件到服务器
  - 识别下载地址，点击下载地址开始下载文件
## TODO:
  - 自动判断文件类型
    - 类型为图片自动显示
    - 类型为音频添加播放器

# 客户端：
## TODO:
  - 自动监听剪切板，自动识别并复制文本和文件
  - 和服务器建立 websocket 连接，剪切板发生改变时自动上传
