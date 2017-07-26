from websocket import create_connection
from watson_developer_cloud import AuthorizationV1, SpeechToTextV1
import json
import threading
import sys

######

import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
CHUNKSIZE = 8000
RECORD_SECONDS = 600
WAVE_OUTPUT_FILENAME = "speech.wav"

ws = None
token = None
t3 = None
isRestarting = False

def resetConnection():
    global ws
    global token
    global t3
    global isRestarting
    
    print("Restarting WS...")
    
    ws.close()
    
    ws = None
    print("\tClosed previous websocket...")
    
    try:
        ws = create_connection('wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize?watson-token=' +
          token + '&model=en-US_BroadbandModel')
    except Exception as e:
        print("Creating WS failed, error: " + str(e))
        return
    
    print("\tEstablished WS connection...")
    
    ws.send('{"action":"start","content-type":"audio/l16;rate=16000","interim_results":true,"inactivity_timeout":300}')
    
    print("\tSent initiation request to IBM")
    
    print("Websocket recreated, starting Mic stream again...")

    isRestarting = False
    getMicData(ws)

def getMicData(ws): 
    global totalData 
    global isRestarting
     
    audio = pyaudio.PyAudio()
                 
 
    # start Recording
    
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True, #input_device_index=inputDeviceIndex,
                    frames_per_buffer=CHUNK)
    print("recording...")
    frames = []
    totalData = b''
    bytesSent = 0
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        try:
            data = stream.read(CHUNK)
        except Exception as e:
            print("Stream reading failed, error: " + str(e))

        totalData += data

        if len(totalData) > CHUNKSIZE:
            try:
                dataChunk = totalData[0:CHUNKSIZE]
                ws.send(dataChunk, opcode=0x2)
            except Exception as e:
                print("Sending failed, error: " + str(e))
                resetConnection()
                print("Closing mic data stream")
                stream.stop_stream()
                stream.close()
                audio.terminate()
                return
            totalData = totalData[CHUNKSIZE:]
        #ws.send(data, opcode=0x2)
        #bytesSent = i * CHUNKSIZE
        #print(str(bytesSent/1000/1000) + " megabytes")
        

    print("finished recording")
     
     
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    

######

def receiveAudio():
    global isRestarting
    while True:
        try:
            result = json.loads(ws.recv())
        except Exception as e:
            print("Receiving failed, error: " + str(e))
            
        print("----------")
        if("results" in result):
            print(result["results"][0]["alternatives"][0]["transcript"])
            overlayF = open(sys.argv[1]+"/overlay.txt", "w")
            overlayF.write(result["results"][0]["alternatives"][0]["transcript"])


authorization = AuthorizationV1(
    username='90dfb3ab-223d-4a5f-87d7-0232a480dc21',
    password='4mgJ1asd4KCj')

token = authorization.get_token(url=SpeechToTextV1.default_url)

ws = create_connection('wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize?watson-token=' +
  token + '&model=en-US_BroadbandModel')

ws.send('{"action":"start","content-type":"audio/l16;rate=16000","interim_results":true,"inactivity_timeout":300}')
t3 = threading.Thread(target=receiveAudio)
t3.start()
getMicData(ws)
t3.join()
ws.close()





