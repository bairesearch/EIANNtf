# -*- coding: utf-8 -*-
"""SANItf2.py

# Requirements:
Python 3 and Tensorflow 2.1+ 

# License:
MIT License

# Usage:
python3 SANItf2.py

# Description

Train an artificial neural network (ANN or SANI)

- Author: Richard Bruce Baxter - Copyright (c) 2020 Baxter AI (baxterai.com)

"""

# %tensorflow_version 2.x
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import tensorflow as tf
import numpy as np

import sys
np.set_printoptions(threshold=sys.maxsize)

#from SANItf2_operations import *
import SANItf2_operations
from SANItf2_operations import generateParameterNameNetwork
import SANItf2_globalDefs
from numpy import random

#algorithm = "ANN"
algorithm = "SUANN"
#algorithm = "CANN"
#algorithm = "SANI"

costCrossEntropyWithLogits = False
if(algorithm == "SANI"):
	algorithmSANI = "sharedModulesBinary"
	#algorithmSANI = "sharedModules"
	#algorithmSANI = "repeatedModules"
	if(algorithmSANI == "repeatedModules"):
		import SANItf2_algorithmSANIrepeatedModules as SANItf2_algorithmSANI
	elif(algorithmSANI == "sharedModules"):
		import SANItf2_algorithmSANIsharedModules as SANItf2_algorithmSANI
		costCrossEntropyWithLogits = True
	elif(algorithmSANI == "sharedModulesBinary"):
		import SANItf2_algorithmSANIsharedModulesBinary as SANItf2_algorithmSANI
elif(algorithm == "ANN"):
	import SANItf2_algorithmANN
elif(algorithm == "CANN"):
	import SANItf2_algorithmCANN
elif(algorithm == "SUANN"):
	import SANItf2_algorithmSUANN
	
import SANItf2_loadDataset

#performance enhancements for development environment only: 
debugUseSmallDataset = True	#def:False	#switch increases performance during development	#eg data-POStagSentence-smallBackup
useSmallSentenceLengths = True	#def:False	#switch increases performance during development	#eg data-simple-POStagSentence-smallBackup
trainMultipleFiles = False	#def:True	#switch increases performance during development	#eg data-POStagSentence
trainMultipleNetworks = False	#improve classification accuracy by averaging over multiple independently trained networks (test)
if(trainMultipleNetworks):
	numberOfNetworks = 5
else:
	numberOfNetworks = 1
	
#loadDatasetType3 parameters:
#if generatePOSunambiguousInput=True, generate POS unambiguous permutations for every POS ambiguous data example/experience
#if onlyAddPOSunambiguousInputToTrain=True, do not train network with ambiguous POS possibilities
#if generatePOSunambiguousInput=False and onlyAddPOSunambiguousInputToTrain=False, requires simultaneous propagation of different (ambiguous) POS possibilities

if(algorithm == "SANI"):
	if(algorithmSANI == "repeatedModules"):
		dataset = "POStagSequence"
	elif(algorithmSANI == "sharedModules"):
		dataset = "POStagSentence"
		numberOfFeaturesPerWord = -1
		paddingTagIndex = -1
		if(SANItf2_algorithmSANI.allowMultipleContributingSubinputsPerSequentialInput):
			generatePOSunambiguousInput = False
			onlyAddPOSunambiguousInputToTrain = False
		else:
			generatePOSunambiguousInput = False
			onlyAddPOSunambiguousInputToTrain = True
	elif(algorithmSANI == "sharedModulesBinary"):
		dataset = "POStagSentence"
		numberOfFeaturesPerWord = -1
		paddingTagIndex = -1	
		generatePOSunambiguousInput = False
		onlyAddPOSunambiguousInputToTrain = False	#True
elif(algorithm == "ANN"):
	#dataset = "POStagSequence"
	dataset = "NewThyroid"
	#trainMultipleNetworks = True	#default: False
	#numberOfNetworks = 3	#default: 1
elif(algorithm == "CANN"):
	#dataset = "POStagSequence"
	dataset = "NewThyroid"
	#trainMultipleNetworks = True	#default: False
	#numberOfNetworks = 5	#default: 1
	trainHebbianBackprop = False	#default: False
elif(algorithm == "SUANN"):
	#dataset = "POStagSequence"
	dataset = "NewThyroid"
	#trainMultipleNetworks = True	#default: False
	#numberOfNetworks = 5	#default: 1
	
if(debugUseSmallDataset):
	datasetFileNameXstart = "XtrainBatchSmall"
	datasetFileNameYstart = "YtrainBatchSmall"
else:
	datasetFileNameXstart = "XtrainBatch"
	datasetFileNameYstart = "YtrainBatch"
datasetFileNameXend = ".dat"
datasetFileNameYend = ".dat"
datasetFileNameStart = "trainBatch"
datasetFileNameEnd = ".dat"


	
		
def neuralNetworkPropagation(x, networkIndex=1):
	if(algorithm == "SANI"):
		pred = SANItf2_algorithmSANI.neuralNetworkPropagationSANI(x)
	elif(algorithm == "ANN"):
		pred = SANItf2_algorithmANN.neuralNetworkPropagationANN(x, networkIndex)
	elif(algorithm == "CANN"):
		pred = SANItf2_algorithmCANN.neuralNetworkPropagationCANN(x, networkIndex)
	elif(algorithm == "SUANN"):
		pred = SANItf2_algorithmSUANN.neuralNetworkPropagationSUANN(x, networkIndex)
	return pred
	

def executeLearning(x, y, networkIndex=1):
	if(algorithm == "CANN"):
		#learning algorithm embedded in forward propagation
		if(trainHebbianBackprop):
			pred = SANItf2_algorithmCANN.neuralNetworkPropagationCANNtrain(x, y, networkIndex, trainHebbianBackprop=True, trainHebbianLastLayerSupervision=True)
		else:
			pred = SANItf2_algorithmCANN.neuralNetworkPropagationCANNtrain(x, y, networkIndex, trainHebbianForwardprop=True, trainHebbianLastLayerSupervision=True)
	elif(algorithm == "SUANN"):
		#learning algorithm embedded in multiple iterations of forward propagation
		pred = SANItf2_algorithmSUANN.neuralNetworkPropagationSUANNtrain(x, y, networkIndex)

def executeOptimisation(x, y, networkIndex=1):
	with tf.GradientTape() as g:
		pred = neuralNetworkPropagation(x, networkIndex)
		loss = SANItf2_operations.crossEntropy(pred, y, datasetNumClasses, costCrossEntropyWithLogits)
		
	if(algorithm == "SANI"):
		if(algorithmSANI == "sharedModules"):
			if(SANItf2_algorithmSANI.useSparseTensors):
				if(SANItf2_algorithmSANI.performSummationOfSubInputsWeighted):
					if(SANItf2_algorithmSANI.performSummationOfSequentialInputsWeighted):
						trainableVariables = list(SANItf2_algorithmSANI.W.values()) + list(SANItf2_algorithmSANI.Wseq.values())	#+ list(SANItf2_algorithmSANI.B.values()) 
					else:
						trainableVariables = list(SANItf2_algorithmSANI.Wseq.values())
				else:
					if(SANItf2_algorithmSANI.performSummationOfSequentialInputsWeighted):
						trainableVariables = list(SANItf2_algorithmSANI.W.values()) #+ list(SANItf2_algorithmSANI.B.values())
					else:
						trainableVariables = list()	
			else:
				if(SANItf2_algorithmSANI.performSummationOfSequentialInputsWeighted):
					trainableVariables = list(SANItf2_algorithmSANI.W.values()) + list(SANItf2_algorithmSANI.Wseq.values()) + list(SANItf2_algorithmSANI.Bseq.values())	#+ list(SANItf2_algorithmSANI.B.values()) 
				else:
					trainableVariables = list(SANItf2_algorithmSANI.Wseq.values()) + list(SANItf2_algorithmSANI.Bseq.values())
					#trainableVariables = list(SANItf2_algorithmSANI.Wseq.values())
					
		elif(algorithmSANI == "repeatedModules"):
			if(SANItf2_algorithmSANI.allowMultipleSubinputsPerSequentialInput):
				if(SANItf2_algorithmSANI.performSummationOfSequentialInputsWeighted):
					if(SANItf2_algorithmSANI.performSummationOfSubInputsWeighted):
						trainableVariables = list(SANItf2_algorithmSANI.W.values()) + list(SANItf2_algorithmSANI.Wseq.values())
						#trainableVariables = list(SANItf2_algorithmSANI.W.values()) + list(SANItf2_algorithmSANI.B.values()) + list(SANItf2_algorithmSANI.Wseq.values()) + list(SANItf2_algorithmSANI.Bseq.values())
					else:
						trainableVariables = list(SANItf2_algorithmSANI.W.values())
						#trainableVariables = list(SANItf2_algorithmSANI.W.values()) + list(SANItf2_algorithmSANI.B.values())
				else:
					if(SANItf2_algorithmSANI.performSummationOfSubInputsWeighted):
						trainableVariables = list(SANItf2_algorithmSANI.Wseq.values())
						#trainableVariables = list(SANItf2_algorithmSANI.Wseq.values()) + list(SANItf2_algorithmSANI.Bseq.values())
					else:
						print("error: allowMultipleSubinputsPerSequentialInput && !performSummationOfSequentialInputsWeighted && !performSummationOfSubInputsWeighted")
			else:
				if(SANItf2_algorithmSANI.performSummationOfSequentialInputsWeighted):
					trainableVariables = list(SANItf2_algorithmSANI.W.values())
					#trainableVariables = list(SANItf2_algorithmSANI.W.values()) + list(SANItf2_algorithmSANI.B.values())
				else:
					print("error: !allowMultipleSubinputsPerSequentialInput && !performSummationOfSequentialInputsWeighted")
	elif(algorithm == "ANN"):
		Wlist = []
		Blist = []
		for l in range(1, numberOfLayers+1):
			Wlist.append(SANItf2_algorithmANN.W[generateParameterNameNetwork(networkIndex, l, "W")])
			Blist.append(SANItf2_algorithmANN.B[generateParameterNameNetwork(networkIndex, l, "B")])
		trainableVariables = Wlist + Blist

	gradients = g.gradient(loss, trainableVariables)
	
	optimizer.apply_gradients(zip(gradients, trainableVariables))




#generate network parameters based on dataset properties:

datasetNumExamplesTemp = 0
datasetNumFeatures = 0
datasetNumClasses = 0

fileIndexTemp = 0
fileIndexStr = str(fileIndexTemp).zfill(4)
datasetType1FileNameX = datasetFileNameXstart + fileIndexStr + datasetFileNameXend
datasetType1FileNameY = datasetFileNameYstart + fileIndexStr + datasetFileNameYend
datasetType2FileName = datasetFileNameStart + fileIndexStr + datasetFileNameEnd

numberOfLayers = 0
if(dataset == "POStagSequence"):
	datasetNumFeatures, datasetNumClasses, datasetNumExamplesTemp, train_xTemp, train_yTemp, test_xTemp, test_yTemp = SANItf2_loadDataset.loadDatasetType1(datasetType1FileNameX, datasetType1FileNameY)
elif(dataset == "POStagSentence"):
	numberOfFeaturesPerWord, paddingTagIndex, datasetNumFeatures, datasetNumClasses, datasetNumExamplesTemp, train_xTemp, train_yTemp, test_xTemp, test_yTemp = SANItf2_loadDataset.loadDatasetType3(datasetType1FileNameX, generatePOSunambiguousInput, onlyAddPOSunambiguousInputToTrain, useSmallSentenceLengths)
elif(dataset == "NewThyroid"):
	datasetNumFeatures, datasetNumClasses, datasetNumExamplesTemp, train_xTemp, train_yTemp, test_xTemp, test_yTemp = SANItf2_loadDataset.loadDatasetType2(datasetType2FileName)



#Model constants
num_input_neurons = datasetNumFeatures  #train_x.shape[1]
num_output_neurons = datasetNumClasses

if(algorithm == "SANI"):
	if(dataset == "POStagSentence"):
		SANItf2_algorithmSANI.defineTrainingParametersSANIsharedModules(numberOfFeaturesPerWord, paddingTagIndex)
	learningRate, trainingSteps, batchSize, displayStep, numEpochs = SANItf2_algorithmSANI.defineTrainingParametersSANI(dataset, trainMultipleFiles)
	SANItf2_algorithmSANI.defineNetworkParametersSANI(num_input_neurons, num_output_neurons, datasetNumFeatures, dataset, trainMultipleFiles, useSmallSentenceLengths)
	SANItf2_algorithmSANI.defineNeuralNetworkParametersSANI()
elif(algorithm == "ANN"):
	learningRate, trainingSteps, batchSize, displayStep, numEpochs = SANItf2_algorithmANN.defineTrainingParametersANN(dataset, trainMultipleFiles)
	numberOfLayers = SANItf2_algorithmANN.defineNetworkParametersANN(num_input_neurons, num_output_neurons, datasetNumFeatures, dataset, trainMultipleFiles, numberOfNetworks)
	SANItf2_algorithmANN.defineNeuralNetworkParametersANN()
elif(algorithm == "CANN"):
	learningRate, trainingSteps, batchSize, displayStep, numEpochs = SANItf2_algorithmCANN.defineTrainingParametersCANN(dataset, trainMultipleFiles)
	numberOfLayers = SANItf2_algorithmCANN.defineNetworkParametersCANN(num_input_neurons, num_output_neurons, datasetNumFeatures, dataset, trainMultipleFiles, numberOfNetworks)
	SANItf2_algorithmCANN.defineNeuralNetworkParametersCANN()
elif(algorithm == "SUANN"):
	learningRate, trainingSteps, batchSize, displayStep, numEpochs = SANItf2_algorithmSUANN.defineTrainingParametersSUANN(dataset, trainMultipleFiles)
	numberOfLayers = SANItf2_algorithmSUANN.defineNetworkParametersSUANN(num_input_neurons, num_output_neurons, datasetNumFeatures, dataset, trainMultipleFiles, numberOfNetworks)
	SANItf2_algorithmSUANN.defineNeuralNetworkParametersSUANN()		
		
#define epochs:
			
fileIndexFirst = -1
fileIndexLast = -1
if(trainMultipleFiles):
	fileIndexFirst = 0
	if(useSmallSentenceLengths):
		fileIndexLast = 11
	else:
		fileIndexLast = 1202
else:
	fileIndexFirst = 0 
	fileIndexLast = 0

if(algorithm == "SUANN"):
	noisySampleGeneration, noisySampleGenerationNumSamples, noiseStandardDeviation = SANItf2_algorithmSUANN.getNoisySampleGenerationNumSamples()
	if(noisySampleGeneration):
		batchXmultiples = tf.constant([noisySampleGenerationNumSamples, 1], tf.int32)
		batchYmultiples = tf.constant([noisySampleGenerationNumSamples], tf.int32)
		randomNormal = tf.initializers.RandomNormal()	#tf.initializers.RandomUniform(minval=-1, maxval=1)
		
# Stochastic gradient descent optimizer.
optimizer = tf.optimizers.SGD(learningRate)
	
for e in range(numEpochs):

	print("epoch e = ", e)
	
	fileIndexArray = np.arange(fileIndexFirst, fileIndexLast+1, 1)
	#print("fileIndexArray = " + str(fileIndexArray))
	np.random.shuffle(fileIndexArray)
	fileIndexShuffledArray = fileIndexArray
	#print("fileIndexShuffledArray = " + str(fileIndexShuffledArray))
	
	for fileIndex in fileIndexShuffledArray:	#range(fileIndexFirst, fileIndexLast+1):
				
		datasetNumExamples = 0

		fileIndexStr = str(fileIndex).zfill(4)
		datasetType1FileNameX = datasetFileNameXstart + fileIndexStr + datasetFileNameXend
		datasetType1FileNameY = datasetFileNameYstart + fileIndexStr + datasetFileNameYend
		datasetType2FileName = datasetFileNameStart + fileIndexStr + datasetFileNameEnd
		
		if(dataset == "POStagSequence"):
			datasetNumFeatures, datasetNumClasses, datasetNumExamples, train_x, train_y, test_x, test_y = SANItf2_loadDataset.loadDatasetType1(datasetType1FileNameX, datasetType1FileNameY)
		if(dataset == "POStagSentence"):
			numberOfFeaturesPerWord, paddingTagIndex, datasetNumFeatures, datasetNumClasses, datasetNumExamples, train_x, train_y, test_x, test_y = SANItf2_loadDataset.loadDatasetType3(datasetType1FileNameX, generatePOSunambiguousInput, onlyAddPOSunambiguousInputToTrain, useSmallSentenceLengths)
		elif(dataset == "NewThyroid"):
			#print("dataset NewThyroid")
			datasetNumFeatures, datasetNumClasses, datasetNumExamples, train_x, train_y, test_x, test_y = SANItf2_loadDataset.loadDatasetType2(datasetType2FileName)

		shuffleSize = datasetNumExamples	#10*batchSize
		trainData = tf.data.Dataset.from_tensor_slices((train_x, train_y))
		trainData = trainData.repeat().shuffle(shuffleSize).batch(batchSize).prefetch(1)	#do not repeat
				
		for batchIndex, (batchX, batchY) in enumerate(trainData.take(trainingSteps), 1):
	
			if(algorithm == "SUANN"):
				if(noisySampleGeneration):
					if(batchSize != 1):	#batchX.shape[0]
						print("error: noisySampleGeneration && batchSize != 1")
						exit()
					batchX = tf.tile(batchX, batchXmultiples)
					batchY = tf.tile(batchY, batchYmultiples)
					batchXnoise = tf.math.multiply(tf.constant(randomNormal(batchX.shape), tf.float32), noiseStandardDeviation)
					batchX = tf.math.add(batchX, batchXnoise)
					#print("batchX = ", batchX)
					#print("batchY = ", batchY)
					
			predNetworkAverage = tf.Variable(tf.zeros(datasetNumClasses))
			
			for networkIndex in range(1, numberOfNetworks+1):
			
				if(algorithm == "ANN"):
					executeOptimisation(batchX, batchY, networkIndex)
					if(batchIndex % displayStep == 0):
						pred = neuralNetworkPropagation(batchX, networkIndex)
						#print("pred.shape = ", pred.shape)
						loss = SANItf2_operations.crossEntropy(pred, batchY, datasetNumClasses, costCrossEntropyWithLogits)
						acc = SANItf2_operations.calculateAccuracy(pred, batchY)
						print("networkIndex: %i, batchIndex: %i, loss: %f, accuracy: %f" % (networkIndex, batchIndex, loss, acc))
						predNetworkAverage = predNetworkAverage + pred
				elif(algorithm == "CANN"):
					batchYoneHot = tf.one_hot(batchY, depth=datasetNumClasses)
					executeLearning(batchX, batchYoneHot, networkIndex)
					if(batchIndex % displayStep == 0):
						pred = neuralNetworkPropagation(batchX, networkIndex)
						loss = SANItf2_operations.crossEntropy(pred, batchY, datasetNumClasses, costCrossEntropyWithLogits)
						acc = SANItf2_operations.calculateAccuracy(pred, batchY)
						print("networkIndex: %i, batchIndex: %i, loss: %f, accuracy: %f" % (networkIndex, batchIndex, loss, acc))
						predNetworkAverage = predNetworkAverage + pred
				elif(algorithm == "SUANN"):
					executeLearning(batchX, batchY, networkIndex)
					if(batchIndex % displayStep == 0):
						pred = neuralNetworkPropagation(batchX, networkIndex)
						loss = SANItf2_operations.crossEntropy(pred, batchY, datasetNumClasses, costCrossEntropyWithLogits)
						acc = SANItf2_operations.calculateAccuracy(pred, batchY)
						print("networkIndex: %i, batchIndex: %i, loss: %f, accuracy: %f" % (networkIndex, batchIndex, loss, acc))
						predNetworkAverage = predNetworkAverage + pred
				elif(algorithm == "SANI"):
					#learning algorithm not yet implemented:
					if(batchSize > 1):
						pred = neuralNetworkPropagation(batchX)
					if(batchIndex % displayStep == 0):
						pred = neuralNetworkPropagation(batchX)
						acc = tf.reduce_mean(tf.dtypes.cast(pred, tf.float32))
						print("batchIndex: %i, accuracy: %f" % (batchIndex, acc))

						
			if(batchIndex % displayStep == 0):
				if(trainMultipleNetworks):
					predNetworkAverage = predNetworkAverage / numberOfNetworks
					loss = SANItf2_operations.crossEntropy(predNetworkAverage, batchY, datasetNumClasses, costCrossEntropyWithLogits)
					acc = SANItf2_operations.calculateAccuracy(predNetworkAverage, batchY)
					print("batchIndex: %i, loss: %f, accuracy: %f" % (batchIndex, loss, acc))	
					
		
		predNetworkAverageAll = tf.Variable(tf.zeros([test_y.shape[0], datasetNumClasses]))
		for networkIndex in range(1, numberOfNetworks+1):
			if(algorithm == "ANN"):
				pred = neuralNetworkPropagation(test_x, networkIndex)	#test_x batch may be too large to propagate simultaneously and require subdivision
				print("Test Accuracy: networkIndex: %i, %f" % (networkIndex, SANItf2_operations.calculateAccuracy(pred, test_y)))
				predNetworkAverageAll = predNetworkAverageAll + pred
			elif(algorithm == "CANN"):
				pred = neuralNetworkPropagation(test_x, networkIndex)
				print("Test Accuracy: networkIndex: %i, %f" % (networkIndex, SANItf2_operations.calculateAccuracy(pred, test_y)))
				predNetworkAverageAll = predNetworkAverageAll + pred
			elif(algorithm == "SUANN"):
				pred = neuralNetworkPropagation(test_x, networkIndex)
				print("Test Accuracy: networkIndex: %i, %f" % (networkIndex, SANItf2_operations.calculateAccuracy(pred, test_y)))
				predNetworkAverageAll = predNetworkAverageAll + pred
			elif(algorithm == "SANI"):
				#learning algorithm not yet implemented:
				pythonDummy = 1

		if(trainMultipleNetworks):
				predNetworkAverageAll = predNetworkAverageAll / numberOfNetworks
				#print("predNetworkAverageAll", predNetworkAverageAll)
				acc = SANItf2_operations.calculateAccuracy(predNetworkAverageAll, test_y)
				print("Test Accuracy: %f" % (acc))
