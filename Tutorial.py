'''
Interactive Tutorial for S_BART.02
Code: Jacob M. Parelman
Date: 07-01-2016
'''
import os
import numpy as np
from psychopy import visual, core, event
from Balloon import balloon
import Instructions
import random
from Data_handler import Data_Handler
from Simulated_players import simulated_player

class Button:
    '''
    button to trigger event

    '''
    def __init__(self,window, pos=[0, 0], scale=0.1, image=os.getcwd() + '/Resources/gameImages/' + 'right_arrow.png', keys=['right']):
        self.Image = visual.ImageStim(window, image=image, pos=pos, size=[scale,scale])
        self.keys = keys

    def Pressed(self):
        '''Returns true when button or key is pressed. Place this in active task
        loop.
        '''
        self.Image.draw()
        if event.getKeys(keyList=self.keys):
            return True


class InstructionBox:
    '''Actively displays textbox in three sizes; small, medium, and large.
    If button = True, dispalys an active Button.
    '''
    def __init__(self, window, pos, text, button = False):
        self.window = window
        self.drawList = []
        self.button = button

        length = len(text)

        if length <= 60:
            wid = 0.45
            hei = 0.25
            Ppos = [pos[0] - 0.21,pos[1] + 0.1]
            wP = 0.4
            Bpos = [pos[0] + 0.175,pos[1] - 0.075]
        elif length <= 160 and len(text) > 60:
            wid = 0.6
            hei = 0.4
            Ppos = [pos[0] - 0.28,pos[1] + 0.175]
            wP = 0.55
            Bpos = [pos[0] + 0.225,pos[1] - 0.125]
        elif length > 150 <= 520:
            wid = 0.8
            hei = 0.6
            Ppos = [pos[0] - 0.38,pos[1] + 0.275]
            wP = 0.75
            Bpos = [pos[0] + 0.35,pos[1] - 0.25]
        self.Box = visual.Rect(window, pos = pos,width = wid, height = hei,fillColor = 'white', opacity = 0.8,lineColor = 'black', lineWidth=3)
        self.drawList.append(self.Box)
        self.text = visual.TextStim(window, text = text, height = 0.04,pos = Ppos,color = 'black',wrapWidth = wP,alignHoriz = 'left',alignVert = 'top')
        self.drawList.append(self.text)

        # if you want a button to cancel box display
        if self.button:
            self.nexter = Button(window,pos = Bpos,scale = 0.075)

    def buttonwait(self, extras = [],balloons = []):
        '''
        displays InstrutionBox with active button until button is pressed
        (to display instructionbox without active button, draw images in
        self.drawList.)
        '''
        event.clearEvents()
        while 1:
            for b in extras:
                b.draw()

            for b in balloons:
                b.update()
            for b in self.drawList:
                b.draw()

            if self.button:
                if self.nexter.Pressed():
                    break
            self.window.flip()


def run_Tutorial(window, competitive):
    '''
    Runs all elements of the tutorial, including gameplay
    '''

    #  Setup___________
    event.Mouse(visible=False)
    savePath = os.path.expanduser('~') + '/Desktop/Temp'  # where to save data
    eventRecorder = Data_Handler(savePath) # Data_Handler to record events of active tasks
    eventRecorder.Competitive = competitive

    # configure eventRecorder with file columns
    Mpacket = {'Session': 0,
               'SubjectID': "Tutorial",
               'Run': 0,
               'Game': 'Single Player',
               'Trial': 0,
               'P2_ID': 0
               }

    eventRecorder.ConfigureDataHandlerGameInformation(Mpacket)


    # Frequently used images
    aspectRatio = float(window.size[1])/float(window.size[0])

    fixation = visual.TextStim(win = window,
                               text = '+',
                               color = 'black',
                               )

    # balloon for single player trials
    b1 = balloon(window, 0, os.getcwd() + '/Resources',eventRecorder = eventRecorder, practice = True)



    #  BEGIN TUTORIAL_______

    # 1. welcome to task
    bButton = InstructionBox(window, [-0.5, 0.75],
                             "Welcome to the Balloon pump game tutorial! Press the 'right arrow' key to continue.",
                             True)
    bButton.buttonwait(balloons=[b1])
    window.flip()

    # 2. explain balloon and token stims
    bButton = InstructionBox(window, [-0.5, 0.75],
                             "Pump balloons, and earn tokens, by pressing or holding the spacebar.", True)
    

    # trial setup
    b1.reset()
    b1.max = 45
    event.clearEvents()



    # Main trial loop
    while not b1.done:
        if b1.pumps < 10:
            b1.pumpAction()
            event.clearEvents()
        if b1.pumps == 10:
            if event.getKeys(['return']):
                Action = b1.cash()
                moveOn = b1.pumps == 10
                if competitive == '1':
                    b1.box.opacity = 1
                b1.outcome.setColor(u'green')

        # stop all player actions from registering and display step 5 when at 10 pumps
        if b1.pumps >= 10:
            # 5. cash in tokens
            bButton = InstructionBox(window, [0.55, 0.55],
                                     "Press the return key to cash in these tokens.",
                                     False)

        b1.update()
        for b in bButton.drawList:
            b.draw()
        window.flip()
        if b1.done:
            core.wait(2)
    event.clearEvents()

    # 6. begin single player freeplay trials
    bButton = InstructionBox(window, [0, 0],
                             "Try a few more balloons on your own.\n\n (remember, you can hold the spacebar to pump quickly).",
                             True)
    bButton.buttonwait()
    window.flip()

    # setup for trial loop
    eventRecorder.p1 = b1
    eventRecorder.p2 = None
    eventRecorder.Game = 0
    b1.practice = False  # start eventRecorder with above parameters

    # Player stops receiving new trials after at least 5 cashed in balloons and 1 popped balloon.
    count = 0
    popped = False
    window.flip()

    # trial loop
    while 1:
        # new trial
        b1.reset()
        eventRecorder.Trial += 1
        # fixation cross
        fixation.draw()
        window.flip()
        eventRecorder.RecordEvent('Fixation')
        core.wait(np.random.uniform(1,3))
        # draw newly updated balloon
        b1.update()
        window.flip()
        eventRecorder.RecordEvent('StartPlay')
        event.clearEvents() # clear junk
        #main trial loop
        while not b1.done:
            Action = b1.pumpAction()
            if event.getKeys(['return']):
                Action = b1.cash()
                if competitive == '1':
                    b1.box.opacity = 1
                b1.outcome.setColor(u'green')
            if Action:
                b1.update()
                window.flip()
        # 7. When player pops for the first time, explain popping mechanics.
        if b1.popped and not popped:
            bButton = InstructionBox(window, [0.55,0.55],"Your balloon popped!\n\nWhen your balloon pops you will lose all of your tokens.",True)
            bButton.buttonwait(balloons = [b1])
            window.flip()
            popped = True

        else:
            core.wait(2)
        eventRecorder.RecordEvent('OutcomeScreen')
        count += 1
        if popped and count >= 5:
            break

    # 8. explain pop points. Watch range of balloons

    bButton = InstructionBox(window, [0,0],"Every balloon can have a different pop point.\n\nLet's watch a set of balloons pump to their pop points.",True)
    bButton.buttonwait()
    window.flip()
    # watch balloons
    b1.practice = True
    Is = Instructions.Instructions(window,os.getcwd())
    Is.Watch(b1)

    # conigure eventRecorder
    b1.practice = False

    # alternate between in and out groups
    count = 0

    # 11. pause for questions
    bButton = InstructionBox(window, [0,0],"If you have any questions at this point, please raise your hand and the experimenter will come to you.",True)
    bButton.buttonwait()


    # 15. Multiplayer introduced - explain computer and human opponents
    visual.ImageStim(window,image = os.getcwd() + '/Resources/gameimages/Computer.png', pos = [-0.1,0.75],size = [0.2*aspectRatio,0.2]), visual.ImageStim(window,image = os.getcwd() + '/Resources/gameimages/SinglePlayer.png',pos = [0.1,0.75],size = [0.2*aspectRatio,0.2])
    bButton = InstructionBox(window, [0,0.1],"You will also play a multiplayer version of the Balloon pump game.\n\nIn this tutorial you will learn to play this game with a computer. In the actual experiment you will only ever play with a real participant from today's session.",True)
    bButton.buttonwait(extras = [visual.ImageStim(window,image = os.getcwd() + '/Resources/gameimages/Computer.png', pos = [0,0.75],size = [0.2*aspectRatio,0.2])])

    #    # p1 and p2 balloons
    b1 = balloon(window, 1, os.getcwd() + '/Resources',eventRecorder = eventRecorder, practice = True)
    b2 = balloon(window, 2, os.getcwd() + '/Resources',eventRecorder = eventRecorder, practice = True)

    b2.balloon.image = os.getcwd() + '/Resources/Balloons/GreyBalloonFull.png'
    b2.Token.image = os.getcwd() + '/Resources/gameImages/Token_black_other.png'

    eventRecorder.p1 = b1
    eventRecorder.p2 = b2
    window.flip()

    # 16. explain multiplayer layout.
    if competitive == '1':
        bButton = InstructionBox(window, [0,-0.5],"Multiplayer trials will look like this.\n\nYour balloon will always be on the left.",True)
        bButton.buttonwait(balloons = [b1,b2])
        window.flip()


        # 17. explain multiplayer rules
        bButton = InstructionBox(window, [0,-0.5],"Pump your balloon 10 times and cash in.",False)
        CP = simulated_player('AGR',b1,b2) # create a simulated opponent

        # get ready for multiplayer trial
        bothdone = False
        b1.reset()
        b1.max = 12
        b2.reset()
        b2.max = 50
        event.clearEvents()

        # main trial loop
        b1.Ex.setAutoDraw(True)
        b2.Ex.setAutoDraw(True)
        while not bothdone:
            # let computer make moves, player only allowed to pump to 10 and cash in.
            if b1.cashed: CP.make_action()
            if b1.pumps < 10:
                b1.pumpAction()
                event.clearEvents()

            if b1.pumps == 10:
                if event.getKeys(['return']):
                    Action = b1.cash()


            if b1.done and b2.done:
                if b1.pumps > b2.pumps:
                    b1.box.opacity = 1
                    b1.outcome.setColor(u'green')
                    if b1.cashed and b2.cashed:
                        b2.Ex.setText('X')
                elif b1.pumps < b2.pumps:
                    b2.box.opacity = 1
                    b2.outcome.setColor(u'green')
                    if b1.cashed and b2.cashed:
                        b1.Ex.setText('X')
                elif b1.pumps == b2.pumps:
                    b1.Ex.setText('X')
                    b2.Ex.setText('X')
                bothdone = True
            for b in bButton.drawList:
                b.draw()

            b1.update()
            b2.update()
            window.flip()


        # 18. explain Multiplayer cashing in rules
        bButton = InstructionBox(window, [0,-0.5],"In multiplayer trials, you will receive your tokens only if you cash in ABOVE the other player. \n\nLet's practice a few more multiplayer trials now.",True)
        bButton.buttonwait(balloons = [b1,b2])
        window.flip()
        b1.Ex.setAutoDraw(False)
        b2.Ex.setAutoDraw(False)

        b1.practice = False
        b2.practice = False
        window.flip()
        # player 5 trials
        HasTied = False
        counter = 0
        botList = ['HES','AGR','NS','HES','AGR','NS','HES','AGR','NS','HES','AGR','NS','HES','AGR','NS','HES','AGR','NS']
        while counter <= 6:
            CP = simulated_player(botList[counter],b1,b2)
            b1.reset()
            b2.reset()
            eventRecorder.Trial += 1

            fixation.draw()
            window.flip()
            eventRecorder.RecordEvent('Fixation')
            core.wait(1)

            bothdone = False

            b2.max = np.random.randint(5,40) # limit range slightly so that computer doesn't pop too often.
            eventRecorder.RecordEvent('StartPlay')
            event.clearEvents()

            if counter >= 4:
                b2.max = b1.max

            # main trial loop
            b1.Ex.setAutoDraw(True)
            b2.Ex.setAutoDraw(True)
            while not bothdone:
                b1.pumpAction()

                CP.make_action()

                if event.getKeys(['return']):
                    b1.cash()

                if event.getKeys('9'):
                    b2.cash()

                if b1.done and b2.done:
                    if b1.pumps > b2.pumps:
                        b1.box.opacity = 1
                        b1.outcome.setColor(u'green')
                        if b1.cashed and b2.cashed:
                            b2.Ex.setText('X')
                    elif b1.pumps < b2.pumps:
                        b2.box.opacity = 1
                        b2.outcome.setColor(u'green')
                        if b1.cashed and b2.cashed:
                            b1.Ex.setText('X')
                    elif b1.pumps == b2.pumps:
                        if b1.cashed and b2.cashed:
                            b1.Ex.setText('X')
                            b2.Ex.setText('X')
                    eventRecorder.RecordEvent('OutcomeScreen')
                    bothdone = True
                    counter += 1
                b1.update()
                b2.update()

                window.flip()


            core.wait(2)
            b1.Ex.setAutoDraw(False)
            b2.Ex.setAutoDraw(False)

    else:
        bButton = InstructionBox(window, [0,-0.5],"Multiplayer trials will look like this.\n\nYour balloon will always be on the left. Your balloon is completely separate from the other player's balloon. Any choices you make will have no affect on the other player's balloon.\n\nLet's practice a few more multiplayer trials now.",True)



        bButton.buttonwait(balloons=[b1, b2])
        window.flip()

        b1.practice = False
        b2.practice = False
        window.flip()
        counter = 0
        while counter <= 6:
            CP = simulated_player('NS', b1, b2)
            b1.reset()
            b2.reset()
            eventRecorder.Trial += 1

            fixation.draw()
            window.flip()
            eventRecorder.RecordEvent('Fixation')
            core.wait(1)

            bothdone = False

            b2.max = np.random.randint(5, 40)  # limit range slightly so that computer doesn't pop too often.
            eventRecorder.RecordEvent('StartPlay')
            event.clearEvents()

            while not bothdone:
                b1.pumpAction()

                CP.make_action()

                if event.getKeys(['return']):
                    b1.cash()
                    b1.outcome.setColor(u'green')

                if event.getKeys('9'):
                    b2.cash()
                    b2.outcome.setColor(u'green')

                if b2.cashed:
                    b2.outcome.setColor(u'green')

                if b1.done and b2.done:
                    eventRecorder.RecordEvent('OutcomeScreen')
                    bothdone = True
                    counter += 1
                b1.update()
                b2.update()

                window.flip()

            core.wait(2)


    # 21. Payment explained
    bButton = InstructionBox(window, [0,0],"At the end of today's experiment, you will receive your earnings from ONE balloon, which will be selected at random.\n\nAll balloons, including those that popped can be selected.",True)
    bButton.buttonwait()

    # 22. Tutorial finished
    bButton = InstructionBox(window, [0,0],"You have now completed the Balloon pump game tutorial!\n\nPress the next button to continue with the experiment.",True)
    bButton.buttonwait()


if __name__ == '__main__':
    MyWin = visual.Window([800, 500], monitor='testMonitor', color='grey', fullscr=False, screen=0, allowGUI=True)
    run_Tutorial(MyWin,'0')

