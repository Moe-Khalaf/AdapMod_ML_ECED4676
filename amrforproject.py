# -*- coding: utf-8 -*-
"""AMRforProject.ipynb

Automatically generated by Colaboratory.



# Adaptive Modulation Project: Automatic Modulation Recognition Training
## Prepared by: Mohammedali Khalaf

This Jupyter Notebook contains the work in order to create an automatic modulation recognition model. The reason that thsi is being done is to faclitate the completion of the ECED 4676 Adaptive Modulation Project (2023).

This model will differentiate between three modulation schemes
- BFSK
- 4FSK
- 8FSK
These modulation schemes were the ones selected to be used in the adaptive modulation system and as such will be the ones considered in training this model.

With regards to the dataset, the dataset of choice for this project is HisarMod. This dataset is available on IEEE DataPort and its citation is given below.

Kürşat Tekbıyık, Cihat Keçeci, Ali Rıza Ekti, Ali Görçin, Güneş Karabulut Kurt, October 27, 2019, "HisarMod: A new challenging modulated signals dataset", IEEE Dataport, doi: https://dx.doi.org/10.21227/8k12-2g70.

Basic libraries are imported below.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from keras.models import Sequential
from keras.layers import Conv1D, MaxPooling1D, Flatten, Dense
from google.colab import drive
drive.mount('/content/drive') # Mounting the Drive

"""The dataset is loaded in below amd pre-processed in order to have the correct foramt of data. The rows have been selected such that only samples from the selected modulation schemes are considered below."""

# Below is are the directories for the data file and label file
train_data_file = '/content/drive/MyDrive/Data/HisarMod/train_data.csv'

# The ranges below describe the desired data chunks from the data to be used for this assignment.
ranges = {
'8FSK': [
    (266001, 267000),
    (292001, 293000),
    (318001, 319000),
    (344001, 345000),
    (370001, 371000),
    (396001, 397000),
    (422001, 423000),
    (448001, 449000),
    (474001, 475000),
    (500001, 501000)
],
'4FSK': [
    (265001, 266000),
    (291001, 292000),
    (317001, 318000),
    (343001, 344000),
    (369001, 370000),
    (395001, 396000),
    (421001, 422000),
    (447001, 448000),
    (473001, 474000),
    (499001, 500000)
],
'2FSK': [
    (264001, 265000),
    (290001, 291000),
    (316001, 317000),
    (342001, 343000),
    (368001, 369000),
    (394001, 395000),
    (420001, 421000),
    (446001, 447000),
    (472001, 473000),
    (498001, 499000)
]
}

# Initialize empty dataframe
Raw_Data = pd.DataFrame()

# Load chunks into the desired DataFrame
for modulation, chunks in ranges.items():
  for start, end in chunks:
    chunk_dataframe = pd.read_csv(train_data_file, header=None, skiprows=start-1, nrows=end-start+1)
    print("Chunk Completed: " + modulation) # Provide a method to see the progress of the execution
    # Adding a column for labels
    chunk_dataframe['Label'] = modulation

    # Append to main dataframe
    Raw_Data = pd.concat([Raw_Data, chunk_dataframe], ignore_index=True)
    Raw_Data

# Print Dataframe to verify success
Raw_Data

"""The data is then preprocessed below in order to format it properly."""

cols = ['Label'] + [col for col in Raw_Data if col != 'Label'] #
Raw_Data = Raw_Data[cols]
Raw_Data

Raw_Data.to_csv('/content/drive/MyDrive/Data/HisarMod/train_data_project.csv')

Raw_Data = pd.read_csv('/content/drive/MyDrive/Data/HisarMod/train_data_project.csv')
Raw_Data = Raw_Data.drop(Raw_Data.columns[0], axis=1)

# Convert the data from str to complex
def convert_to_complex(s):
    try:
        return complex(s.replace('i', 'j'))
    except ValueError:
        print(f"Problematic string: {s}")
        return 0j

# Apply the function on each cell of the DataFrame for selected columns
Raw_Data.iloc[:, 1:] = Raw_Data.iloc[:, 1:].applymap(convert_to_complex)
Raw_Data # Verify Success

# Split complex numbers into I and Q
for col in Raw_Data.columns[1:]:
  Raw_Data[col + '_I'] = Raw_Data[col].apply(lambda x: x.real)
  Raw_Data[col + '_Q'] = Raw_Data[col].apply(lambda x: x.imag)
Raw_Data # Print to verify success
Raw_Data

Raw_Data = Raw_Data.drop(columns=Raw_Data.columns[1:1+len(Raw_Data.columns)//3])

Raw_Data.to_csv('/content/drive/MyDrive/Data/HisarMod/train_data_project_IQSplit.csv')

"""## Model Training
### Cross Validation
The model is cross validated below for assurance in its quality.
"""

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import confusion_matrix, classification_report

df = pd.read_csv('/content/drive/MyDrive/Data/HisarMod/train_data_project_IQSplit.csv')
df = df.drop(df.columns[0], axis=1)
df

from keras.layers import Dropout
# Separate Labels and Features
labels = df.iloc[:, 0].values
features = df.iloc[:, 1:].values

# Convert labels to integers
label_encoder = LabelEncoder()
integer_labels = label_encoder.fit_transform(labels)

# Normalize features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Reshape data for 1D CNN
scaled_features = np.expand_dims(scaled_features, axis=2)

# Define the 1D CNN model in a function for reusability
def create_model(input_shape):
    model = Sequential()
    model.add(Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=input_shape))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Dropout(0.2))
    model.add(Conv1D(filters=32, kernel_size=3, activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Dropout(0.2))
    model.add(Conv1D(filters=16, kernel_size=3, activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(64, activation='relu'))
    model.add(Dense(len(np.unique(labels)), activation='softmax'))
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# K-fold cross-validation
n_folds = 5
skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

# Prepare Empty Stores for Results
scores = []
cms = []
reports = []
# Cross Validated Training is happening in this for loop
for train_index, val_index in skf.split(scaled_features, integer_labels):
    X_train, X_val = scaled_features[train_index], scaled_features[val_index]
    y_train, y_val = integer_labels[train_index], integer_labels[val_index]

    model = create_model((X_train.shape[1], 1))
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_val, y_val))

    # Evaluate model on validation data
    score = model.evaluate(X_val, y_val, verbose=0)
    scores.append(score[1])  # assuming score[1] is accuracy

    # Predict on validation data
    y_pred = model.predict(X_val)
    y_pred_int = np.argmax(y_pred, axis=1)

    # Compute confusion matrix and classification report
    cm = confusion_matrix(y_val, y_pred_int)
    report = classification_report(y_val, y_pred_int, target_names=label_encoder.classes_)
    # Add Current Folds Results to the empty stores for results we already made
    # The results are then printed together at once later on.
    cms.append(cm)
    reports.append(report)

# Calculate mean and standard deviation of the scores
mean_score = np.mean(scores)
std_score = np.std(scores)

print(f"Mean accuracy over {n_folds}-folds: {mean_score:.4f}")
print(f"Standard deviation: {std_score:.4f}")

# Print confusion matrices and classification reports for each fold
for i, (cm, report) in enumerate(zip(cms, reports)):
    print(f"\nFor fold {i+1}:")
    print("Confusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(report)

import seaborn as sns
classes = label_encoder.classes_

# Print confusion matrices and classification reports for each fold
for i, (cm, report) in enumerate(zip(cms, reports)):
    plt.figure(figsize=(10,7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()

"""The cross validation of the model yielded interesting results. From the classification reports and confusion matrices, it can be seen that there still remain some errors in classification among the samples.

What can be seen is that most of the confusion is between 4FSK and 8FSK. While this could be due to the similarity between them in features, there is another possibility. The few errors may have more likely occured due to higher noise. In previous attempts at AMR, perfect results had been yielded when the samples were of higher SNR. In the previous attempts, the lowest SNR used was 10dB. Here the lowest values are at -2dB and 0dB. This could indicate that what brought forth imperfection here was not the striking similarity between 4FSK and 8FSK, but the higher noise. This is even further evident by the high success rate that still remains.

The nature of the error described above in fact does not cause any major inconvenience. The reason being is that, for higher SNRs, BFSK is going to be selected anyways, and since that is the case, the errors will be negligible as all of the errors are between 4FSK and 8FSK.

Taking the above results into consideration, the model is recreated below and trained off of the whole dataset.
"""

model = create_model((scaled_features.shape[1], 1))
model.fit(scaled_features, integer_labels, epochs=10, batch_size=32)
model.save('/content/drive/MyDrive/Models/AMRProjectModel.h5')
model.save('/content/drive/MyDrive/Models/AMRProjectModel.keras')
from joblib import dump
dump(label_encoder, '/content/drive/MyDrive/Models/AMRProjectLabelEncoder.joblib')
dump(scaler, '/content/drive/MyDrive/Models/AMRProjectScaler.joblib')
