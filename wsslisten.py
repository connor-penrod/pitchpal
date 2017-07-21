from websocket import create_connection

url = "wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize"
ws = create_connection(url)
result = ws.recv()
ws.close()
print(result)