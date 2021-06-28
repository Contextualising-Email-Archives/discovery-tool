This model makes use of BERT servers. To create BERT embeddings:


This model needs bert service to be on.
to start bert service,
1. pip install -U bert-serving-server bert-serving-client # do it on your console
2. The server MUST be running on Python >= 3.5 with Tensorflow >= 1.10 (one-point-ten). Again, the server does not support Python 2! . 
3. However, the client can be running on both Python 2 and 3.
4. DOwnload a pre trained BERT model from https://bert-as-service.readthedocs.io/en/latest/section/get-start.html, then uncompress the zip file into some folder, say /tmp/english_L-12_H-768_A-12/
5. bert-serving-start -model_dir /your/directory/to/uncased_L-12_H-768_A-12/ -num_worker=4(check number of parallel threads on your system). 
6. Check whether the version of tensorflow is 1.15. BERT does not create optimization graph with Tensorflow 2.0
7. Incase you want to install tensorflow 1.15, the stable version is 1.15.2. $ pip install tensorflow==1.15.2


8. Next, system will ask for the folder path. Enter the folder path where the Enron.pkl is stored. 
For example, Your/path/ only. Do not include the file name.

9. System will create 'Results' folder in this directory to store the search results.
10. Input phrases to search when prompted separated by commas. Ex: Profit, JEDI, Chewco, Election Bush, President Elections. click ENTER.
You can have more than two words(space separated) in the search query.

11. System will prompt you when done.
