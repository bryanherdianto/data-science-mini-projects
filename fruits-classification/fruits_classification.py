# -*- coding: utf-8 -*-
"""fruits-classification

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1eF0C_PpeToNfj8bAh8difBUkq-aD0kEr
"""

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Flatten, Dropout, MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import Callback
from google.colab import files
from keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
import random

# Get project files
!wget https://raw.githubusercontent.com/bryanherdianto/data-science-mini-projects/main/fruits-classification/fruits.zip

!unzip fruits.zip

# Variables for pre-processing
batch_size = 128
IMG_HEIGHT = 100
IMG_WIDTH = 100

# Define paths
dataset_dir = 'fruits'
train_dir = 'train'
validation_dir = 'validation'

fruits = [
    'Watermelon', 'Tomato', 'Strawberry', 'Raspberry', 'Potato Red', 'Pomegranate', 'Plum',
    'Pineapple', 'Pepper Red', 'Pepper Green', 'Pear', 'Peach', 'Passion Fruit', 'Papaya', 'Orange',
    'Onion White', 'Mango', 'Limes', 'Lemon', 'Kiwi', 'Grape Blue', 'Cucumber Ripe', 'Corn', 'Clementine',
    'Cherry', 'Cantaloupe', 'Cactus fruit', 'Blueberry', 'Banana', 'Avocado', 'Apricot', 'Apple Granny Smith',
    'Apple Braeburn'
]

# Create training and validation directories
for category in fruits:
    os.makedirs(os.path.join(train_dir, category), exist_ok=True)
    os.makedirs(os.path.join(validation_dir, category), exist_ok=True)

# Split ratio
train_ratio = 0.8
validation_ratio = 0.2

# Function to split and move files
def split_data(category):
    category_path = os.path.join(dataset_dir, category)
    images = os.listdir(category_path)
    random.shuffle(images)

    total_images = len(images)
    train_size = int(total_images * train_ratio)

    train_images = images[:train_size]
    validation_images = images[train_size:]

    for image in train_images:
        src = os.path.join(category_path, image)
        dst = os.path.join(train_dir, category, image)
        shutil.copy(src, dst)

    for image in validation_images:
        src = os.path.join(category_path, image)
        dst = os.path.join(validation_dir, category, image)
        shutil.copy(src, dst)

# Split the data for each category
for category in fruits:
    split_data(category)

print("Data splitting complete.")

# Get number of files in each directory. The train and validation directories each have the subdirectories of different fruit names.
total_train = sum([len(files) for r, d, files in os.walk(train_dir)])
total_val = sum([len(files) for r, d, files in os.walk(validation_dir)])

print(total_train)
print(total_val)

train_image_generator = ImageDataGenerator(rescale=1./255)
validation_image_generator = ImageDataGenerator(rescale=1./255)

train_data_gen = train_image_generator.flow_from_directory(
    train_dir,
    batch_size=batch_size,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    class_mode='categorical'
)
val_data_gen = validation_image_generator.flow_from_directory(
    validation_dir,
    batch_size=batch_size,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    class_mode='categorical'
)

# Print class distribution in training set
print(train_data_gen.class_indices)
train_class_counts = train_data_gen.classes
print(np.bincount(train_class_counts))

# Print class distribution in validation set
print(val_data_gen.class_indices)
val_class_counts = val_data_gen.classes
print(np.bincount(val_class_counts))

def plotImages(images_arr):
    fig, axes = plt.subplots(len(images_arr), 1, figsize=(5,len(images_arr) * 3))
    for img, ax in zip(images_arr, axes):
        ax.imshow(img)
        ax.axis('off')
    plt.show()

sample_training_images, _ = next(train_data_gen)
plotImages(sample_training_images[:5])

train_image_generator = ImageDataGenerator(
    horizontal_flip = True,
    rescale=1./255,
    shear_range=0.1,
    rotation_range=20,
    width_shift_range=0.1,
    zoom_range=0.1,
    height_shift_range=0.1,
    brightness_range=[0.9, 1.1],
    channel_shift_range=0.05,
    fill_mode='nearest'
)
train_data_gen = train_image_generator.flow_from_directory(
    train_dir,
    batch_size=batch_size,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    class_mode='categorical'
)

augmented_images = [train_data_gen[0][0][0] for i in range(5)]

plotImages(augmented_images)

class MyCallback(Callback):
    def on_epoch_end(self, epoch, logs={}):
        if(logs.get('accuracy') > 0.92):
            print("\nReached 92% accuracy so cancelling training!")
            self.model.stop_training = True

callbacks = MyCallback()

# Number of classes
num_classes = 33

model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(num_classes, activation='softmax')
])

model.summary()

model.compile(optimizer='adam',
              loss=tf.keras.losses.CategoricalCrossentropy(),
              metrics=['accuracy'])

# Variables for training
epochs = 20

tf.keras.backend.clear_session()

history = model.fit(
    train_data_gen,
    steps_per_epoch=total_train//batch_size,
    epochs=epochs,
    validation_data=val_data_gen,
    verbose=2,
    validation_steps=total_val//batch_size,
    callbacks=[callbacks]
)

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Akurasi Model')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# Upload files
fil = files.upload()

# Print class indices
print(train_data_gen.class_indices)

# Predict for each uploaded file
for fn in fil.keys():
    path = fn
    img = image.load_img(path, target_size=(IMG_HEIGHT, IMG_WIDTH))
    imgplot = plt.imshow(img)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0  # Rescale the image

    images = np.vstack([x])
    classes = model.predict(images, batch_size=32)

    # Get the class with the highest probability
    predicted_class_index = np.argmax(classes[0])

    # Get the class label from the index
    class_labels = list(train_data_gen.class_indices.keys())
    predicted_class_label = class_labels[predicted_class_index]

    print(f"Predicted class: {predicted_class_label}")

# Save the model in TF-Lite format
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('model.tflite', 'wb') as f:
    f.write(tflite_model)

print("Model saved in TF-Lite format.")