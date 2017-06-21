'''
SOCIAL BART.03
Design: J.M. Parelman, K. Fairley, R.M. Carter
Code: J.M. Parelman
contact: JmParelman@gmail.com
'''
from psychopy import visual, event, core, gui
from Balloon import balloon
import time
import numpy as np
from socket import *
import pickle
from Supplementary import WithinTaskRating
import os

class Game:
    '''
    Includes all games and game methods for S_BART tasks
    '''
    def __init__(self, window, path, eventRecorder = None):
        self.restart = False
        self.window = window
        self.path = path
        self.eventRecorder = eventRecorder # Data_Handler for task

        self.TrialTimer = core.CountdownTimer() # No-Timer trial countdown clock

        self.aspectRatio = float(window.size[1])/float(window.size[0])

        self.GameIm = visual.ImageStim(win = self.window,
                                      image = None,
                                      pos = [0.09,0.7],
                                      size = [0.3 * self.aspectRatio,0.3])


        self.fixation = visual.TextStim(win = self.window,
                                        text = '+',
                                        color = 'black',
                                        )

        self.Cover = visual.Rect(win = self.window,
                                      width = 0.8,
                                      fillColor='white',
                                      opacity=1,
                                      height=1.8,
                                      pos = [0.5,0],
                                      lineColor='black',
                                      lineWidth=2)

        self.RedEx = visual.TextStim(win=window,
                            text='X',
                            color='red',
                            pos = [0,0],
                            height = 0.2)

        self.balloonColors = {'0':os.getcwd() + '/Resources/Balloons/BlueBalloonFull.png',
                              '1':os.getcwd() + '/Resources/Balloons/YellowBalloonFull.png'}
        self.IconColors = {'0': os.getcwd() + '/Resources/gameImages/BlueGroup.png',
                              '1': os.getcwd() + '/Resources/gameImages/YellowGroup.png'}

    # Trial Setup methods __________________________________________________________
    def drawFixationGetMotherPacket(self,Socket,server,rStart = False):
        '''
        Draws fixation and requests game information from server.
        Catches restart messages from main program and sends
        appropriate message to server.
        server: IP and port for server coputer
        rStart: did the participant run into a problem?
        '''
        self.fixation.draw()
        self.eventRecorder.p1 = None;self.eventRecorder.p2 = None
        self.window.flip()
        if rStart:
            self.eventRecorder.headerMade = True
            Socket.sendto('ISSUE',server) # if there was an issue send ISSUE to server
        else: Socket.sendto('NEWGAME',server) # otherwise request a new game
        Socket.settimeout(10) # set the time out to 10 seconds.
        while 1:
            try: # wait for all game information from the server and unpack
                MotherPacket = pickle.loads(Socket.recvfrom(1000)[0])

                # Use motherpacket to configure the data csv for new trial
                self.eventRecorder.ConfigureDataHandlerGameInformation(MotherPacket)
                if rStart:
                    self.eventRecorder.RecordEvent('Restart')
                self.eventRecorder.RecordEvent('Fixation')

                return MotherPacket
            except timeout: # If no message is received in 10s send ISSUE to mother and wait again
                Socket.sendto('ISSUE', server)


    def helpFlip(self, group):
        if group == '0':
            return 1
        else:
            return 0

    def drawBreak(self,Socket):
        '''
        Draws the break screen and waits for server's begin trial message
        '''
        # Draw break screen and wait for game information from server
        visual.TextStim(win = self.window,
                       text = 'You will now take a short break.\n'+
                       'The task will continue automatically.',
                       color = 'black',
                       ).draw()
        self.window.flip()
        Socket.settimeout(300)
        MotherPacket = pickle.loads(Socket.recvfrom(1000)[0])
        self.eventRecorder.ConfigureDataHandlerGameInformation(MotherPacket)
        self.eventRecorder.Game = 0
        self.fixation.draw() # draw fixation again to prepare for trial
        self.window.flip()
        core.wait(1.5)

        return MotherPacket


    def PreTrialSetup(self, MotherPacket):
        ''' sets the images and their positions for a trial's specific rules
        '''
        self.restart = False

        self.TrialTimer.reset(240)  # reset timer

        # Begin Trial by clearing events and drawing balloons to screen
        self.eventRecorder.RecordEvent('StartPlay')
        self.window.flip()
        event.clearEvents()

    # multiplayer helper functions_________________________________________________
    def checkMessage(self,sock):
        '''
        Checks a non-blocking TCP socket for a message.
        If there isn't anything to receive or anything goes wrong
        do nothing.
        '''
        try:
            message = sock.recv(1)
            return message
        except:
            pass

    def sendMessage(self,sock,message):
        '''
        Send a message to other side of TCP socket.
        If anything goes wrong return True for error.
        '''
        try:
            sock.send(message)
            return False
        except:
            return True

    def rstart(self):
        '''
        If something went wrong during the multiplayer trial
        display this message and exit the trial.
        '''
        self.eventRecorder.RecordEvent('Restart')
        visual.TextStim(win = self.window,
                        text = 'The second player disconnected.\n'+
                        'Please wait for a new game.',
                        color = 'black',
                       ).draw()
        self.window.flip()
        self.restart = True


    # S_BART games ________________________________________________________________
    def Alone(self, MotherPacket):

        '''
        Subject Plays one trial of BART either timed or not.
        '''
        # balloon instance
        b1 = balloon(self.window, 0, os.getcwd() + '/Resources/Balloons',self.eventRecorder)
        b1.balloon.image = self.balloonColors[MotherPacket['Group']]
        self.eventRecorder.p1 = b1
        self.eventRecorder.p2 = None
        # Get Trial ready
        b1.reset()

        self.PreTrialSetup(MotherPacket)
        if int(MotherPacket['Run']) in [2,3,4,5]:
            # If subject must make a belief rating, allow them to do so
            if MotherPacket['Rating']:
                WithinTaskRating(self.window, self.path, MotherPacket)

            TokenIcons = {
                '0': os.getcwd() + '/Resources/gameImages/Token_blue_split_in.png',
                '1': os.getcwd() + '/Resources/gameImages/Token_yellow_split_in.png',
                '2': os.getcwd() + '/Resources/gameImages/Token_blue_split_out.png',
                '3': os.getcwd() + '/Resources/gameImages/Token_yellow_split_out.png',
            }
            print MotherPacket['Run']
            print type(MotherPacket['Run'])

            if MotherPacket['In']:
                ImageColor = TokenIcons[MotherPacket['Group']]
            else:
                ImageColor = TokenIcons[str(int(MotherPacket['Group']) + 2)]
                print self.helpFlip(MotherPacket['Group'])
        else:
            if MotherPacket['Run'] > 5:
                if MotherPacket['Rating']:
                    WithinTaskRating(self.window, self.path, MotherPacket, both=False)

            TokenIcons = {
                '0': os.getcwd() + '/Resources/gameImages/Token_blue_you.png',
                '1': os.getcwd() + '/Resources/gameImages/Token_yellow_you.png'
            }

            ImageColor = TokenIcons[MotherPacket['Group']]

        event.Mouse(visible=False)
        self.GameIm.setImage(ImageColor)
        self.GameIm.setAutoDraw(True)

        b1.update()
        self.window.flip()

        while not b1.done:
            Action = False     # Only update screen if something happens
            TimerAction = False # If Timer updates or timedOut
            # Check if player has timed out
            TimerAction = b1.timeOut(world = self.TrialTimer)


            Action = b1.pumpAction() # pump

            # Cash in
            # if np.random.randint(0, 1000000) < 10:
            if event.getKeys(['return']):                     # FOR AUTO PUMP
                Action = b1.cash()
                b1.box.opacity = 1
                b1.outcome.setColor(u'green')
                if MotherPacket['Run'] not in [1,6]:
                    b1.pumps = float(b1.pumps / 2.0)

            if Action or TimerAction:
                b1.update()
                self.window.flip()

        self.eventRecorder.RecordEvent('OutcomeScreen')
        core.wait(2)
        self.GameIm.setAutoDraw(False)
        
        return self.restart # If there are no errors, return False


    def Social(self, MotherPacket):
        '''
        Pariticpant plays a trial of the social game in any of the
        four conditions.
        '''
        event.Mouse(visible=False)
        self_icons = {
            '0': os.getcwd() + '/Resources/gameImages/Token_blue_you.png',
            '1': os.getcwd() + '/Resources/gameImages/Token_yellow_you.png'
        }
        other_icon = {
            '0': os.getcwd() + '/Resources/gameImages/Token_blue_other.png',
            '1': os.getcwd() + '/Resources/gameImages/Token_yellow_other.png'
        }

        # balloon instances
        b1 = balloon(self.window, 1, os.getcwd() + '/Resources/Balloons',self.eventRecorder)
        b2 = balloon(self.window, 2, os.getcwd() + '/Resources/Balloons',self.eventRecorder)

        b1.balloon.image = self.balloonColors[MotherPacket['Group']]
        p1im = self_icons[MotherPacket['Group']]

        if MotherPacket['In']:
            b2.balloon.image = b1.balloon.image
            p2im = other_icon[MotherPacket['Group']]
        else:
            b2.balloon.image = self.balloonColors[str(self.helpFlip(MotherPacket['Group']))]
            p2im = other_icon[str(self.helpFlip(MotherPacket['Group']))]
        self.eventRecorder.p1 = b1
        self.eventRecorder.p2 = b2


        P2Icon = visual.ImageStim(win = self.window,
                                image = p2im,
                                pos = [b2.xPos + 0.09,0.7],
                                size=[0.3 * self.aspectRatio, 0.3])

        P1Icon = visual.ImageStim(win = self.window,
                                image = p1im,
                                pos = [b1.xPos + 0.09,0.7],
                                size=[0.3 * self.aspectRatio, 0.3])


        self.RedEx.setText('')
        # Use subject ID's to generate valid port numbers for subject TCP sockets
        Port = int(1100 + MotherPacket['SubjectID'])
        P2port = int(1100 + MotherPacket['P2_ID'])

        # Establish TCP connection with other player
        if Port > P2port: # If player's SubjectID is larger than P2, act as server.
            core.wait(np.random.uniform(1,3)) # pause for a moment to ensure P2 is ready to establish connection
            # Begin connnection protocol
            Server = socket(AF_INET,SOCK_STREAM)
            Server.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
            Server.bind((gethostbyname(gethostname()),Port))
            Server.settimeout(10) # Set timeout for 10 seconds
            Server.listen(1)
            try:
                GameSock, clientaddr = Server.accept()
            except timeout: # If no connection is established within 10sec. return restart = True
                self.restart = True
                return True

        elif Port < P2port: # If player's SubjectID is smaller than P2, act as client.
            start = time.time()
            end = start + 10
            while 1: # For 10 seconds try to establish connection with server
                GameSock = socket(AF_INET,SOCK_STREAM)
                GameSock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
                try:
                    GameSock.connect((MotherPacket['P2_IP'],P2port))
                    break
                except error: # If no connection is established within 10sec. return restart = True
                    if time.time() >= end:
                        self.restart = True
                        return True


        self.fixation.draw()
        self.window.flip()
        # Trial handshake ensures that both computers start trial at exact same time
        GameSock.setblocking(1)
        GameSock.settimeout(180)
        if Port > P2port:
            GameSock.send('n')
            GameSock.recv(1)
        else:
            GameSock.recv(1)
            GameSock.send('n')
        GameSock.setblocking(0)

        core.wait(1)

        # Get Trial ready
        BothFinished = False
        b1.reset()
        b2.reset()
        b1.update()
        b2.update()
        P2Icon.setAutoDraw(True)
        P1Icon.setAutoDraw(True)
        self.RedEx.setAutoDraw(True)
        self.PreTrialSetup(MotherPacket)
        while not BothFinished:
            # Only update screen is something happens
            Action = False
            b2Action = False

            # Check if players have timed out
            Action = b1.timeOut(world = self.TrialTimer)
            b2Action = b2.timeOut(world = self.TrialTimer)


            # Check whether P2 sent a message
                # 1 = pump, 0 = popped, 2 = cashed
            Message = self.checkMessage(GameSock)
            if Message == '1':
                b2.pump()
                b2Action = True
            elif Message == '0':
                b2.pump()
                b2.pumps = 0
                self.eventRecorder.RecordEvent('P2_Pop')
                b2.popped = True
                b2.done = True
                b2Action = True
            elif Message == '2':
                b2Action = b2.cash()

            # Make Actions
            if b1.pumpAction(): # Pump and send message
                Action = True
                if b1.popped:
                    if self.sendMessage(GameSock, '0'):
                        self.rstart(); break # if something went wrong, end trial
                else:
                    if self.sendMessage(GameSock, '1'):
                        print 'pump'
                        self.rstart(); break # if something went wrong, end trial

            # if np.random.randint(0,1000000) < 10:                                # FOR AUTO PUMP
            if event.getKeys(['return']): # cash in and send messaged
                if b1.cash():
                    Action = True
                    if self.sendMessage(GameSock,'2'):
                        self.rstart(); break # if something went wrong, end trial


            # Determine winner of trial
            if b1.done and b2.done:
                if b1.pumps > b2.pumps:
                    b1.box.opacity = 1
                    b1.outcome.setColor(u'green')
                    if b1.cashed and b2.cashed:
                        self.RedEx.pos = b2.earned.pos
                        self.RedEx.setText('X')
                elif b1.pumps < b2.pumps:
                    b2.box.opacity = 1
                    b2.outcome.setColor(u'green')
                    if b1.cashed and b2.cashed:
                        self.RedEx.pos = b1.earned.pos
                        self.RedEx.setText('X')
                elif b1.pumps == b2.pumps:
                    if b1.cashed and b2.cashed:
                        b1.box.opacity = 1
                        b2.box.opacity = 1
                        b1.pumps = float(b1.pumps / 2.0)
                        b2.pumps = b1.pumps
                        b1.outcome.setColor(u'green')
                        b2.outcome.setColor(u'green')


                self.eventRecorder.RecordEvent('OutcomeScreen')
                Action = True
                BothFinished = True

            # Update the screen

            if Action or b2Action:
                b1.update()
                b2.update()
                if MotherPacket['Belief'] and not BothFinished:
                    self.Cover.draw()
                self.window.flip()

        GameSock.close() # close game TCP socket
        core.wait(np.random.uniform(2,3))
        self.GameIm.setAutoDraw(False)
        P2Icon.setAutoDraw(False)
        P1Icon.setAutoDraw(False)
        self.RedEx.setAutoDraw(False)
        return self.restart


if __name__ == '__main__':

    window = visual.Window(
                    size=[800, 500], monitor='testMonitor',
                    color=(0, 0, 0), fullscr=False, screen=0, allowGUI=False)
