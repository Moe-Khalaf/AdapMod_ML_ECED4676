# -*- coding: utf-8 -*-
"""ChannelAssessmentProject.ipynb

# Channel Assessment Model Training
## 1. Introduction
This notebook contains the process for both generating a dataset for channel assessment, as well as the training of a model. This work is being done with the purpose of complimenting the proposed adaptive modulation architecture mentioned in the project report.
"""

import numpy as np
import pandas as pd
import random
from google.colab import drive
import seaborn as sns
import matplotlib.pyplot as plt
drive.mount('/content/drive') # Mounting the Drive

"""## 2. User Defined Functions
The following functions are designed wih the intent of generating the channel assessment dataset. Each data sample contains a signal with channel conditions applied to it, a measurement of the signal to noise ratio, and a measurement of the multipath applied. In this case, the signal is the input, or "features", while the channel conditions are the labels.
"""

# Function Definitions
def generate_random_bits(len):
    """
    Generate a bitstream to transmit.

    :param len: Length of the bitstream.
    :return: NumPy array containing the bitstream.
    """
    return np.array([random.randint(0, 1) for i in range(len)])

def generate_BFSK_Signal_vectorized(bitstream, f1, f2, fs, fc, T_symbol):
    """
    Generate a BFSK signal using vectorization.

    :param bitstream: Bitstream to modulate.
    :param f1: Frequency representing '0'.
    :param f2: Frequency representing '1'.
    :param fs: Sampling frequency.
    :param T_symbol: Symbol duration.
    :return: BFSK signal as a numpy array.
    """
    num_bits = len(bitstream)
    t = np.arange(0, num_bits * T_symbol, 1/fs)  # Full time vector for all symbols

    # Initialize the waveform
    f_waveform = np.zeros(len(t), dtype=complex)

    # Create the waveform for each bit in the bitstream
    for i, bit in enumerate(bitstream):
        start_index = i * int(T_symbol * fs)
        end_index = start_index + int(T_symbol * fs)
        frequency = f1 if bit == 0 else f2
        f_waveform[start_index:end_index] = np.exp(2j * np.pi * frequency * t[start_index:end_index])

    # Upconvert with Carrier Frequency
    signal_upconverted = f_waveform*np.exp(2j*np.pi*fc*t)
    return signal_upconverted

def apply_multipath(signal, delays, attenuations, sampling_freq):
    """
    Apply multipath effects to a signal without extending its length.

    :param signal: The original signal (numpy array).
    :param delays: List of delays for each path in seconds.
    :param attenuations: List of attenuation factors for each path (0 to 1).
    :param sampling_freq: Sampling frequency of the signal.
    :return: Signal with multipath effects applied.
    """
    multipath_signal = np.copy(signal)  # Start with the original signal

    # Add each delayed and attenuated path
    for delay, attenuation in zip(delays, attenuations):
        delay_samples = int(delay * sampling_freq)
        delayed_signal = np.zeros(len(signal))
        delayed_signal[:len(signal) - delay_samples] = signal[delay_samples:] * attenuation
        multipath_signal += delayed_signal

    return multipath_signal

def apply_awgn_snr(signal, snr_db): # Applies addiive white gausian noise to signal
    """
    Apply Additive White Gaussian Noise to a signal based on a given SNR in dB.

    :param signal: The original signal (numpy array).
    :param snr_db: Desired Signal-to-Noise Ratio in dB.
    :return: Signal with AWGN applied.
    """
    # Calculate signal power
    signal_power = np.mean(np.abs(signal)**2)

    # Convert SNR from dB to linear scale
    snr_linear = 10 ** (snr_db / 10)

    # Calculate noise power based on SNR
    noise_power = signal_power / snr_linear

    # Generate white Gaussian noise
    noise = np.random.normal(0, np.sqrt(noise_power), len(signal))

    # Add noise to the signal
    noisy_signal = signal + noise

    return noisy_signal

def generate_random_mp_conditions():
    """
    Generate a random set of multipath conditions with ordered delays and attenuations scaling linearly with delay.

    :return: List of multipath conditions.
    """
    alpha = -0.02645 # Attenuation constant (Approximation based of of kinslers fundamentals of acoustics)
    # Generate number of paths (Can later be modified to be random in future work)
    num_paths = 5

    # Generate and sort random delays
    delays = np.sort(np.random.uniform(0, 0.04, num_paths))

    # Calculate attenuations that decay exponentially with delay
    min_attenuation = np.random.uniform(0.01, 0.6)
    attenuations = [min_attenuation * np.exp(-delay * alpha/max(delays)) for delay in delays]

    # Ensure that attenuations do not exceed min_attenuation
    attenuations = [max(att, min_attenuation) for att in attenuations]

    return delays, attenuations

"""## 3. Dataset generation
The following code generates a the dataset as a pandas dataframe. Here, the same BFSK signal is used in all data samples as a pilot signal. Each sample then only varies in the channel conditions.
"""

# Parameters
num_signals = 3000  # Number of signals to generate
bitstream_length = 25  # Length of each bitstream

# BFSK Parameters
f1, f2, fs, fc, T_symbol = -2500, 2500, 30000, 10000, 0.02



# Initialize DataFrame with expanded columns for delays and attenuations
columns = ['BFSK_Signal_Real', 'BFSK_Signal_Imag'] + [f'Delay_{i+1}' for i in range(5)] + [f'Attenuation_{i+1}' for i in range(5)] + ['SNR']
df = pd.DataFrame(columns=columns)


# Generate Random Bitstream
bitstream = generate_random_bits(bitstream_length)

# Generate BFSK signal
bfsk_signal = generate_BFSK_Signal_vectorized(bitstream, f1, f2, fs, fc, T_symbol)

# Generate Samples
for _ in range(num_signals):
    # Generate random channel conditions
    delays, attenuations = generate_random_mp_conditions()
    snr_db = np.random.uniform(0, 30)

    # Apply channel conditions
    multipath_signal = apply_multipath(bfsk_signal, delays, attenuations, fs)

    # Apply AWGN
    final_signal = apply_awgn_snr(multipath_signal, snr_db)
    real_part = [num.real for num in final_signal]
    imag_part = [num.imag for num in final_signal]

    # Create a new row and append it
    new_row = {
        'BFSK_Signal_Real': real_part,
        'BFSK_Signal_Imag': imag_part,
        **{f'Delay_{i+1}': delays[i] for i in range(5)},
        **{f'Attenuation_{i+1}': attenuations[i] for i in range(5)},
        'SNR': snr_db
    }
    df = pd.concat([df, pd.DataFrame([new_row], columns=columns)], ignore_index=True)
df

"""The data is separated here into a features dataframe and a labels dataframe"""

# Expand the real and imaginary parts into separate DataFrames
real_df = pd.DataFrame(df['BFSK_Signal_Real'].tolist())
imag_df = pd.DataFrame(df['BFSK_Signal_Imag'].tolist())

# Concatenate the two DataFrames Horizontally
combined_df = pd.concat([real_df, imag_df], axis=1)
# Create the label data frame
combined_df_labels = df[[f'Delay_{i+1}' for i in range(5)] +
                        [f'Attenuation_{i+1}' for i in range(5)] +
                        ['SNR']]

# Export the dataframes to csv files
combined_df.to_csv('/content/drive/MyDrive/Data/channelassessment_dataset.csv')
combined_df_labels.to_csv('/content/drive/MyDrive/Data/channelassessment_labels.csv')

"""# 4. Model Training
The following code executes the training of the channel assessment model based off of the generated dataset
"""

from keras.models import Sequential, Model
from keras.layers import Input, Conv1D, MaxPooling1D, Flatten, Dense, Dropout, concatenate
from keras.metrics import MeanSquaredError
import keras.backend as K
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import confusion_matrix, classification_report
import ast

# Load in the Dataset
features = pd.read_csv('/content/drive/MyDrive/Data/channelassessment_dataset.csv')
features = features.drop(features.columns[0], axis=1)
labels = pd.read_csv('/content/drive/MyDrive/Data/channelassessment_labels.csv')
labels = labels.drop(labels.columns[0], axis=1)
labels

def regression_accuracy(y_true, y_pred, threshold=0.1):
    """
    A custom accuracy metric for regression tasks.
    Considers predictions within a certain range of the actual values as accurate.
    :param y_true: The actual values.
    :param y_pred: The predicted values.
    :param threshold: The acceptable range.
    """
    return K.mean(K.less_equal(K.abs(y_true - y_pred), threshold), axis=-1)

"""This following function defines the creation of the CNN model that will be used for channel assessment. One thing thats worth noting is how the model splits into three branches for the three predictions. All branches share the convolutional layers. Where they differ is after the convolutional layers.

The branch that predicts the multipath delays takes in the output of the convolutional layers and feeds that output to a dense layer, followed by the final output.

The branch that predicts the multipath attenuations takes in a combination of the convolutional layer output, and the delay branch output and then sends the combination of the two through several dense layers. The reason this has been done is because it was desirable to factor in the results for the delay predictions into the preditions of attenuation in case there was a relationship that could be taken advantage of.

The branch that predicts snr goes straight to the output following the convolution layers.
"""

def create_multi_output_model(input_shape, num_delays=5, num_attenuations=5):
    # Input layer
    input_layer = Input(shape=input_shape)

    # Shared Convolutional layers
    x = Conv1D(filters=128, kernel_size=3, activation='relu')(input_layer)
    x = MaxPooling1D(pool_size=2)(x)
    x = Dropout(0.2)(x)

    x = Conv1D(filters=64, kernel_size=3, activation='relu')(x)
    x = MaxPooling1D(pool_size=2)(x)
    x = Dropout(0.2)(x)

    x = Conv1D(filters=64, kernel_size=3, activation='relu')(x)
    x = MaxPooling1D(pool_size=2)(x)
    x = Dropout(0.2)(x)

    x = Conv1D(filters=32, kernel_size=3, activation='relu')(x)
    x = MaxPooling1D(pool_size=2)(x)
    x = Dropout(0.2)(x)

    x = Conv1D(filters=16, kernel_size=3, activation='relu')(x)
    x = MaxPooling1D(pool_size=2)(x)
    x = Dropout(0.2)(x)

    x = Conv1D(filters=8, kernel_size=3, activation='relu')(x)
    x = MaxPooling1D(pool_size=2)(x)
    x = Dropout(0.2)(x)

    x = Flatten()(x)

    # Branch for Delays
    x_delays = Dense(64, activation='relu')(x)
    delays_output = Dense(num_delays, name='delays_output')(x_delays)

    # Combine the output of the delays branch with the flattened features
    combined_features = concatenate([x, delays_output])

    # Enhanced branch for attenuations
    x_attenuations = Dense(128, activation='relu')(combined_features)  # First dense layer with more neurons
    x_attenuations = Dropout(0.3)(x_attenuations)  # Dropout layer for regularization
    x_attenuations = Dense(64, activation='relu')(x_attenuations)  # Second dense layer
    x_attenuations = Dropout(0.3)(x_attenuations)
    x_attenuations = Dense(32, activation='relu')(x_attenuations)  # Third dense layer
    attenuations_output = Dense(num_attenuations, name='attenuations_output')(x_attenuations)

    # Branch for SNR
    snr_output = Dense(1, name='snr_output')(x)  # Output for SNR

    # Define the model
    model = Model(inputs=input_layer, outputs=[snr_output, delays_output, attenuations_output])

    # Compile the model
    model.compile(optimizer='adam',
                  loss={'snr_output': 'mse', 'delays_output': 'mse', 'attenuations_output': 'mse'},
                  metrics={'snr_output': regression_accuracy, 'delays_output': regression_accuracy, 'attenuations_output': regression_accuracy})

    return model

"""The following code divides up the data between training and validation"""

time_steps = features.shape[1]
input_shape = (time_steps, 1)
model = create_multi_output_model(input_shape)

X_train, X_val, y_train, y_val = train_test_split(
    features,
    combined_df_labels,
    test_size=0.2,  # 20% of the data will be used for validation
    random_state=42  # for reproducibility of results
)

# Extracting individual label sets from the training and validation sets
y_train_snr = y_train['SNR']
y_train_delays = y_train[[f'Delay_{i+1}' for i in range(5)]]
y_train_attenuations = y_train[[f'Attenuation_{i+1}' for i in range(5)]]

y_val_snr = y_val['SNR']
y_val_delays = y_val[[f'Delay_{i+1}' for i in range(5)]]
y_val_attenuations = y_val[[f'Attenuation_{i+1}' for i in range(5)]]

"""The code is trained here."""

# Train the model
history = model.fit(
    X_train,
    {'snr_output': y_train_snr, 'delays_output': y_train_delays, 'attenuations_output': y_train_attenuations},
    epochs=30,  # Number of epochs, adjust as needed
    batch_size=32,  # Batch size, adjust as needed
    validation_data=(X_val, {'snr_output': y_val_snr, 'delays_output': y_val_delays, 'attenuations_output': y_val_attenuations})
)

"""## 5. Evaluation and Results
From the above results, it can be seen that the predictions for Multipath are good, however, the prediction for SNR has little to no accuracy. From this, we can say that this model can be used for multipath assessment, however, more traditional methods of noise measurement may be more suitable. Ultimately however, in future work, tweaks can be made in order to better determine the attenuation of the multipath signals.

In summary
- SNR Validation Accuracy: 0.00%
- Multipath Delay Validation Accuracy: 99.99%
- Multipath Attenuation Validation Accuracy: 39.53%
"""
