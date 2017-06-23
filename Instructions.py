from psychopy import visual, event, core, gui
from Balloon import balloon
import numpy as np
import os
import json
from qLib2.qLib import *
import random
import pickle
import Tutorial
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

class Instructions:
    '''
    Supplementary instruction tasks for economic tasks
    included: Maximum rating for BART and implementation of distribution ratings
    '''
    def __init__(self,window,path):
        self.window = window
        self.path = path

    def Watch(self,b1):
        '''
        Subjects watch several balloons fill to their max size and pop.
        Balloon sizes represent the full range of possible balloon sizes.
        '''
        event.Mouse(visible=False)
        Fixation = visual.TextStim(win=self.window, text='+', color='black')

        # list of 16 pop points which span the entire range of the distribution
        Poplist = [4,40,12,20,32,48,52,1,60,24,64,28,8,56,36,44,16]

        for popPoint in Poplist:
            Fixation.draw()
            self.window.flip()
            core.wait(np.random.uniform(1,3))
            b1.reset()
            b1.max = popPoint
            b1.update()

            self.window.flip()

            while not b1.done:
                core.wait(0.1)
                b1.pump()
                b1.update()

                self.window.flip()
            core.wait(1)


    def MaxRatings(self):
        '''
        Ask participants to make belief ratings about pop points and other players'
        behavior during the task.
        '''
        event.Mouse(visible=True)
        question = visual.TextStim(win = self.window,height = .08,wrapWidth=1.5,
                                   text =('What do you believe is the maximum balloon size?'
                                          '\n\nPlease respond in number of pumps.'),
                                   color = 'black',pos=[0,.3])

        # use qLib.textField to display maximum balloon rating question
        MaxBelief = textField(window = self.window,drawList=[question],clock = None, label='',
                              labelColor='black',maxChars=3,size=.08,text=00,type='int')

        while type(MaxBelief[0][0]) != unicode:    # ensure that response is of acceptable value type
            MaxBelief = textField(window = self.window,drawList=[question],clock = None, label='',
                                  labelColor='black',maxChars=3,size=.08,text=00,type='int')

        # save maxiumum rating
        with open(self.path+'/MaxRatings.csv',mode = 'a') as MyFile:
            MyFile.write('1' + ',' + str(MaxBelief[0][0]) + '\n')
        return int(MaxBelief[0][0])

    def dists(self,Max,type):
        ticks = [0] + [' ' for _ in range(18)] + [Max] # tick labels for X axis

        if 'DistRatings.csv' not in os.listdir(self.path):
            with open(self.path+'/DistRatings.csv',mode = 'a') as MyFile:
                X = ','.join(str(e) for e in [str(i) for i in range(5,105,5) + ['run','type']])
                MyFile.write('%s\n'%X)

            Text = "Out of at least 100 balloons, where do you think any balloon is likely to pop? A higher number for a bar will indicate that you think more balloons will pop at that size."
        else:
            Text = "Out of at least 100 balloons, where do you think the other participants in today's session are likely to 'cash in'? A higher number for a bar will indicate that you think the other participants in today's session are more likely to pump to that value and cash in"

        barsText = visual.TextStim(win=self.window,
                                   height=.06,
                                   wrapWidth=1.9,
                                   color='black',
                                   pos=[0, .85],
                                   text=Text)

        # Distribution to be drawn from qLib.distribution
        bars = Distribution(window=self.window,
                            drawList=[barsText],
                            limits=[0, 100],
                            labels=ticks,
                            nBars=20,
                            defaultHeight=[1 for f in range(20)],
                            MaxVal=100,
                            width=.9,
                            h=.06)
        bars[2].append(1)
        bars[2].append(type)
        with open(self.path+'/DistRatings.csv',mode = 'a') as MyFile:
            X = ','.join(str(e) for e in bars[2])
            MyFile.write('%s\n'%X)

class questions:
    '''
    A set of questions asked ot the subject to check for their understanding of the
    task rules
    '''
    def __init__(self,path,window):
        self.path = path
        self.window = window

        # Response fields for questions
        self.Fields = [['Your tokens', 'black', ' ', 8, 'string'],
                       ["Other player's tokens", 'black', '', 8, 'string']]

    def AskQuestion(self,Question):

        event.Mouse(visible=True)

        Header = visual.TextStim(win=self.window, height=.08, wrapWidth=1.7,
                                 text="In the following situation, how many tokens would you and the other player receive?",
                                 color='black', pos=[0, .8])

        QuestionText = visual.TextStim(win=self.window, wrapWidth=1.7, height=.08, text=Question,
                                       color='black', pos=[0, .4])

        # Ask subject question and display fields. IF input is not able to be cast as integer, try again
        while 1:
            try:
                question_canvas = form(window=self.window, size=.08,
                                       drawList=[Header,QuestionText],fields=self.Fields)
                answers = [int(question_canvas[0][0]),
                           int(question_canvas[0][1])
                           ]
                return answers
            except:
                visual.TextStim(self.window,text = "Please fill in all fields before submitting the form, and be sure to only use numbers.",color = 'red',height = .08).draw()
                visual.TextStim(self.window,text = "Press the right key to try again.", pos = [0,-.5],color = 'red',height = .08).draw()
                self.window.update()
                event.waitKeys(keyList = ['right'])


    def UnderstandingQuestionWithField(self,Question,CorrectAnswers,explanation):
        '''
        Display question and response boxes. If participant enters information that
        does not match integer values, display hint and let them try again.
        '''

        Text1 = visual.TextStim(win=self.window, height=.08, wrapWidth=1.7,
                                text="You answered incorrectly",
                                color='red', pos=[0, .8])

        Text2 = visual.TextStim(win=self.window, wrapWidth=1.7, height=.08, text='',
                                color='black', pos=[0, .4])

        Help = visual.TextStim(win=self.window, wrapWidth=1.7, height=.08, text="If you are stuck or have a question, please raise your hand and the experimenter will come to you.",
                               color='black', pos=[0, -0.6])

        Next = visual.TextStim(win=self.window, wrapWidth=1.7, height=.08, text="press the right key to try again",
                               color='black', pos=[0, -0.8])


        answers = self.AskQuestion(Question)

        event.Mouse(visible=False)
        # continue to ask question until subject gets it correct. Provide a hint if subject gets question wrong.
        while (answers[0] != CorrectAnswers[0]) or (answers[1] != CorrectAnswers[1]):
            Text1.draw()
            Text2.setText('Hint:\n\n' + explanation)
            Text2.draw()
            Help.draw()
            Next.draw()
            self.window.flip()
            event.waitKeys(['Space'])

            answers = self.AskQuestion(Question)

        Text1.setText('You answered correctly')
        Text1.setColor('green')
        Text1.draw()
        Text2.setText(explanation)
        Text2.draw()
        Next.setText("press the right arrow key to move on")
        Next.draw()
        self.window.flip()
        event.waitKeys(['right'])




    def UnderstandingQuestionWithTrueFalse(self,Question,CorrectAnswers,explanation):
        '''
        Display question and true or false buttons. If participant enters information that
        does not match integer values, display hint and let them try again.
        '''
        Header = visual.TextStim(win=self.window, height=.08, wrapWidth=1.7,
                                 text="You answered incorrectly",
                                 color='red', pos=[0, .8])

        QuestionText = visual.TextStim(win=self.window, wrapWidth=1.7, height=.08, text=Question,
                                       color='black', pos=[0, .4])

        Next = visual.TextStim(win=self.window, wrapWidth=1.7, height=.08, text="press the right key to try again",
                               color='black', pos=[0, -0.8])

        Help = visual.TextStim(win=self.window, wrapWidth=1.7, height=.08, text="If you are stuck or have a question, please raise your hand and the experimenter will come to you.",
                               color='black', pos=[0, -0.6])

        question_canvas = choice(window=self.window,
                                 drawList=[QuestionText],
                                 labels=['True', 'False'], labelColor='black')

        event.Mouse(visible=False)
        while question_canvas[0] != CorrectAnswers:
            Header.setText('You answered incorrectly')
            Header.setColor('red')
            Header.draw()
            QuestionText.setText('Hint:\n\n' + explanation)
            QuestionText.draw()
            Next.draw()
            Help.draw()
            self.window.flip()
            event.waitKeys(['right'])

            QuestionText.setText(Question)
            Header.setColor('black')
            question_canvas = choice(window=self.window,
                                     drawList=[QuestionText],
                                     labels=['True', 'False'], labelColor='black')


        Header.setText('You answered correctly')
        Header.setColor('green')
        Header.draw()
        Next.setText("press the right key to move on")
        Next.draw()
        QuestionText.setText(explanation)
        QuestionText.draw()
        self.window.flip()
        event.waitKeys(['right'])


def Run_AllIntro(MyWin, path,skip):
    '''
    Runs all pieces of the introduction of experiment
    '''
    Instruct = Instructions(MyWin, path)
    if skip not in ['all','tutorial']:
        Tutorial.run_Tutorial(MyWin)  # Run the tutorial

    if skip != 'all':
        Questions = questions('/Users/JMP/Desktop/',MyWin)
        File = open(os.getcwd() + '/instruction_quests.json')
        j = json.load(File) # Import json with questions for quiz

        # Ask questions
        for item in j[:-1]:
            print item[0]
            print item[1]
            print item[2]
            Questions.UnderstandingQuestionWithField(item[0],item[1], item[2])
        Questions.UnderstandingQuestionWithTrueFalse(j[-1][0],j[-1][1],j[-1][2])

        # Get maximum rating and distributions
        Max = Instruct.MaxRatings()
        vid = visual.MovieStim3(MyWin, os.getcwd() +'/Resources/dist_vid.mp4', size=[700, 400], pos=[0, -150])
        distIm = visual.ImageStim(MyWin, os.getcwd() + '/Resources/DistImage.png',size=[0.8,0.8], pos=[0,-.5])
        bButton = Tutorial.InstructionBox(MyWin, [0, 0.5],
                                          "The scale below represents the size of a balloon from 0 pumps (leftmost column) to your estimated maximum balloon size (rightmost column). Each column represents a slightly larger balloon. \nAt what size do you think the balloons in this task are most likely to pop? You can place a bet by tapping one of the columns with your cursor."
                                          ,True)
        bButton.buttonwait(extras=[distIm])

        bButton = Tutorial.InstructionBox(MyWin, [0, 0.5],
                                          "Imagine that you would play as few as 100 balloons. At what size do you think these balloons will pop?\n\n You can place a bet by tapping one of the columns with your cursor. The more bets you place in a column, the more you expect that the balloons will pop at that size.",
                                          True)
        bButton.buttonwait(extras=[vid])
        bButton = Tutorial.InstructionBox(MyWin, [0,0.5],"We will pay you for the accuracy of your bets by comparing your bets against one randomly drawn popped balloon from the experiment today. The more bets you place on the correct column, the more you win.", True)
        bButton.buttonwait(extras=[vid])

        Instruct.dists(Max,'pop')

        bButton = Tutorial.InstructionBox(MyWin, [0,0.5],
                                          "With the same scale as before we would like you to indicate where you think other participants in todays session will pump to before they cash in.",
                                          True)
        bButton.buttonwait(extras=[distIm])

        singleDist = Distributor(MyWin, Max,
                                 instructions="Using only one bet, where do you think other participants in today's session are likely to pump to and cash in?",
                                 maxTotal=1).initialize()
        print singleDist
        with open(path + '/singleBet.csv', mode='a') as MyFile:
            X = ','.join(str(e) for e in singleDist)
            MyFile.write('%s\n' % X)


        bButton = Tutorial.InstructionBox(MyWin, [0, 0.5],
                                          "Imagine that you would see another player from today's session play with 50 balloons. How many pumps do you think that player will make before cashing in?",
                                          True)
        bButton.buttonwait(extras=[vid])

        bButton = Tutorial.InstructionBox(MyWin, [0, 0.5],
                                          "We will pay you for the accuracy of your rating by comparing your bets against one randomly drawn cashed in balloon from another participant in today's experiment. The more bets that you place in the correct column, the more you win..",
                                          True)
        bButton.buttonwait(extras=[vid])
        Instruct.dists(Max,'soc')

if __name__ == '__main__':
    window = visual.Window([800,500],monitor='testMonitor',fullscr=True,screen=0,allowGUI=False)
    I = Instructions(window,'/Users/JMP/Desktop/Temp')
    I.dists2(64)
