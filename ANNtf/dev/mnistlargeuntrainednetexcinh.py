# -*- coding: utf-8 -*-
"""MNISTlargeUntrainedNetExcInh.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pq3mkfiqpF7Cxmik43QaVxJOKt9dXvQs

##### Copyright 2019 The TensorFlow Authors.
"""

#@title Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""# TensorFlow 2 quickstart for beginners

<table class="tfo-notebook-buttons" align="left">
  <td>
    <a target="_blank" href="https://www.tensorflow.org/tutorials/quickstart/beginner"><img src="https://www.tensorflow.org/images/tf_logo_32px.png" />View on TensorFlow.org</a>
  </td>
  <td>
    <a target="_blank" href="https://colab.research.google.com/github/tensorflow/docs/blob/master/site/en/tutorials/quickstart/beginner.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" />Run in Google Colab</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/tensorflow/docs/blob/master/site/en/tutorials/quickstart/beginner.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" />View source on GitHub</a>
  </td>
  <td>
    <a href="https://storage.googleapis.com/tensorflow_docs/docs/site/en/tutorials/quickstart/beginner.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" />Download notebook</a>
  </td>
</table>

This short introduction uses [Keras](https://www.tensorflow.org/guide/keras/overview) to:

1. Load a prebuilt dataset.
1. Build a neural network machine learning model that classifies images.
2. Train this neural network.
3. Evaluate the accuracy of the model.

This tutorial is a [Google Colaboratory](https://colab.research.google.com/notebooks/welcome.ipynb) notebook. Python programs are run directly in the browser—a great way to learn and use TensorFlow. To follow this tutorial, run the notebook in Google Colab by clicking the button at the top of this page.

1. In Colab, connect to a Python runtime: At the top-right of the menu bar, select *CONNECT*.
2. Run all the notebook code cells: Select *Runtime* > *Run all*.

## Set up TensorFlow

Import TensorFlow into your program to get started:
"""

import tensorflow as tf
print("TensorFlow version:", tf.__version__)
from keras import backend as K

"""If you are following along in your own development environment, rather than [Colab](https://colab.research.google.com/github/tensorflow/docs/blob/master/site/en/tutorials/quickstart/beginner.ipynb), see the [install guide](https://www.tensorflow.org/install) for setting up TensorFlow for development.

Note: Make sure you have upgraded to the latest `pip` to install the TensorFlow 2 package if you are using your own development environment. See the [install guide](https://www.tensorflow.org/install) for details.

## Load a dataset

Load and prepare the [MNIST dataset](http://yann.lecun.com/exdb/mnist/). Convert the sample data from integers to floating-point numbers:
"""

mnist = tf.keras.datasets.mnist

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

"""## Build a machine learning model

Build a `tf.keras.Sequential` model by stacking layers.
"""

def activationExcitatory(x):
    return K.maximum(x, 0)

def activationInhibitory(x):
    return -(K.maximum(x, 0))

def excitatoryNeuronInitializer(shape, dtype=None):
    return tf.math.abs(tf.random.normal(shape, dtype=dtype))

def inhibitoryNeuronInitializer(shape, dtype=None):
    return tf.math.negative(tf.math.abs(tf.random.normal(shape, dtype=dtype)))

input_shape = (28, 28)
num_classes = 10

generateLargeNetworkUntrained = True
if(generateLargeNetworkUntrained):
  #only train the last layer
  generateLargeNetworkRatio = 50
  x = tf.keras.layers.Input(shape=input_shape)
  h0 = tf.keras.layers.Flatten()(x)

  h1E = tf.keras.layers.Dense(128*generateLargeNetworkRatio, kernel_initializer=excitatoryNeuronInitializer)(h0)
  h1I = tf.keras.layers.Dense(128*generateLargeNetworkRatio, kernel_initializer=inhibitoryNeuronInitializer)(h0)
  h1E = tf.keras.layers.Activation(activationExcitatory)(h1E)
  h1I = tf.keras.layers.Activation(activationInhibitory)(h1I)
  h1 = tf.keras.layers.Concatenate()([h1E, h1I])

  h2E = tf.keras.layers.Dense(128*generateLargeNetworkRatio, kernel_initializer=excitatoryNeuronInitializer)(h1)
  h2I = tf.keras.layers.Dense(128*generateLargeNetworkRatio, kernel_initializer=inhibitoryNeuronInitializer)(h1)
  h2E = tf.keras.layers.Activation(activationExcitatory)(h2E)
  h2I = tf.keras.layers.Activation(activationInhibitory)(h2I)
  h2 = tf.keras.layers.Concatenate()([h2E, h2I])

  h3E = tf.keras.layers.Dense(128*generateLargeNetworkRatio, kernel_initializer=excitatoryNeuronInitializer)(h2)
  h3I = tf.keras.layers.Dense(128*generateLargeNetworkRatio, kernel_initializer=inhibitoryNeuronInitializer)(h2)
  h3E = tf.keras.layers.Activation(activationExcitatory)(h3E)
  h3I = tf.keras.layers.Activation(activationInhibitory)(h3I)
  h3 = tf.keras.layers.Concatenate()([h3E, h3I])
 
  hLast = h3
  hLast = tf.keras.layers.Lambda(lambda x: tf.keras.backend.stop_gradient(x))(hLast)
  y = tf.keras.layers.Dense(num_classes, activation='softmax')(hLast)
  model = tf.keras.Model(x, y)
  #print(model.summary())
  #model.compile(optimizer=tf.keras.optimizers.RMSprop(epsilon=1e-08), loss='categorical_crossentropy', metrics=['acc'])
  #evaluation accuracy: ? (with 1 or 2 hidden layers)
else:
  generateLargeNetworkRatio = 1
  model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=input_shape),
    tf.keras.layers.Dense(128*generateLargeNetworkRatio, activation='relu'),
    #tf.keras.layers.Dense(128*generateLargeNetworkRatio, activation='relu'),
    tf.keras.layers.Dense(num_classes)
  ])
  #evaluation accuracy: 0.9764

loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

model.compile(optimizer='adam',
              loss=loss_fn,
              metrics=['accuracy'])


print(model.summary())

"""## Train and evaluate your model

Use the `Model.fit` method to adjust your model parameters and minimize the loss: 
"""

model.fit(x_train, y_train, epochs=5)

"""The `Model.evaluate` method checks the models performance, usually on a "[Validation-set](https://developers.google.com/machine-learning/glossary#validation-set)" or "[Test-set](https://developers.google.com/machine-learning/glossary#test-set)"."""

model.evaluate(x_test,  y_test, verbose=2)

"""The image classifier is now trained to ~98% accuracy on this dataset. To learn more, read the [TensorFlow tutorials](https://www.tensorflow.org/tutorials/).

If you want your model to return a probability, you can wrap the trained model, and attach the softmax to it:
"""

probability_model = tf.keras.Sequential([
  model,
  tf.keras.layers.Softmax()
])

probability_model(x_test[:5])

"""## Conclusion

Congratulations! You have trained a machine learning model using a prebuilt dataset using the [Keras](https://www.tensorflow.org/guide/keras/overview) API.

For more examples of using Keras, check out the [tutorials](https://www.tensorflow.org/tutorials/keras/). To learn more about building models with Keras, read the [guides](https://www.tensorflow.org/guide/keras). If you want learn more about loading and preparing data, see the tutorials on [image data loading](https://www.tensorflow.org/tutorials/load_data/images) or [CSV data loading](https://www.tensorflow.org/tutorials/load_data/csv).

"""