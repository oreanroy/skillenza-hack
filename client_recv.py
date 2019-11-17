import socket
import cv2
import os
import asyncio
import numpy as np
import pickle
from audio_stream import TextToSpeech

size = 64,64
loop = asyncio.get_event_loop()
bottomLeftCornerOfText = (10,20)
subscription_key = "9a230063f45c4838aa7ccdc41c710bdd"
app = TextToSpeech(subscription_key)
app.get_token()

RevLabel = {0:'A',1:'B',2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J',10:'K',11:'L',12:'M',
                   13:'N',14:'O',15:'P',16:'Q',17:'R',18:'S',19:'T',20:'U',21:'V',22:'W',23:'X',
               24:'Y',25:'Z',26:'space',27:'del',29:'nothing'}

async def cli():
        reader, writer = await asyncio.open_connection('10.104.200.217', 9888,loop=loop)

        json_data = {'PeerCode': "1", 'Sender': False}

        send_data = pickle.dumps(json_data)
        writer.write(send_data)
        #await asyncio.sleep(6)
        count = 0
        cv2.namedWindow('Resized Window', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Resized Window', 400, 600)
        while (1):
                frames = await reader.read(60000)
                frames = np.frombuffer(frames,dtype='uint8')
                if (len(frames)==60000):
                    frame = frames.reshape((100,200,3))
                    Text   = await reader.read(40)
                    try:
                        Text =  int(str(Text,encoding='utf-8'))
                    except:
                        continue
                    Text = RevLabel[Text]
                    print(Text)
                    app.save_audio(str(Text))
                    cv2.putText(frame,"The correct seq is: %s"%str(Text),bottomLeftCornerOfText,cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,0),1)
                    cv2.imshow('Resized Window',frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    #
                else:
                    continue

                #cv2.imshow('frame',frame)
                #if cv2.waitKey(1) & 0xFF == ord('q'):
                #    break
                #print(frame.size)
                #resize = cv2.resize(image, (640, 480), interpolation = cv2.INTER_LINEAR)
                #send_frame = frame.tobytes()
                #send_frame = pickle.dumps(frame)
                #await writer.drain()
                #count = count+1
                #if count > 100:
                 #       break
#resize = cv2.resize(image, (640, 480), interpolation = cv2.INTER_LINEAR) 
#  cv2.imwrite("%03d.jpg" % count, resize)  


loop.run_until_complete(cli())
loop.close()

