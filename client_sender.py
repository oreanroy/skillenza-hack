import socket
import cv2
import os
import asyncio
import numpy as np
import pickle

cap = cv2.VideoCapture(0)
cap.set(64, 64)
chunkLen = 250
size = 100,200
loop = asyncio.get_event_loop()
async def cli():
        reader, writer = await asyncio.open_connection('10.104.200.217', 9888,loop=loop)

        json_data = {'PeerCode': "2", 'Sender': True}

        send_data = pickle.dumps(json_data)
        print(len(send_data))
        writer.write(send_data)

        await writer.drain()
        #await asyncio.sleep(6)
        count = 0

        while 1:
                success,frame = cap.read()
                print(frame.shape)
                frame = cv2.resize(frame, size)
                cv2.imshow('frame',frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                #print(frame.size)
                #resize = cv2.resize(image, (640, 480), interpolation = cv2.INTER_LINEAR)
                if (count%10==0):
                    send_frame = frame.tobytes()
                    print(len(send_frame))
                    #send_frame = pickle.dumps(frame)
                    writer.write(send_frame)
                    await writer.drain()
                count = count+1
                #if count > 100:
                 #       break
#resize = cv2.resize(image, (640, 480), interpolation = cv2.INTER_LINEAR) 
#  cv2.imwrite("%03d.jpg" % count, resize)  


loop.run_until_complete(cli())
loop.close()
