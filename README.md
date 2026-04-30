# Copyright Email Automation

This script automates the lookup process of an IP address that we have received for copyright infringement. It will prepare the email to be sent, but it will have to be sent manually.

## Table of Contents
### Installation
	- Clone the repo 
		https://github.com/derrick1001/copywrite_emails.git
	
	- Be sure to clone the python_modules repo as well, and verify that its in your PYTHONPATH
		https://github.com/derrick1001/python_modules.git	
	
### Usage
	- By default, this script is using thunderbird as a client. You can edit the compose_email function in the 
	- script to change this.
	
	- Change the global variables MAILDIR, WORKDIR, and LOGDIR to reflect the directories you are using on your
	- system
