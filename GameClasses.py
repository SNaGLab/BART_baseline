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
        self.Competitive = self.eventRecorder.Competitive

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

        b1 = balloon(self.window, 0, os.getcwd() + '/Resources',self.eventRecorder)
        self.eventRecorder.p1 = b1
        self.eventRecorder.p2 = None
        # Get Trial ready
        b1.reset()
        self.PreTrialSetup(MotherPacket)

        if int(MotherPacket['Run']) in [2,3,4,5]:
            # If subject must make a belief rating, allow them to do so
            if MotherPacket['Rating']:
                WithinTaskRating(self.window, self.path, MotherPacket)

        else:
            if MotherPacket['Run'] > 5:
                if MotherPacket['Rating']:
                    WithinTaskRating(self.window, self.path, MotherPacket, both=False)


        event.Mouse(visible=False)

        b1.update()
        self.window.flip()

        while not b1.done:
            Action = False     # Only update screen if something happens

            TimerAction = b1.timeOut(world = self.TrialTimer)


            Action = b1.pumpAction() # pump

            # Cash in
            # if np.random.randint(0, 1000000) < 10:
            if event.getKeys(['return']):                     # FOR AUTO PUMP
                Action = b1.cash()
                if self.Competitive == '1':
                    b1.box.opacity = 1
                b1.outcome.setColor(u'green')

            if Action or TimerAction:
                b1.update()
                self.window.flip()

        self.eventRecorder.RecordEvent('OutcomeScreen')
        core.wait(2)

        return self.restart # If there are no errors, return False


    def Social(self, MotherPacket):
        '''
        Pariticpant plays a trial of the social game in any of the
        four conditions.
        '''
        event.Mouse(visible=False)

        # balloon instances
        b1 = balloon(self.window, 1, os.getcwd() + '/Resources',self.eventRecorder)
        b2 = balloon(self.window, 2, os.getcwd() + '/Resources',self.eventRecorder)


        self.eventRecorder.p1 = b1
        self.eventRecorder.p2 = b2

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

        b1.Ex.setAutoDraw(True)
        b2.Ex.setAutoDraw(True)
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
                if self.Competitive == '0':
                    b2.outcome.setColor(u'green')


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
                    if self.Competitive == '0':
                        b1.outcome.setColor(u'green')
                    if self.sendMessage(GameSock,'2'):
                        self.rstart(); break # if something went wrong, end trial


            # Determine winner of trial
            if b1.done and b2.done:
                if self.Competitive == '1':
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



                self.eventRecorder.RecordEvent('OutcomeScreen')
                Action = True
                BothFinished = True

            # Update the screen

            if Action or b2Action:
                b1.update()
                b2.update()
                self.window.flip()

        GameSock.close() # close game TCP socket
        core.wait(np.random.uniform(2,3))
        b1.Ex.setAutoDraw(False)
        b2.Ex.setAutoDraw(False)
        return self.restart


if __name__ == '__main__':

    window = visual.Window(
                    size=[800, 500], monitor='testMonitor',
                    color=(0, 0, 0), fullscr=False, screen=0, allowGUI=False)

