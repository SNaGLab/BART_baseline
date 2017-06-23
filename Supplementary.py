import pandas as pd
import os
import numpy as np
import math
from psychopy import visual, event, core, gui
from qLib2.qLib import *
import pickle
from Coin_distributor import Distributor

def DS_cleaner(FilePath):
    ''' Removes .DS_Store file from list of directory
        and reindexes when using os.listdir()
        '''
    Files = os.listdir(FilePath)
    found = False
    popper = []
    for F in Files:
        if F[0] == '.':
            popper.append(Files.index(F))
    for I in reversed(popper):
        Files.pop(I)
    return Files

def pickleEditAndDump(key,value,pathtopickle):
    pklFile = open(pathtopickle)
    otherInfo = pickle.load(pklFile)
    otherInfo[key] = value
    pklFile.close()
    pklFile = open(pathtopickle,'wb')
    pickle.dump(otherInfo,pklFile)
    pklFile.close()


def WithinTaskRating(window, path, MotherPacket, both=True):
    fixation = visual.TextStim(win=window,
                               text='+',
                               color='black',
                               )

    question = visual.TextStim(win=window, height=.08, wrapWidth=1.5,
                               text=('What do you believe is the maximum balloon size?'
                                     '\n\nPlease respond in number of pumps.'),
                               color='black', pos=[0, .3])

    # use qLib.textField to display maximum balloon rating question
    MaxBelief = textField(window=window, drawList=[question], clock=None, label='',
                          labelColor='black', maxChars=3, size=.08, text=00, type='int')

    while type(MaxBelief[0][0]) != unicode:  # ensure that response is of acceptable value type
        MaxBelief = textField(window=window, drawList=[question], clock=None, label='',
                              labelColor='black', maxChars=3, size=.08, text=00, type='int')

    with open(path + '/MaxRatings.csv', mode='a') as MyFile:
        MyFile.write(str(MotherPacket['Run']) + ',' + str(MaxBelief[0][0]) + '\n')

    Text = "Out of 50 balloons, where do you think the balloon is likely to pop? Placing more bets in a column will indicate that you think more balloons will pop at that size. You must place 50 bets to continue."
    bars = Distributor(window, int(MaxBelief[0][0]), Text).initialize()
    bars.append(MotherPacket['Run'])
    bars.append('pop')

    with open(path + '/DistRatings.csv', mode='a') as MyFile:
        X = ','.join(str(e) for e in bars)
        MyFile.write('%s\n' % X)

    if both:

        Text = "In this block you will play with another participant.\n\nOut of 50 balloons, where do you think the other participant is likely to 'cash in'? Placing more bets in a column will indicate that you think the other participant is more likely to pump to that value and cash in. You must place 50 bets to continue."
        bars = Distributor(window, int(MaxBelief[0][0]), Text).initialize()
        bars.append(MotherPacket['Run'])
        bars.append('soc')

        with open(path + '/DistRatings.csv', mode='a') as MyFile:
            X = ','.join(str(e) for e in bars)
            MyFile.write('%s\n' % X)

    window.flip()
    fixation.draw()
    window.flip()
    core.wait(1.2)


def orange_white(window,path):
    '''
    Have subject choose between orange or white for the gamble decision
    '''
    instruction = visual.TextStim(
                            win = window, color='black',pos=(0,.4),wrapWidth=1.6,height = .07,
                            text = "Please select a color.")

    question_canvas = choice(window= window,
                 drawList=[instruction],
                 labels=['Orange', 'White'], labelColor='black')
    if question_canvas[0] == 0: response = 'Orange'
    else: response = 'White'
    otherInfo = open(path + '/OtherInfo.p', mode='wb')
    pickle.dump({'Color': response}, otherInfo)

def risk_ambiguity_scale(window,riskamb,path,instructionImage):
    '''
    Displays one of three componenets of the risk ambiguity portion of the exp.
    '''

    aspectRatio = float(window.size[1])/float(window.size[0])
    unselected = os.getcwd() + '/Resources/gameImages/rb.png'
    selected = os.getcwd() + '/Resources/gameImages/rbc.png'
    optA = visual.TextStim(
                        win = window, units='norm', text='Option A',
                        alignHoriz='left',height=.05, color='black',
                        pos=(-.25, .75))
    optB = visual.TextStim(
                        win = window, units='norm', text='Option B',
                        alignHoriz='left',height=.05, color='black',
                        pos=(.21, .75))
    next = visual.TextStim(
                        win = window, text = 'Press return to continue',pos=(0, -.9))

    Instruct = visual.TextStim(
                    win = window, text=("Use the 'up' and 'down' keys to move rows, the 'left' key"
                                        " to select option A\n"), wrapWidth=1.8,
                    height=.05, color='black', pos=[.0, .9],alignHoriz='center')
    Instruct2 = visual.TextStim(
                    win = window, text=("and the 'right' key to select option B."
                                        " Press 'i' to view instructions again."),
                    wrapWidth=1.8, height=.05,color='black',pos=[.0, .86],
                    alignHoriz='center')
    instructionWindow = visual.ImageStim(win=window, image=instructionImage, units='norm')

    class Question():

        def __init__(self, idex, window, aspectRatio, vPos=0.0, amount=.25, labelSize=.04,
                     labelColor='black'):
            self.Sure = False
            self.Gamble = False
            self.window = window
            self.vPos = vPos
            self.amount = amount
            self.labelSize = labelSize
            self.labelColor = labelColor
            self.idex = idex
            self.Got = False
            self.aspectRatio = aspectRatio

            if len(str(self.idex+1)) == 1:
                ntext = '  '+str(self.idex+1)+'.'
            else:
                ntext = str(self.idex+1)+'.'

            self.Number = visual.TextStim(
                                    self.window, units='norm', text = ntext,
                                    alignHoriz='left', height=self.labelSize,
                                    color=self.labelColor, pos=(-.6, self.vPos))

            self.SureBet = visual.TextStim(
                                    self.window, units='norm',
                                    text='I choose the sure amount of %s Tokens.' % self.amount,
                                    alignHoriz='left', height=self.labelSize,
                                    color=self.labelColor, pos=(self.Number.pos[0]+.09,
                                    self.vPos))

            self.buttonS = visual.ImageStim(
                                    self.window, image= unselected,
                                    size=(self.labelSize * self.aspectRatio, self.labelSize), units='norm',
                                    pos=(self.Number.pos[0]+.06, self.vPos - self.labelSize * .04))

            self.buttonG = visual.ImageStim(
                                    self.window, image=unselected,
                                    size=(self.labelSize * self.aspectRatio, self.labelSize), units='norm',
                                    pos=(self.SureBet.pos[0]+.7, self.vPos - self.labelSize * .04))

            self.gamble = visual.TextStim(
                                    self.window, units='norm', text='I choose to pick a paper slip.',
                                    alignHoriz='left', height=self.labelSize,
                                    color=self.labelColor, pos=(self.buttonG.pos[0]+.03, self.vPos))

        def Draw(self):
            self.Number.color = 'black'
            self.SureBet.color = 'black'
            self.gamble.color = 'black'

            if Index == self.idex:
                self.Number.color = 'white'
                self.SureBet.color = 'white'
                self.gamble.color = 'white'
            if Nexted:
                self.Number.color = 'black'
                self.SureBet.color = 'black'
                self.gamble.color = 'black'

            self.Number.draw()
            self.SureBet.draw()
            self.buttonS.draw()
            self.gamble.draw()
            self.buttonG.draw()

        def output(self, Type):
            if self.Sure:
                return [Type, self.idex, self.amount, 'Sure Bet']
            elif self.Gamble:
                return [Type, self.idex, self.amount, 'Gamble']

    List = []
    vMax = .67
    vPos = vMax
    amount = .25
    num = 20
    increment = .075
    for i in range(num):
        List.append(Question(i, window, aspectRatio, vPos, amount=amount))
        vPos -= increment
        amount += .25
    vMin = vPos
    y = vMax
    x = -.032
    box = visual.Rect(
                    win = window, width=1.2, fillColor=None, opacity=.5, height=.08,
                    pos=[x, y], lineColor='darkblue', lineWidth=2)
    Index = 0
    Done = False
    Nexted = False
    instruct = False
    while not Done:
        if event.getKeys('down'):
            Index += 1
            if Index == num:
                Index -= 1
            y -= increment
        elif event.getKeys('up'):
            Index -= 1
            y += increment

        elif event.getKeys('left'):
            List[Index].buttonS.setImage(selected)
            List[Index].buttonG.setImage(unselected)
            List[Index].Sure = True
            List[Index].Got = True

        elif event.getKeys('right'):
            List[Index].buttonS.setImage(unselected)
            List[Index].buttonG.setImage(selected)
            List[Index].Got = True
            List[Index].Gamble = True

        if y == vMin:
            y = vMax
            Index = 0
        elif y > vMax:
            y = vMin + increment
            Index = num - 1
        box.pos = [x, y]

        Count = 0
        for i in List:
            if i.Got:
                Count += 1

        if event.getKeys(['return']) and Count == num:
            Nexted = True
            Done = True

        Instruct.draw()
        Instruct2.draw()
        optA.draw()
        optB.draw()
        for i in List:
            i.Draw()
        if not Nexted:
            box.draw()
        if Count == num:
            next.draw()

        if event.getKeys('i') and not instruct:
            instructionWindow.setAutoDraw(True)
            instruct = True

        if event.getKeys(['space']) and instruct:
            instructionWindow.setAutoDraw(False)
            instruct = False

        window.update()


    for _ in List:
        out = _.output(riskamb)
        with open(path + '/RiskAmb.csv', mode='a') as MyFile:
            X = ','.join(str(e) for e in out)
            MyFile.write('%s\n' % X)
    core.wait(1)

if __name__ == '__main__':
    window = visual.Window(
                    size=[800, 500], monitor='testMonitor',
                    color=(0, 0, 0), fullscr=True, screen=0, allowGUI=False)
    risk_ambiguity_scale(window, 'risk', '/Users/JMP/Desktop', '/Users/JMP/Desktop/1.png')
