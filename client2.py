import socket
import cv2
import os
import asyncio
import numpy as np
import pickle


loop = asyncio.get_event_loop()
async def cli():
        reader, writer = await asyncio.open_connection('10.104.200.217', 9888,loop=loop)

        json_data = {'PeerCode': "1", 'Sender': False}

        send_data = pickle.dumps(json_data)
        writer.write(send_data)
        #await asyncio.sleep(6)
        count = 0

        while (1):
                print("came here")
                frames = await reader.read(1)
                print(frames)
                Text   = await reader.read(1)
                print (Text)
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

