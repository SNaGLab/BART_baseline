import os
import numpy as np
import pandas as pd
from qLib2.qLib import *
from psychopy import visual, core, event


window = visual.Window(
                    size=[1000, 500], monitor='testMonitor',color='white', colorSpace='rgb',fullscr=False, screen=0,
                    allowGUI=True
                    )
sessionField = textField(window=window,
                                 drawList=[
                                     visual.TextStim(win=window, height=.08, wrapWidth=1.5,
                                                    text=('Session.'), color='black', colorSpace='rgb',
                                                    pos=[0, .3])
                                 ],
                                 clock=None, label='', labelColor='black', maxChars=3, size=.08, text=00, type='int')

Session = int(sessionField[0][0])


path = os.path.dirname(os.path.realpath(__file__))
frame = pd.read_csv(path + '/payments/subjectPaymentFrame_%s.csv'%Session)
frame.index = frame.SubjectID
idList = []
ypos = -0.8
for i in frame.index:
    id = visual.TextStim(win = window,height = .08,wrapWidth=1.5,
                         text = str(i),
                         color = 'black',colorSpace='rgb',pos=[-.8,ypos])
    idList.append(id)
    ypos += 0.1

while 1:
    txt = visual.TextStim(win = window,height = .08,wrapWidth=1.5,
                          text =('SubjID'),
                          color = 'black',colorSpace='rgb',pos=[0,.3])
    idList.append(txt)
    SubID = textField(window = window,drawList=idList,clock = None, label='',
                      labelColor='black',maxChars=3,size=.08,text=00,type='int')

    print frame.loc[int(SubID[0][0])]



