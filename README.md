# Charting Engine
Charting Engine is a Microservice, which will provide charts and other visuals as required.

## Installation

To Install you will need Python 3.8 or above. We recommand to work with Ubuntu WSL2, which will make your work envoirnment very clear and your computer will perform better.

### Install WSL

Installing Windows Subsystem for Linux (WSL) on Windows 11:

Open the Start menu and type "Windows Features" in the search bar. Click on the "Turn Windows features on or off" option that appears in the search results.

In the "Windows Features" window that opens, scroll down to find "Windows Subsystem for Linux". Check the box next to it, and then click "OK". This will start the installation process.

Windows will download and install the necessary files. This may take several minutes, depending on your internet connection and computer speed.

After the installation is complete, restart your computer.

Once your computer has restarted, open the Microsoft Store app and search for the Linux distribution of your choice. There are several options available, including Ubuntu, Debian, and SUSE.

Choose the Linux distribution (Ubuntu 20.04.5 LTS) you want to install  and click on the "Get" or "Install" button. This will download and install the Linux distribution on your computer.

After the installation is complete, open the Start menu and search for the Linux distribution you just installed. Click on it to launch the Linux terminal.


### Install Python3

On WSL Terminal first update and upgarde your WSL Instance

```
sudo apt update
```
Then upgrade WSL Instance
```
sudo apt upgrade
```

Install python3
```
sudo apt install python3
```
And also install Pip
```
sudo apt install python3-pip
```
### Getting the code from Github
First you need to install Git on your WSL Ubuntu
```
sudo apt install git
```

For loging in to Github you will need to Authenticate the instance of WSL Ubuntu to your git-hub account you will need to generate SSH-KEY, to generate SSH-Key use the following command and follow the instruction. Enter the file name and give a password you will remember (No need to be the Git-hub account password).
```
ssh-keygen
```

Once the SSH-Key is generated, you can copy the content just by browseing the file using windows explorer or you can copy using the following command.

```
cat [File Name].pub | xclip -sel clip
```

You might need to install xclip by 

```
sudo apt install xclip
```

Now go to github.com and go to your profile and click SSH and GPG Keys [Link](https://github.com/settings/keys).

Click "New SSH Key"

Give a name and Past the Key in your Clipboard and Click "Add SSH Key".

Now you can get the project in a desired folder by running the following command.

```
git clone git@github.com:Argaam/charting_engine.git
```
### Create Virtual envoirnment
To create virtual envoirnment go the folder where you cloned the code and run the following command.
```
python3 -m venv archarts
```

And activate the envoirnment as follow.

```
source /archarts/bin/activate
```

### Install Requirements

The code include requirements.txt file and you can install it by browseing to the code folder where you get the code 
```
pip install -r requirements.txt
```
### Database 
The Database is located in the Database folder it is recommanded to place it in another folder or you can change the refrence in the config file.

### Running the code updated
You can run the code after setting th database path in the config file.
```
flask --app app --debug run
```


