import json
import os
import shutil
from typing import List

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat</title>
</head>
<body>
<h1>WebSocket Chat</h1>
<h2>Your ID: <span id="ws-id"></span></h2>
<form action="" onsubmit="sendMessage(event)">
    <input type="text" id="messageText" autocomplete="off"/>
    <button>Send</button>
</form>

<iframe name="dummyframe" id="dummyframe" style="display: none;"></iframe>

<form action="/upload/" method="post" enctype="multipart/form-data" target="dummyframe">
<input name="file" id="file" type="file">
<input type="submit" value="uploadFile上传">
</form>

<ul id='messages'>
</ul>
<script>
    var client_id = Date.now()
    var host = location.host
    document.querySelector("#ws-id").textContent = client_id;
    var ws = new WebSocket(`ws://${host}/ws/msg/${client_id}`);
    ws.onmessage = function (event) {
        var messages = document.getElementById('messages')
        var message = document.createElement('li')
        var msg = JSON.parse(event.data)
        console.log("type", msg.type, event)
        var msg_type = msg.type
        if (msg_type == 'text'){
            var content = document.createTextNode(msg.data)}
            else {
                var content = document.createElement('a')
                content.href = '/file/' + msg.filename
                content.innerText = msg.filename
            }
        message.appendChild(content)
        messages.appendChild(message)
    };

    function sendMessage(event) {
        var input = document.getElementById("messageText")
        var data = input.value
        ws.send(data)
        input.value = ''
        event.preventDefault()
    }
</script>
</body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
file_manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/msg/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            form = {"type": "text", "data": data}
            await manager.broadcast(json.dumps(form))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


def save_path(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder)
    print("path", path)
    return path + "/"


@app.post("/upload/")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        path = save_path("files")
        print("path", path)
        filename = file.filename
        filepath = path + filename
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        form = {"type": "file", "filename": filename, "path": path}
        await manager.broadcast(json.dumps(form))
    except Exception as e:
        print("save file error", e)
    # return {"filename": file.filename}

@app.get("/file/{filename}")
def file_download(filename):
    path = save_path("files")
    file_path = path + filename
    return FileResponse(file_path)


if __name__ == '__main__':
    # uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
    uvicorn.run(app, host="localhost", port=8000, debug=True)
