# ECED 4676: Deep Learning Driven Adaptive Modulation Model
This repository contains the adaptive modulation project for Dalhousie University ECED4676: Machine Learning for Engineers.

This project was prepared by Mohammedali Khalaf and Rehan Khalid

## Purpose
The purpose of this project is to develop a proof-of-concept for an adaptive modulation system. Adaptive modulation is a method that allows a communication system to dynamically assess its environment and choose the most appropriate modulation scheme in real-time. This system's design features two machine learning models, which are pivotal to the project's proof-of-concept. Although other components of the system have been previously proven effective in many applications, they are not the main focus at this juncture. Their complete integration and further refinement are considered future work, contingent upon the successful demonstration of the machine learning models' functionality in this initial phase.
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
## Machine Learning Models Involved
### Automatic Modulation Recognition
This model employs a 1-dimensional Convolutional Neural Network (CNN) to analyze incoming signals and accurately identify their modulation schemes. The model is trained on the HisarMod dataset, which comprises a diverse collection of signal samples, each annotated with the corresponding modulation scheme and signal to noise ratio.

For more detailed insights into this model, the Jupyter Notebook on modulation recognition within this repository offers comprehensive information. In the context of this project, the focus is narrowed to three specific modulation schemes: B-FSK, 4-FSK, and 8-FSK. This selection is driven by two primary factors: the prevalence of Frequency-Shift Keying (FSK) in underwater communication systems and the necessity for simplicity in this proof-of-concept phase.

### Channel Estimation.
The second model in this project is dedicated to channel estimation. Based on the proposed architecture, the objective was to develop a model capable of analyzing signal samples and estimating the channel conditions affecting them. This model lays the groundwork for future enhancements, where a broader spectrum of channel conditions could be incorporated and analyzed.

To achieve this, a custom dataset was crafted, utilizing a consistent FSK signal across all samples. However, each sample is uniquely modified with randomized channel conditions. This methodology aligns with the project's architectural design, wherein the same pilot signal is sent back to the transmitter repeatedly. Since the project is tailored towards underwater communication scenarios, the current focus is on two primary channel conditions: additive noise and multipath effects. Consequently, the model is designed to predict various parameters such as the signal-to-noise ratio (SNR), multipath delays, and the attenuation levels of each delayed signal copy. To provide a clear baseline for comparison, a spectrogram of the base FSK signal—prior to the application of any channel conditions—is presented below. 

![image](https://github.com/Moe-Khalaf/AdapMod_ML_ECED4676/assets/124087656/2965bcc7-10d6-40b6-85c6-52d84ba5254e)

When each sample signal is being created, a randomized set of noise and multipath is applied to the base signal. Below, the application of these conditions is visualized in the form of spectrograms.

![image](https://github.com/Moe-Khalaf/AdapMod_ML_ECED4676/assets/124087656/5368cf55-b82f-40d5-9d2b-5714cbd89968)
![image](https://github.com/Moe-Khalaf/AdapMod_ML_ECED4676/assets/124087656/056c5fc7-57d8-4008-a428-5a1eb2e33117)

## Evaluation and Results
### Automatic Modulation Recognition
The modulation recognition model had achieved high performance. The classification had a near perfect accuracy. The confusion matrix is shown below.

![image](https://github.com/Moe-Khalaf/AdapMod_ML_ECED4676/assets/124087656/2f322c91-4e12-4e16-a417-5b6106ac108a)

### Channel Estimation
Compared to the modulation recognition results, the channel estimation results were mildly lackluster. The multipath delays were predicted at over 90% accuracy consistently, however, the multipath attenuations were predicted at a 40% accuracy. The signal to noise ratio predictions yielded no accuracy, indicating that alternative and perhaps more traditional methods of assessing noise may be more suitable for the grander scheme of this project.

## Future Work
There are several improvements and developments that are due in order to further this project,
 - An alternative more accurate method for assessing signal-to-noise ratio should be determined
 - The modulation recognition model should be further stress tested by using other datasets to assess the strength of the model against a truly diverse set of signals.
 - The remainder of the system should be implemented and fully integrated with these models in a mathematical simulation in python. The simulation should assess the effectiveness of the adaptive modulation system through an evaluation of error rate and transmission speed, following with a comparison with the effectiveness of fixed modulation schemes
 - The system should be integrated in the physical world and tested for effectiveness, providing more realistic insights.

## References
The following secondary sources were used to inform the research and development of this project.

[1]	 A. Svensson, “An introduction to adaptive QAM modulation schemes for known and predicted channels,” Proceedings of the IEEE, vol. 95, no. 12, pp. 2322–2336, 2007. doi:10.1109/jproc.2007.904442 

[2] 	F. Zhang, C. Luo, J. Xu, Y. Luo, and F.-C. Zheng, “Deep Learning based automatic modulation recognition: Models, datasets, and challenges,” Digital Signal Processing, vol. 129, p. 103650, 2022. doi: 10.1016/j.dsp.2022.103650 

[3]	 H. Wymeersch and A. Eryilmaz, “Multiple Access Control in wireless networks,” Academic Press Library in Mobile and Wireless Communications, pp. 435–465, 2016. doi:10.1016/b978-0-12-398281-0.00012-0 

[4] 	W. Sun, Z. Wang, M. Jamalabdollahi, and S. A. Reza Zekavat, “Experimental study on the difference between acoustic communication channels in freshwater rivers/lakes and in Oceans,” 2014 48th Asilomar Conference on Signals, Systems and Computers, 2014. doi:10.1109/acssc.2014.7094457 

[5] 	“Reducing signal noise in practice,” Precision Digital, https://www.predig.com/whitepaper/reducing-signal-noise-practice (accessed Dec. 2, 2023). 

[6] 	J. Bordash, “Multipath interference and Diversity switching,” Sound Devices, https://www.sounddevices.com/multipath-interference-and-diversity-switching/ (accessed Dec. 2, 2023). 

[7] 	Kürşat Tekbıyık, Cihat Keçeci, Ali Rıza Ekti, Ali Görçin, Güneş Karabulut Kurt, October 27, 2019, "HisarMod: A new challenging modulated signals dataset", IEEE Dataport, doi: https://dx.doi.org/10.21227/8k12-2g70







