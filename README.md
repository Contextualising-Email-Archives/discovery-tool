# discovery-tool
Test version of Email CONtextualisation DIScovery Tool (ECONDIST)

This code is a part of WP3 of the AHRC project

First you need to establish the environment using the imports mentioned in requirements.txt

first step is to - Open the Data_pre_processing folder and pre process the data. You need to do it only once. The process will generate pickle files. You can reuse those pickle files for running models. The current version of the code runs best on python version 3.7 (it has support to tensorflow 1.15.2 ). 

The Data_pre_processing folder contains a python file for preprocessing the code. Instructions needed to run this file are given in the DataProcess_readme.txt in the same folder

The Exploratory_data_analysis folder consists of a EDA.py file. This is best open in an ipython environment.
Instructions are in the EDA_readme.txt within this folder.

Please be aware that this folder is not supplied with requirements.txt as most of the versions have changed over the project duration and hardware resources used. Please follow the configuration needed for the bert-serving-client work on your machine. 
