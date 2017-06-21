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
    A button that can be clicked to trigger event
    '''
    def __init__(self,window, pos=[0, 0], scale=0.1, imagePath=os.getcwd() + '/Resources/gameImages/', im='right_arrow.png', keys=['right']):
        self.window = window
        aspectRatio = (float(window.size[1])/float(window.size[0])) * scale
        self.im = im
        self.Im = visual.ImageStim(window, image=imagePath + im, pos=pos, size=[scale,scale])
        self.imagepath = imagePath
        self.keys = keys

    def Pressed(self):
        '''Returns true when button or key is pressed. Place this in active task
        loop.
        '''
        self.Im.draw()
        if event.getKeys(keyList=self.keys):
            return True


class InstructionBox:
    '''Actively displays textbox in three sizes; small, medium, and large.
    If button = True, dispalys an active Button.
    '''
    def __init__(self,window,pos,Text, button = False):
        self.window = window
        self.drawList = []
        self.button = button
        if len(Text) <= 60:
            wid = 0.45
            hei = 0.25
            Ppos = [pos[0] - 0.21,pos[1] + 0.1]
            wP = 0.4
            Bpos = [pos[0] + 0.175,pos[1] - 0.075]
        elif len(Text) <= 160 and len(Text) > 60:
            wid = 0.6
            hei = 0.4
            Ppos = [pos[0] - 0.28,pos[1] + 0.175]
            wP = 0.55
            Bpos = [pos[0] + 0.225,pos[1] - 0.125]
        elif len(Text) > 150 <= 520:
            wid = 0.8
            hei = 0.6
            Ppos = [pos[0] - 0.38,pos[1] + 0.275]
            wP = 0.75
            Bpos = [pos[0] + 0.35,pos[1] - 0.25]
        self.Box = visual.Rect(window, pos = pos,width = wid, height = hei,fillColor = 'white', opacity = 0.8,lineColor = 'black', lineWidth=3)
        self.drawList.append(self.Box)
        self.text = visual.TextStim(window, text = Text, height = 0.04,pos = Ppos,color = 'black',wrapWidth = wP,alignHoriz = 'left',alignVert = 'top')
        self.drawList.append(self.text)
        if self.button:
            self.nexter = Button(window,pos = Bpos,scale = 0.075,im = 'right_arrow.png')

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


def run_Tutorial(window,group):
    '''
    Runs all elements of the tutorial, including gameplay
    '''

    #  Setup___________
    event.Mouse(visible=False)
    savePath = os.path.expanduser('~') + '/Desktop/Temp'  # where to save data
    eventRecorder = Data_Handler(savePath) # Data_Handler to record events of active tasks

    # configure eventRecorder with file columns
    Mpacket = {'Session':0,'SubjectID':"Tutorial",'Belief':False,'In':False,'Run':0,'Game':'Single Player','Trial':0,'P2_ID':0,'Group':group}
    eventRecorder.ConfigureDataHandlerGameInformation(Mpacket)

    # Frequently used images
    aspectRatio = float(window.size[1])/float(window.size[0])

    fixation = visual.TextStim(win = window,
                               text = '+',
                               color = 'black',
                               )

    balloonColors = {'0': os.getcwd() + '/Resources/Balloons/BlueBalloonFull.png',
                     '1': os.getcwd() + '/Resources/Balloons/YellowBalloonFull.png',
                     'comp': os.getcwd() + '/Resources/Balloons/GreyBalloonFull.png'}

    TokenIcons = {
        '0': os.getcwd() + '/Resources/gameImages/Token_blue_you.png',
        '1': os.getcwd() + '/Resources/gameImages/Token_yellow_you.png',
        '2': os.getcwd() + '/Resources/gameImages/Token_black_other.png'
    }

    GameIm = visual.ImageStim(win=window,
                              image=TokenIcons[group],
                              pos=[0.09, 0.7],
                              size=[0.3 * aspectRatio, 0.3])
    GameIm.setAutoDraw(True)

    RedEx = visual.TextStim(win=window,
                            text='X',
                            color='red',
                            pos = [0,0],
                            height = 0.2)


    # balloon for single player trials
    b1 = balloon(window, 0, os.getcwd() + '/Resources/Balloons',eventRecorder = eventRecorder, practice = True)
    balloonColor = balloonColors[group]
    b1.balloon.image = balloonColor
    #  BEGIN TUTORIAL_______

    # 1. welcome to task
    bButton = InstructionBox(window, [-0.5, 0.75],
                             "Welcome to the Balloon pump game tutorial! Press the 'right arrow' key to continue.",
                             True)
    bButton.buttonwait(balloons=[b1])
    window.flip()

    # 2. explain balloon and token stims
    bButton = InstructionBox(window, [-0.5, 0.75],
                             "Today you are going to be playing several versions of the Balloon pump game.\n\nEvery game will have two basic elements: a balloon and a token counter.", True)
    bButton.buttonwait(balloons=[b1])
    window.flip()

    # 3. explain token > $
    bButton = InstructionBox(window, [-0.6, 0.65], "You have been placed in one of two groups (blue or yellow), according to your preferences for the paintings you submitted prior to this experiment.\n\nThe color of your balloon and tokens will tell you what group you are in.", True)
    bButton.buttonwait(balloons=[b1])
    window.flip()

    # 4. pump th balloon to 10
    bButton = InstructionBox(window, [0.55, 0.55],
                             "To play these games you will pump the balloon for tokens. \n\nPlease press or hold down the SPACEBAR to pump your balloon and earn tokens.", False)

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
                b1.box.opacity = 1
                b1.outcome.setColor(u'green')

        # stop all player actions from registering and display step 5 when at 10 pumps
        if b1.pumps >= 10:
            # 5. cash in tokens
            bButton = InstructionBox(window, [0.55, 0.55],
                                     "Nice work!\n\nCash in these tokens to save them by pressing the RETURN key.",
                                     False)

        b1.update()
        for b in bButton.drawList:
            b.draw()
        window.flip()
        if b1.done:
            core.wait(2)
    event.clearEvents()
    GameIm.setAutoDraw(False)

    # 6. begin single player freeplay trials
    bButton = InstructionBox(window, [0, 0],
                             "Try a few more balloons on your own.\n\nTo pump press or hold the SPACEBAR, \nto cash in press the RETURN key.",
                             True)
    bButton.buttonwait()
    window.flip()
    # setup for trial loop
    eventRecorder.p1 = b1
    eventRecorder.p2 = None
    eventRecorder.Game = 'Learning Cash'
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
        GameIm.draw()
        window.flip()
        eventRecorder.RecordEvent('StartPlay')
        event.clearEvents() # clear junk
        #main trial loop
        while not b1.done:
            Action = b1.pumpAction()
            if event.getKeys(['return']):
                Action = b1.cash()
                b1.box.opacity = 1
                b1.outcome.setColor(u'green')
            if Action:
                b1.update()
                GameIm.draw()
                window.flip()
        # 7. When player pops for the first time, explain popping mechanics.
        if b1.popped and not popped:
            GameIm.setAutoDraw(True)
            bButton = InstructionBox(window, [0.55,0.55],"Your balloon popped!\n\nWhen your balloon pops you will lose all of your tokens.",True)
            bButton.buttonwait(balloons = [b1])
            window.flip()
            popped = True
            GameIm.setAutoDraw(False)

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
    Is = Instructions.Instructions(window,os.getcwd())
    Is.Watch(b1,GameIm)

    # conigure eventRecorder
    eventRecorder.Game = 'Learning Single Rules'
    b1.practice = False

    # alternate between in and out groups
    count = 0

    TokenIcons = {
        '0': os.getcwd() + '/Resources/gameImages/Token_blue_split_in.png',
        '1': os.getcwd() + '/Resources/gameImages/Token_yellow_split_in.png',
        '2': os.getcwd() + '/Resources/gameImages/Token_blue_split_out.png',
        '3': os.getcwd() + '/Resources/gameImages/Token_yellow_split_out.png',
    }

    # free play with split for grops
    instr = False
    cashedOnce = False
    while count < 5:
        if count < 3:
            GameIm.setImage(TokenIcons[group])
            eventRecorder.In = True
        else:
            eventRecorder.In = False
            GameIm.setImage(TokenIcons[str(int(group) + 2)])
        # setup trial

        b1.reset()
        eventRecorder.Trial += 1

        # set image display for rules
        fixation.draw()

        window.flip()
        eventRecorder.RecordEvent('Fixation')
        core.wait(1)
        GameIm.setAutoDraw(True)
        b1.update()
        if not instr and count >= 3:
            bButton = InstructionBox(window, [0.55, 0.55],
                                     "In some trials half of your tokens will go to a player in the other group.",
                                     True)
            bButton.buttonwait(balloons=[b1])
            instr = True
            window.flip()
        elif count == 0:
            bButton = InstructionBox(window, [0.55, 0.55],
                                     "When an avatar in the color of your group is displayed on the right of the token, half of your earnings will go to another player from your group.",
                                     True)
            bButton.buttonwait(balloons=[b1])
            window.flip()
        b1.update()
        window.flip()

        eventRecorder.RecordEvent('StartPlay')
        event.clearEvents()

        # trial loop
        while not b1.done:

            Action = b1.pumpAction()
            if event.getKeys(['return']):
                Action = b1.cash()
                b1.pumps = float(b1.pumps)/2.0
                b1.box.opacity = 1
                b1.outcome.setColor(u'green')
            if Action:
                b1.update()
                window.flip()
        if b1.done:
            count += 1
            if not cashedOnce and b1.cashed:
                bButton = InstructionBox(window, [0.55, 0.55],
                                         "Notice that when you cashed in, you received half of your tokens.\n\nThe other half went to another player from the team shown on the coin.",
                                         True)
                bButton.buttonwait(balloons=[b1])
                cashedOnce = True
                window.flip()
        eventRecorder.RecordEvent('OutcomeScreen')
        GameIm.setAutoDraw(False)
        core.wait(2)



    # 11. pause for questions
    bButton = InstructionBox(window, [0,0],"If you have any questions at this point, please raise your hand and the experimenter will come to you.",True)
    bButton.buttonwait()




    # 15. Multiplayer introduced - explain computer and human opponents
    visual.ImageStim(window,image = os.getcwd() + '/Resources/gameimages/Computer.png', pos = [-0.1,0.75],size = [0.2*aspectRatio,0.2]), visual.ImageStim(window,image = os.getcwd() + '/Resources/gameimages/SinglePlayer.png',pos = [0.1,0.75],size = [0.2*aspectRatio,0.2])
    bButton = InstructionBox(window, [0,0.1],"You will also play a multiplayer version of the Balloon pump game.\n\nIn this tutorial you will learn to play this game with a computer. In the actual experiment you will only ever play with a real participant from today's session.",True)
    bButton.buttonwait(extras = [visual.ImageStim(window,image = os.getcwd() + '/Resources/gameimages/Computer.png', pos = [0,0.75],size = [0.2*aspectRatio,0.2])])

    #    # p1 and p2 balloons
    b1 = balloon(window, 1, os.getcwd() + '/Resources/Balloons',eventRecorder = eventRecorder, practice = True)
    b2 = balloon(window, 2, os.getcwd() + '/Resources/Balloons',eventRecorder = eventRecorder, practice = True)

    b1.balloon.image = balloonColor
    b2.balloon.image = balloonColors['comp']

    TokenIcons = {
        '0': os.getcwd() + '/Resources/gameImages/Token_blue_you.png',
        '1': os.getcwd() + '/Resources/gameImages/Token_yellow_you.png',
        '2': os.getcwd() + '/Resources/gameImages/Token_black_other.png'
    }

    P2Icon = visual.ImageStim(win=window,
                              image=TokenIcons['2'],
                              pos=[b2.xPos + 0.09, 0.7],
                              size=[0.3 * aspectRatio, 0.3])

    P1Icon = visual.ImageStim(win=window,
                              image= TokenIcons[group],
                              pos=[b1.xPos + 0.09, 0.7],
                              size=[0.3 * aspectRatio, 0.3])


    eventRecorder.p1 = b1; eventRecorder.p2 = b2
    window.flip()

    # 16. explain multiplayer layout.
    bButton = InstructionBox(window, [0,-0.5],"Multiplayer trials will look like this.\n\nYour balloon will always be on the left.",True)
    bButton.buttonwait(balloons = [b1,b2],extras = [P1Icon,P2Icon])
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
    P1Icon.setAutoDraw(True)
    P2Icon.setAutoDraw(True)
    RedEx.setAutoDraw(True)
    RedEx.setText('')
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
                    RedEx.pos = b2.earned.pos
                    RedEx.setText('X')

            elif b1.pumps < b2.pumps:
                b2.box.opacity = 1
                b2.outcome.setColor(u'green')
                if b1.cashed and b2.cashed:
                    RedEx.pos = b1.earned.pos
                    RedEx.setText('X')
            elif b1.pumps == b2.pumps:
                b1.box.opacity = 1
                b2.box.opacity = 1
                b2.outcome.setColor(u'green')
                b1.outcome.setColor(u'green')
                b1.pumps = float(b1.pumps / 2.0)
                b2.pumps = b1.pumps
            bothdone = True
        for b in bButton.drawList:
            b.draw()

        b1.update()
        b2.update()
        window.flip()


    # 18. explain Multiplayer cashing in rules
    bButton = InstructionBox(window, [0,-0.5],"In multiplayer trials, you will receive your tokens only if you cash in ABOVE the other player OR if you TIE with the other player. \n\nLet's practice a few more multiplayer trials now.",True)
    bButton.buttonwait(balloons = [b1,b2],extras = [P1Icon,P2Icon])
    window.flip()
    RedEx.setAutoDraw(False)
    P1Icon.setAutoDraw(False)
    P2Icon.setAutoDraw(False)

    b1.practice = False
    b2.practice = False
    window.flip()
    # player 5 trials
    HasTied = False
    counter = 0
    botList = ['HES','AGR','NS','HES','AGR','NS','HES','AGR','NS','HES','AGR','NS','HES','AGR','NS','HES','AGR','NS']
    while counter <= 6:
        RedEx.setText('')

        CP = simulated_player(botList[counter],b1,b2)
        print CP.Type
        print counter
        b1.reset()

        b2.reset()
        eventRecorder.Trial += 1

        fixation.draw()
        window.flip()
        eventRecorder.RecordEvent('Fixation')
        core.wait(1)

        bothdone = False

        b2.max = np.random.randint(1,40) # limit range slightly so that computer doesn't pop too often.
        eventRecorder.RecordEvent('StartPlay')
        event.clearEvents()

        if counter >= 4:
            b2.max = b1.max

        # main trial loop
        P1Icon.setAutoDraw(True)
        P2Icon.setAutoDraw(True)
        RedEx.setAutoDraw(True)
        while not bothdone:
            b1.pumpAction()
            if counter < 4:
                CP.make_action()
            else:
                while b2.pumps < b1.pumps - 1:
                    b2.pump()
                if b1.cashed:
                    b2.pump()
                    b2.cash()
                    if b2.pumps == b1.pumps:
                        HasTied = True
                elif b1.popped:
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
                        RedEx.pos = b2.earned.pos
                        RedEx.setText('X')
                elif b1.pumps < b2.pumps:
                    b2.box.opacity = 1
                    b2.outcome.setColor(u'green')
                    if b1.cashed and b2.cashed:
                        RedEx.pos = b1.earned.pos
                        RedEx.setText('X')
                elif b1.pumps == b2.pumps:
                    if b1.cashed and b2.cashed:
                        b1.box.opacity = 1
                        b2.box.opacity = 1
                        b1.outcome.setColor(u'green')
                        b2.outcome.setColor(u'green')
                        b1.pumps = float(b1.pumps / 2.0)
                    b2.pumps = b1.pumps
                eventRecorder.RecordEvent('OutcomeScreen')
                bothdone = True
                counter += 1
            b1.update()
            b2.update()

            window.flip()


        core.wait(2)
        P1Icon.setAutoDraw(False)
        P2Icon.setAutoDraw(False)
        RedEx.setAutoDraw(False)
        if HasTied:
            bButton = InstructionBox(window, [0, 0.1],
                                     "When you TIE with the other player, you will receive HALF of your tokens.",
                                     True)
            bButton.buttonwait(extras=[P1Icon,P2Icon],balloons = [b1,b2])
            break

    # 18. explain Multiplayer Social Belief
    bButton = InstructionBox(window, [0,0],"In some multiplayer games THE OTHER PLAYER'S ACTIONS WILL BE HIDDEN.\n\nThe results of each trial will be displayed immediately after both you and the other player have cashed in or popped.",True)
    bButton.buttonwait()
    window.flip()

    bButton = InstructionBox(window, [0,0],"Practice a few of these multiplayer trials now.",True)
    bButton.buttonwait()
    window.flip()

    # setup trials (SOCIAL BELIEF)

    b1.practice = False
    b2.practice = False

    eventRecorder.Belief = True

    HalfScreen = visual.Rect(win = window,
                               width=.8,
                               fillColor=u'white',
                               opacity=1,
                               height= 1.8,
                               pos = [b2.balloon.pos[0],b2.balloon.pos[1]],
                               lineColor = u'white',
                               lineWidth=4)
    # window.flip()
    for i in range(5):
        RedEx.setText('')

        CP = simulated_player('SB', b1, b2)
        b1.reset()
        b2.reset()
        eventRecorder.Trial += 1

        fixation.draw()
        window.flip()
        eventRecorder.RecordEvent('Fixation')
        core.wait(1)

        bothdone = False

        eventRecorder.RecordEvent('StartPlay')
        event.clearEvents()

        # main trial loop
        P1Icon.setAutoDraw(True)
        P2Icon.setAutoDraw(True)
        RedEx.setAutoDraw(True)
        b2.max = np.random.randint(10, 60)  # limit range slightly so that computer doesn't pop too often.

        while not bothdone:
            b1.pumpAction()
            if not HasTied:
                if b1.cashed:
                    b2.pumps = b1.pumps
                    core.wait(2)
                    b2.cash()
                elif b1.popped:
                    b2.pumps = np.random.randint(5,63)
                    if b2.pumps >= b2.max:
                        b2.pump()
                    else:
                        b2.cash()
            else:
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
                        RedEx.pos = b2.earned.pos
                        RedEx.setText('X')

                elif b1.pumps < b2.pumps:
                    b2.box.opacity = 1
                    b2.outcome.setColor(u'green')
                    if b1.cashed and b2.cashed:
                        RedEx.pos = b1.earned.pos
                        RedEx.setText('X')

                elif b1.pumps == b2.pumps:
                    if b1.cashed and b2.cashed:
                        b1.box.opacity = 1
                        b2.box.opacity = 1
                        b1.outcome.setColor(u'green')
                        b2.outcome.setColor(u'green')
                        b1.pumps = float(b1.pumps / 2.0)
                    b2.pumps = b1.pumps

                eventRecorder.RecordEvent('OutcomeScreen')
                bothdone = True

            b1.update()
            b2.update()
            if not bothdone:
                HalfScreen.draw()
            window.flip()
        core.wait(2)
        P1Icon.setAutoDraw(False)
        P2Icon.setAutoDraw(False)
        RedEx.setAutoDraw(False)
        if not HasTied and b1.cashed:
            bButton = InstructionBox(window, [0, 0.1],
                                     "When you TIE with the other player, you will receive HALF of your tokens.",
                                     True)
            bButton.buttonwait(extras=[P1Icon, P2Icon], balloons=[b1, b2])
            HasTied = True

    # 21. Payment explained
    bButton = InstructionBox(window, [0,0],"At the end of today's experiment, you will receive your earnings from ONE balloon, which will be selected at random.\n\nAll balloons, including those that popped can be selected.",True)
    bButton.buttonwait()

    # 22. Tutorial finished
    bButton = InstructionBox(window, [0,0],"You have now completed the Balloon pump game tutorial!\n\nPress the next button to continue with the experiment.",True)
    bButton.buttonwait()


if __name__ == '__main__':
    MyWin = visual.Window([800, 500], monitor='testMonitor', color='grey', fullscr=False, screen=0, allowGUI=True)
    run_Tutorial(MyWin,'1')

