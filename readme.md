Extract the project,

Go to browser past the link to download python3.7

1 - https://www.python.org/ftp/python/3.7.7/python-3.7.7-amd64.exe(windows)
download it and double click when it open there would be an option

add path 

please select add path compulsory.


2 - https://www.python.org/ftp/python/3.7.0/python-3.7.0-macosx10.9.pkg(MAC OS)
     2.1 - for macbook sometimes in old macbook versions python 2.7 is installed if you have new macbook and python 3.7 installed as default donot proceed with next steps go straight to step 4, which is quite dificult to uninstall,so we don't need to unintall. 
     
     2.2 - when you installed python 3.7, check it by writing command : python3 --version
if it displays python version 3.7.* | that is fine to work on.

     2.3 - now install virtualenv using pip, write command using pip or pip3 : pip3 install virtualenv
it will install virtualenv library.

     2.4 - open the new terminal window and write : cd (drag and drop project folder in terminal)
it will open the project folder in terminal.

     2.5 - now create a virtualenv of python3.7 write : virtualenv myenv --python=python3.7

     2.6 - activate the virtualenv write : source myenv/bin/activate
you will see (myenv) before line starting in terminal. now proceed to step number 4.

     2.7 - *****For daily running*****
          2.7.1 - open the terminal window write : cd (drag the project folder and press enter)
          2.7.2 - activate virtualenv write : source myenv/bin/activate
          2.7.3 - proceed to step 5 for Mac.



3 - for Linux OS

     3.1-sudo apt update
     3.2-sudo apt install software-properties-common

     3.3-sudo add-apt-repository ppa:deadsnakes/ppa

     Press [ENTER] to continue or Ctrl-c to cancel adding it.

     3.4-sudo apt install python3.7

     install pip?

     sudo apt install python3-pip

now after installation please open the terminal/cmd

4 - write following commands one by one.

pip install scrapy
pip install scrapy-zyte-api
pip install zyte-api
pip install --upgrade pip

5 - The start and the end dates are captured in the input_date.csv. You might need to specify the path where the file is on your setup. Please specify this on line #

*****************Mac******************

in the terminal you should be in project where scrapy.cfg file presents, so write the command: scrapy crawl wicourts. This will start the scrapper

Once running you will likley see the Captcha Challange on the screen that you will need to manually solve for the first time, the script will run automatically for that session. The demo.mp4 shows a recording on how to bypass the Captcha


*****************Windows & Linux***************** 
now go to extracted folder


double click on runner.bat file to run it is for windows.

if not in windows please run the scraper using terminal command make sure you are in folder where scrapy.cfg file present


scrapy crawl wicourts


