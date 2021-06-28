This folder contains ECONDIST webapp prototype (Model 1 only ) to run on your desktop and as a herokuapp.
If you are running for the first time, please take the help of a software developer with python and webapp development.

#How to run this webapp prototype for Model 1 on your desktop:
1. Download the sourcecode to your desktop. This app works on Linux type of environments as it needs to spawn worker threads. Not possible on Windows OS.
2. Requirements.txt contains all required packages to run the desktop.
2a. for Conda users, the command is *$conda install --file requirements.txt* , else *$pip install -r requirements.txt --target ./lib*
3. the files Model1.py and Model1_original.py are superfluous. You can add them to .gitignore if you add the project to git.
4. From the terminal, run worker.py first (It is a server to spawn worker threads)
5. start another terminal window and run app.py. You will get a message 'Serving on http://0.0.0.5000'
6. Open a browser and paste the url http://0.0.0.5000 (i.e you are running the app from your localhost)
7. You should see the screen as image1.png in this folder.
8. In the include/exclude groups, check 'Top management' 
9. Add a search phrase in the text box (e.g: Election Bush).
10. Select time period
11. Click on 'Simple Search' (In this version, advanced search i.e Advanced Search is not included)
12. The search will take sometime depending on the groups you have added.
13. You may check whether search is done by clicking on the check results periodically.
14. A list of up to 25 results will be displayed when search is done (image2.png). Each email result is clickable.
15. Once, search is completed, scroll down the results to see the button to view time plot and word cloud. You can click on the plot time line and word cloud for the given search phrase (as shown in image3.png).
15a. The time plot shows the usage of the phrase on the time line and wordcloud shows all relevant words used in those mails to aid your analysis

#How to run this webapp from heroku
1. Create a heroku login account, login to heroku cli from your desktop.
2. Upload the sourcecode to heroku by adding project to git push ($git push heroku master)
3. Create heroku app
4. Run from the website provided.
