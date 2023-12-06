# ECED 4676: Deep Learning Driven Adaptive Modulation Model
This repository contains the adaptive modulation project for Dalhousie University ECED4676: Machine Learning for Engineers.

This project was prepared by Mohammedali Khalaf and Rehan Khalid

## Purpose
The purpose of this project is to provide a proof-of-concept for an adaptive modulation system design. Adaptive modulation is essentially the practice of setting up a communication system to be able to assess the environment it is placed in and select the most suitable modulation scheme in real time. The proposed system design utilizes two machine learning models. The proof-of-concept will include these models. Further integration of the system currently falls under "future work".
## Proposed Architecture
The proposed system architecture is displayed below.
![image](https://github.com/Moe-Khalaf/AdapMod_ML_ECED4676/assets/124087656/cf941233-2ddd-4d36-8dcf-949dea0b6e0a)
The system in its current design should follow the following order of operations:
1. The transmitter sends a data packet to the reciever using the currently selected modulation scheme
2. The reciever uses an AI model to assess the modulation scheme of the recieved signal.
3. The reciever uses the correlating demodulation process to demodulate, based on the assessment done by the modualtion recognition model.
4. A pilot signal is sent from the reciever to the transmitter. This signal will always be the same signal
5. At the transmitter side, the signal is recieved and analyzed in order to assess the channel conditions
6. The transmitter selects the next modulation scheme based on the results from the channel assessment
7. The process is repeated from step 1




