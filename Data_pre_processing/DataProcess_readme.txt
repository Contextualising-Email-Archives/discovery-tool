1. The Enron_data.py is the data pre-processing file. You have to run this process only once and save the output at a known location.
2. Download Enron data (May 7, 2015 Version of dataset) from https://www.cs.cmu.edu/~enron/ 
3. Unzip and save at a known location.
4. Run Enron_data.py
5. You will be asked for the data path ; supply the path upto,  complete/data/path/enron_mail_20150507/maildir/
6. The code reads the data and processes it in a way needed for the discovery tool. It will take several minutes 
(depending on the machine's capacity, it may take up to 1 hour or more)

7. System performs a simple test and provides the number of emails in the dataset. For the given dataset, it should be 495554.
8. It is important for the preprocessing to know which operating system it is working on. 
You will be propted to give input 1 if you are working on Windows, '2' for Linux environment.

9. The dataset contains the mailboxes of 150 custodians. You will be notified about it. (data validation check)
10. System performs date format conversion appropriate for the processing.
A default date is set to '2222/01/01' (YYYY/MM/DD) . But this dataset should have no default values.

11. Next, please specify an output path when prompted. Do not forget to include '/' towards the end.
12. The processed output is saved as a pickle file at output/path/Enron_full.pkl. 

13. Next process is to create folders of Lay-k and Skilling-J. You will be prompted when done.

