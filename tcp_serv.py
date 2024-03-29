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




model = create_model()
PeerDict = {"1":queue.Queue(),"2":queue.Queue()}




class client_threadd():
	def __init__(self,reader,writer,idd):
		self.readerr = reader
		self.writerr = writer
		self.VideoChunkLen = 60000 
		self.textChunkLen  = 256
		self.MaxSizeSize   = 40
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
			Text = await self.readerr.read(45)
			Text = pickle.loads(Text)
			self.Peer = Text['PeerCode']
			self.ID   = list(PeerDict.keys()-set([self.Peer]))[0]
			self.sender = Text['Sender']
			print(Text,self.sender,self.Peer)
		#except:
		#	await self.closeAll()



	async def communicate(self):
		await self.getPeerID()
		size=64,64
		while(1):
			try:
				if (not self.sender):
					if (PeerDict[self.ID].empty()):
						await asyncio.sleep(0.5)
						continue
					dataDict = PeerDict[self.ID].get()
					frames = dataDict['frames']
					Text   = self.getStrSize(dataDict['text'])
					#print(Text,len(bytes(Text,encoding='utf-8')))
					self.writerr.write(frames)
					await self.writerr.drain()
					self.writerr.write(bytes(Text,encoding='utf-8'))
					await self.writerr.drain()
				else:
					frames = await self.readerr.read(n=self.VideoChunkLen)
					frames2 = np.frombuffer(frames,dtype='uint8')
					frames1 = frames2.reshape((100,200,3))
					frame = cv2.resize(frames1, size)
					frames1 = frame.reshape((1,64,64,3))
					Text   = model.predict_classes(frames1)
					Dict   = ({"text":Text[0],"frames":frames})
					PeerDict[self.Peer].put(Dict)
			except ValueError:
				await self.closeAll()


	async def runCommunication(self):
		self.CommunicationTask = asyncio.ensure_future(self.communicate())
		await self.CommunicationTask



	async def closeAll(self):
		print ("Came In",self.ID)
		if not self.CommunicationTask.cancelled():
			self.CommunicationTask.cancel()
		self.writerr.close()
		await self.writerr.wait_closed()

i=1


async def clientFD(reader,writer):
	global i
	print("Connection %d"%i)
	CT = client_threadd(reader,writer,i)
	i+=1
	CommunicationTask = asyncio.ensure_future(CT.runCommunication())
	asyncio.gather(CommunicationTask)
	return 

async def serverAsync():
	server = await asyncio.start_server(clientFD, '0.0.0.0', 9888)
	await server.serve_forever()

if __name__=='__main__':
	model.load_weights('Final_model_asl.h5')
	loop = asyncio.new_event_loop()
	loop.run_until_complete(serverAsync())