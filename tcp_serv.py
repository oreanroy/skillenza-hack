import sys
import os
import socket
import asyncio
from multiprocessing import Process
import queue
import pickle
import numpy as np
import pandas as pd
import os
import keras
from keras.layers import Conv2D, MaxPool2D, Flatten, Dense, Dropout, BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras import regularizers
from sklearn.model_selection import train_test_split
import cv2
import seaborn as sns


def create_model():
    
    model = Sequential()
    
    model.add(Conv2D(16, kernel_size = [3,3], padding = 'same', activation = 'relu', input_shape = (64,64,3)))
    model.add(Conv2D(32, kernel_size = [3,3], padding = 'same', activation = 'relu'))
    model.add(MaxPool2D(pool_size = [3,3]))
    
    model.add(Conv2D(32, kernel_size = [3,3], padding = 'same', activation = 'relu'))
    model.add(Conv2D(64, kernel_size = [3,3], padding = 'same', activation = 'relu'))
    model.add(MaxPool2D(pool_size = [3,3]))
    
    model.add(Conv2D(128, kernel_size = [3,3], padding = 'same', activation = 'relu'))
    model.add(Conv2D(256, kernel_size = [3,3], padding = 'same', activation = 'relu'))
    model.add(MaxPool2D(pool_size = [3,3]))
    
    model.add(BatchNormalization())
    
    model.add(Flatten())
    model.add(Dropout(0.5))
    model.add(Dense(512, activation = 'relu', kernel_regularizer = regularizers.l2(0.001)))
    model.add(Dense(29, activation = 'softmax'))
    
    model.compile(optimizer = 'adam', loss = keras.losses.categorical_crossentropy, metrics = ["accuracy"])
    
    print("MODEL CREATED")
    model.summary()
    
    return model




PeerDict = {'1':None,'2':None}
i=1
model = create_model()




class client_threadd():
	def __init__(self,reader,writer,idd):
		self.TextQueue = queue.Queue()
		self.reader = reader
		self.writer = writer
		self.VideoChunkLen = 12288 
		self.textChunkLen  = 256
		self.MaxSizeSize   = 25
		self.ID            = idd
		self.Peer          = None
		self.sender        = True
		self.CommunicationTask = None


	def getStrSize(self,sizee):
		strSize = str(sizee)
		while len(strSize)<self.MaxSizeSize:
			strSize = "0%s"%(strSize)
		return strSize

	async def getPeerID(self):
		#try:
			Text = await self.reader.read(45)
			Text = pickle.loads(Text)
			self.Peer = PeerDict[Text['PeerCode']]
			self.sender = Text['Sender']
			print(Text,self.sender,self.Peer)
		#except:
		#	await self.closeAll()

	async def communicate(self):
		await self.getPeerID()
		while(1):
			try:
				if (self.sender == False):
					return
				frames = await self.reader.read(n=self.VideoChunkLen)
				#print(frames,len(frames))
				#frames_arr = pickle.load(frames)
				frames1 = np.frombuffer(frames,dtype='uint8')
				frames1 = frames1.reshape((1,64,64,3))
				Text   = model.predict_classes(frames1)
				print (np.argmax(Text),Text[0])
				#Dict   = pickle.dumps({"text":Text,"frames":frames1})
				#FramesToWrite = picke.dump(Dict)
				#print(Dict,FramesToWrite)
				#self.Peer.writer.write(FramesToWrite)
				#await self.Peer.writer.drain()
			except:
				await self.closeAll()


	async def runCommunication(self):
		self.CommunicationTask = asyncio.ensure_future(self.communicate())
		await self.CommunicationTask



	async def closeAll(self):
		print ("Came In")
		if not self.CommunicationTask.cancelled():
			self.CommunicationTask.cancel()
		self.writer.close()
		await self.writer.wait_closed()

async def clientFD(reader,writer):
	print("Connection 1")
	global i
	CT = client_threadd(reader,writer,i)
	PeerDict["%d"%i] = CT
	i+=1
	CommunicationTask = asyncio.ensure_future(CT.runCommunication())
	asyncio.gather(CommunicationTask)
	return 

async def serverAsync():
	server = await asyncio.start_server(clientFD, '0.0.0.0', 9888)
	await server.serve_forever()

if __name__=='__main__':
	model.load_weights('Trained_model.h5')
	loop = asyncio.new_event_loop()
	loop.run_until_complete(serverAsync())
