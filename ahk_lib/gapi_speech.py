#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr

# obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)


# recognize speech using Google Cloud Speech
GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""
{
  "type": "service_account",
  "project_id": "splendid-tower-174014",
  "private_key_id": "d4f5a83f46d8b0bb76f46f4e1327483ee7442428",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDSP7GiVK9VGhJd\n/nIzaudsixK39nlVwgXpJQOwjLgJhetgoSf/XrzXXEvKY9Q3jv6ROt+Fwv9y0cBN\nPxD91mJXCt8sLb5i94u9Z4aJt9H7FoTgLFtyRbkRUWmkm4bO27S0BmVtWyahGWd8\nCJHOrPuclSxYLHbbxBotpS4kZOQ1o65XMe0EjsTjrUc1THJMOZ8dra9weZj/mA23\n9P7EcitZDXrnB/zSpF+jV+WR9Za8qNPwuLJ1TKHnb+wIhNt9CBFl2gZZjD6M6HuE\nYapdInbw19f8DvP+ioVP6ZdInAO7xgeDgeCynS/Fn9xe1CgBF7Dee5yAaERBs30P\nH6NZoXLFAgMBAAECggEAHcQrw4ZGzn8i85DHHVV4z0q/SzFHi2ctTA1UAOZjVeHS\nabtXPNXuWXU1O8G3dWg2zVvu8nKhlOFyXt1ba/yyro0Y/Jm7Vyqh655hE1Vlkq1l\nAZH2Hm8VnQiQMuBcDSRY6JXxPTLG/M7qckqKTh76fng2L4OYDlQsuqKkrj1ke91f\naqoRZWJHjBOQxhHKGJSVKJijaejCPFN4/HVlAe3SSI0rAHz/ROu7M59VSVwwqbeP\nS0VievJDM/4Q6870qnDFGIf42cS6azp6lmPUOm4NyhEKhYYEMEA+tYZ352b1x2jQ\nKNLhRqcWvWHTl48MsFqfEFMT9P/xxZImz7UIU6BhrwKBgQDqnM9MvtDMabiFUXUp\nbvT5KX/jpSqdQvmGC9tK8pvyONRxplpNkaxMhXXiFHt+mveBqJnSGWp5TU9iK6i3\nuuhKu17j38302KB9qKqioBOIuAZ2VA4syAjDOtvwy6t74PwEhnbeDxv3XOV3FFp1\nLx+0CCReLoztQpQpU6C/09IFuwKBgQDlak3EDxD6oed9i1CG+XmE6Lh3a6ytYICH\nwcayY8vQy5b7G63tAQOMjBtLW8aMIBYVDIUUP3HOJx8s2CGrOzipbOIJjfcQd/UB\nBWEReIr8ZnUhMFrlsXdtMS1XFe7+kSy3I09noigT715lMpBtKAsDgH0P/i1RaLbG\nhvsrhCKhfwKBgHaFiWQn8auSrRkMsbegyjklceo7AnA36X6CduJB9e5EL27Kr0wI\nj5aIxajU2B55gxgJaMvu8w8cs0HQ9Ib88WTvi1xrL8zFsy5ICwvk+nlTHlCg3hhZ\nZbPbBEl9WsBWRHq0w1AjKempEHM74QbaK5XzlwvNUHx76gWGreq6w5sJAoGBAMjw\nNTD2aU69JH8n2N6AAFnTZE7k9pfdIHbH2PtCwbAdwh4q/knKS4t85CM7PUpaiDzj\nfGRhtZJ1Xa7vl33dHyH2hn0L5Ux9ZREB3yVoSYQNUaZCLjtlF0+CdU4DnhNGoL2/\npbsFosjjLfDBOxMAsbTdg6zQWm0lpIF6lOBmmdaNAoGBAJl/yx/0aARcNsAxG7uh\nd4UE7XB0b9WRZRJEEbcZ7xLjGfoM3el/Lv5eCljNCYe4hIZESqPy6GNyOyDj1Elw\n0Uoj1FrcX/94w1KnjeBwAQETJquDjcyl+rvAyKTdhhD0Jz8m57IehLA0GL2qhey0\nmgfBrGNjKSWVXD8nS1PfXP27\n-----END PRIVATE KEY-----\n",
  "client_email": "connorpenrod@splendid-tower-174014.iam.gserviceaccount.com",
  "client_id": "106484207701172391291",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/connorpenrod%40splendid-tower-174014.iam.gserviceaccount.com"
}
"""

transcription = ""
try:
    transcription = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
except sr.UnknownValueError:
    print("Google Cloud Speech could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Cloud Speech service; {0}".format(e))

file = open("gapi_text.txt", "w")
file.write(transcription)
file.close()