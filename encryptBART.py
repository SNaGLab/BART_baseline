import re
from simplecrypt import encrypt
import getpass
import pandas as pd
import os
def encryptBART(file,Session,path,password):
	filepath = os.path.join(path,'Linker_%s.csv'%Session)
	file.to_csv(filepath)
	File = open(filepath,'r')
	Text = File.read()
	File.close()
	
	text = encrypt(password,Text)
	File = open(filepath,'w')
	File.write(text)
	File.close()
