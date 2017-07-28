import logging, traceback
from websocket import create_connection
from watson_developer_cloud import AuthorizationV1, SpeechToTextV1
import json
import threading
import sys, os
from configparser import SafeConfigParser

######
try:
    parser = SafeConfigParser()
    parser.read(sys.argv[1] + "/../settings.conf")
    USERNAME = parser.get('STT_settings', 'username')
    PASSWORD = parser.get('STT_settings', 'password')
except Exception as e:
    logging.error(str(e))
    logging.warning("Could not load IBM STT configuration settings. Cannot connect websocket. Disconnecting...")
    sys.exit()

logging.basicConfig(
    filename="stt_debug.log",
    level=1,
    format="*****\n%(asctime)s||%(levelname)s||line %(lineno)d||%(funcName)s: %(message)s",
    datefmt='%m/%d/%Y %I:%M:%S %p'
    )
logging.info("---------NEW DEBUG SESSION--------")

def logExecutionInfo():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    logging.error(''.join('!! ' + line for line in lines))

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
    
    logging.info("Restarting WS...")
    
    ws.close()
    
    ws = None
    logging.info("\tClosed previous websocket...")
    
    try:
        ws = create_connection('wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize?watson-token=' +
          token + '&model=en-US_BroadbandModel')
    except Exception as e:
        logging.error("Creating WS failed, error: " + str(e))
        logExecutionInfo()
        return
    
    logging.info("\tEstablished WS connection...")
    
    ws.send('{"action":"start","content-type":"audio/l16;rate=16000","interim_results":true,"inactivity_timeout":300}')
    
    logging.info("\tSent initiation request to IBM")
    
    logging.info("Websocket recreated, starting Mic stream again...")

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
    logging.info("Mic stream initiated, recording...")
    frames = []
    totalData = b''
    bytesSent = 0
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        try:
            data = stream.read(CHUNK, False)
        except Exception as e:
            logging.error("Stream reading failed, error: " + str(e))

        totalData += data

        if len(totalData) > CHUNKSIZE:
            try:
                dataChunk = totalData[0:CHUNKSIZE]
                ws.send(dataChunk, opcode=0x2)
            except Exception as e:
                logging.error("Sending failed, error type " + type(e).__name__ + ": " + str(e))
                logExecutionInfo()
                resetConnection()
                logging.info("Closing mic data stream")
                stream.stop_stream()
                stream.close()
                audio.terminate()
                return
            totalData = totalData[CHUNKSIZE:]
        #ws.send(data, opcode=0x2)
        #bytesSent = i * CHUNKSIZE
        #print(str(bytesSent/1000/1000) + " megabytes")
        

    logging.info("Mic stream has finished recording, closing stream, terminating audio...")
     
     
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    

######
def check_pid(pid):        
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def receiveAudio():

    global isRestarting
    global ws
    while True:
        try:
            if(check_pid(int(sys.argv[2])) is False):
                logging.warning("PitchPal termination detected, closing stream and websocket...")
                ws.close()
                os.kill(os.getpid(), 9)
        except Exception as e:
            logging.error("Receiving failed, error type " + type(e).__name__ + ": " + str(e))
            logExecutionInfo()

        try:
            result = json.loads(ws.recv())
        except Exception as e:
            pass

        print("----------")
        if("results" in result):
            print(result["results"][0]["alternatives"][0]["transcript"])
            overlayF = open(sys.argv[1]+"/overlay.txt", "w")
            overlayF.write(result["results"][0]["alternatives"][0]["transcript"])


authorization = AuthorizationV1(
    username=USERNAME,
    password=PASSWORD)

token = authorization.get_token(url=SpeechToTextV1.default_url)

ws = create_connection('wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize?watson-token=' +
  token + '&model=en-US_BroadbandModel')

ws.send('{"action":"start","content-type":"audio/l16;rate=16000","interim_results":true,"inactivity_timeout":300}')
t3 = threading.Thread(target=receiveAudio)
t3.start()
getMicData(ws)
t3.join()
ws.close()





