import re
import logging, traceback
from websocket import create_connection
from watson_developer_cloud import AuthorizationV1, SpeechToTextV1
import json
import threading
import sys, os
import time
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
logging.info("---------NEW DEBUG SESSION---------")

def logExecutionInfo():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    logging.error(''.join('!! ' + line for line in lines))

import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
CHUNKSIZE = 4000
RECORD_SECONDS = 6000
WAVE_OUTPUT_FILENAME = "speech.wav"
TIMEOUT_LIMIT = 3
TIME_SINCE_RESPONSE = 0
TIME_AT_RESPONSE = time.time() + 8

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

    try:
        ws.close()
    except Exception as e:
        logging.error("Could not close WebSocket: " + str(e))
    
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
    
    ws.send('{"action":"start","content-type":"audio/l16;rate=16000","interim_results":true,"inactivity_timeout":600}')
    
    logging.info("\tSent initiation request to IBM")
    
    logging.info("Websocket recreated, starting Mic stream again...")

    isRestarting = False
    #getMicData(ws)

def getMicData(): 
    global totalData 
    global isRestarting
    global ws

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
            logging.info("Reading stream chunk " + str(i))
            data = stream.read(CHUNK, False)
        except Exception as e:
            logging.error("Stream reading failed, error: " + str(e))

        try:
            logging.info("Appending stream data for chunk " + str(i) + "...")
            totalData += data
        except Exception as e:
            logging.error("Appending stream data to websocket buffer failed: " + str(e))
            totalData = b''

        if len(totalData) > CHUNKSIZE:
            try:
                dataChunk = totalData[0:CHUNKSIZE]
                dataStr = str(dataChunk)
                #matched = re.search(r'&\w+;', dataStr)
                #try:
                 #   dataStr = dataStr.encode('utf-8')
                logging.info("Sending data chunk " + str(i))
                ws.send(dataChunk, opcode=0x2)
                #except Exception as e:
                #    logging.error("Invalid binary message detected. Dumping message. Error type " + type(e).__name__ + ": " + str(e))
                #    totalData = totalData[CHUNKSIZE:]
            except (OSError) as e:
                logging.error("Invalid binary message detected. Dumping message. Error type " + type(e).__name__ + ": " + str(e))
                logExecutionInfo()
                totalData = totalData[CHUNKSIZE:]
                resetConnection()
            except Exception as e:
                logging.error("Sending failed, error type " + type(e).__name__ + ": " + str(e))
                logExecutionInfo()
                totalData = totalData[CHUNKSIZE:]
                resetConnection()
            try:
                logging.info("Stripping used data chunk " + str(i) + " from websocket buffer...")
                totalData = totalData[CHUNKSIZE:]
            except Exception as e:
                logging.error("Stripping CHUNKSIZE from websocket buffer failed: " + str(e))
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
    global TIME_SINCE_RESPONSE
    global TIME_AT_RESPONSE
    while True:
        try:
            if(check_pid(int(sys.argv[2])) is False):
                logging.warning("PitchPal termination detected, closing stream and websocket...")
                ws.close()
                os.kill(os.getpid(), 9)
        except Exception as e:
            logging.error("Monitor failed, error type " + type(e).__name__ + ": " + str(e))
            logExecutionInfo()

        try:
            result = json.loads(ws.recv())
        except Exception as e:
            #logging.error("Receiving failed, error type " + type(e).__name__ + ": " + str(e))
            #logExecutionInfo()
            pass

        print("----------")
        if("results" in result):
            print(result["results"][0]["alternatives"][0]["transcript"])
            try:
                overlayF = open(sys.argv[1]+"/overlay.txt", "w")
                overlayF.write(result["results"][0]["alternatives"][0]["transcript"])
            except Exception as e:
                logging.error("Error writing to overlay buffer: " + str(e))

            #TIME_AT_RESPONSE = time.time()
            #logging.info("Time since last websocket response: " + str(time.time()-TIME_AT_RESPONSE))

def checkForTimeout():
    global TIME_SINCE_RESPONSE
    global TIME_AT_RESPONSE
    while True:
        TIME_SINCE_RESPONSE = time.time() - TIME_AT_RESPONSE
        if(TIME_SINCE_RESPONSE > TIMEOUT_LIMIT):
            logging.info("Timeout limit reached, restarting WS...")
            try:
                resetConnection()
            except Exception as e:
                logging.error("Could not reset connection: " + str(e))
            TIME_AT_RESPONSE = time.time()
    

authorization = AuthorizationV1(
    username=USERNAME,
    password=PASSWORD)

token = authorization.get_token(url=SpeechToTextV1.default_url)

ws = create_connection('wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize?watson-token=' +
  token + '&model=en-US_BroadbandModel')

ws.send('{"action":"start","content-type":"audio/l16;rate=16000","interim_results":true,"inactivity_timeout":600}')
t3 = threading.Thread(target=receiveAudio)
t3.start()
#t4 = threading.Thread(target=checkForTimeout)
#t4.start()
getMicData()
t3.join()
#t4.join()
ws.close()





