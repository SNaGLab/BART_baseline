import socket
import pickle
import time
import os
import numpy as np
import pandas as pd
import logging
import datetime
from qLib2.qLib import *
from psychopy import visual, core, event, gui
import payment_methods
from encryptBART import encryptBART
import datetime



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

class Clock:
    '''
    Clock for monitoring the duration of experiment
    '''
    def __init__(self,window, mainDraw):
        self._start = core.Clock()
        self.timeStr = visual.TextStim(window,pos = [0,0.9], text = '00:00:00',color = 'black',colorSpace='rgb')
        self.timeStr.autoDraw = True
        mainDraw.append(self.timeStr)
    def _update(self):
        # Update the time using the _start timer
        self.timeStr.setText(time.strftime("%H:%M:%S",time.gmtime(self._start.getTime())))
    def reset(self):
        # clock should not start until start button is pressed
        self._start.reset()


class Button:
    '''
    a button stimulus that is either pressed or not
    '''
    def __init__(self,window, pos = [0,0],scale = 0.1,imagePath = '/Users/JMP/Documents/S_BART/S_BART.02/s_bart.02/Resources/gameImages/', im = 'Info.png'):
        self.window = window
        aspectRatio = (float(window.size[1])/float(window.size[0])) * scale
        self.im = im
        self.Scale = [aspectRatio*2,scale]
        self.Im = visual.ImageStim(window, image = imagePath + im ,pos = pos,size = self.Scale)
        self.Mouse = event.Mouse()
        self.imagepath = imagePath

        # when key is pressed, change to darker image
        splitim = self.im.split('.')
        splitim.insert(1,'dark')
        self.darkim =  '.'.join(splitim)

    def Pressed(self):
        self.Im.draw()
        if self.Mouse.isPressedIn(self.Im): # change color and return True
            self.Im.setImage(self.imagepath + self.darkim)
            core.wait(0.1)
            self.Im.setImage(self.imagepath + self.im)
            return True

def getTime():
    '''
    Gets the current time of any event
    '''
    dt = datetime.datetime(2015,5,24)
    timenow = dt.now()
    return str(timenow)


class row:
    def __init__(self,SubjID,ypos,window,mainDraw, SessionFrame, StateFrame):
        self.ypos = ypos
        xpos = -0.8
        self.SubjID = SubjID
        SessInfo = SessionFrame.loc[self.SubjID]
        StateInfo = StateFrame.loc[self.SubjID]

        self.ID = visual.TextStim(window,text = str(int(SessInfo.SubjectID)),color = 'black',colorSpace='rgb', pos = [xpos,self.ypos],height = 0.06)
        self.ID.autoDraw = True
        self.IDBox = visual.Rect(window, width=.2, fillColor=None, opacity=1, height=.1, pos = [xpos, ypos], lineColor = 'black', lineWidth=4)
        self.IDBox.autoDraw = True
        mainDraw.append(self.ID);mainDraw.append(self.IDBox)
        xpos += 0.2
        self.Run = visual.TextStim(window,text = str(int(SessInfo.Run)),color = 'black',colorSpace='rgb', pos = [xpos,self.ypos],height = 0.06)
        self.Run.autoDraw = True
        self.RunBox = visual.Rect(window, width=.2, fillColor=None, opacity=1, height=.1, pos = [xpos, ypos], lineColor = 'black', lineWidth=4)
        self.RunBox.autoDraw = True
        mainDraw.append(self.Run);mainDraw.append(self.RunBox)
        xpos += 0.2
        self.Trial = visual.TextStim(window,text = str(int(SessInfo.Trial)),color = 'black',colorSpace='rgb', pos = [xpos,self.ypos],height = 0.06)
        self.Trial.autoDraw = True
        self.TrialBox = visual.Rect(window, width=.2, fillColor=None, opacity=1, height=.1, pos = [xpos, ypos], lineColor = 'black', lineWidth=4)
        self.TrialBox.autoDraw = True
        mainDraw.append(self.Trial);mainDraw.append(self.TrialBox)
        xpos += 0.2
        self.Game = visual.TextStim(window,text = str(StateInfo.Playing),color = 'black',colorSpace='rgb',pos = [xpos,self.ypos],height = 0.06)
        self.Game.autoDraw = True
        self.Gamebox = visual.Rect(window, width=.2, fillColor=None, opacity=1, height=.1, pos = [xpos, ypos], lineColor = 'black', lineWidth=4)
        self.Gamebox.autoDraw = True
        mainDraw.append(self.Game);mainDraw.append(self.Gamebox)
        xpos += 0.2
        self.P2 = visual.TextStim(window,text = str(int(SessInfo.P2_ID)),color = 'black', colorSpace='rgb',pos = [xpos,self.ypos],height = 0.06)
        self.P2.autoDraw = True
        self.P2Box = visual.Rect(window, width=.2, fillColor=None, opacity=1, height=.1, pos = [xpos, ypos], lineColor = 'black', lineWidth=4)
        self.P2Box.autoDraw = True
        mainDraw.append(self.P2);mainDraw.append(self.P2Box)
        xpos += 0.2
        self.Soc = visual.TextStim(window,text = str(int(StateInfo.CountSocial)),color = 'black', colorSpace='rgb',pos = [xpos,self.ypos],height = 0.06)
        self.Soc.autoDraw = True
        self.SocBox = visual.Rect(window, width=.2, fillColor=None, opacity=1, height=.1, pos = [xpos, ypos], lineColor = 'black', lineWidth=4)
        self.SocBox.autoDraw = True
        mainDraw.append(self.Soc);mainDraw.append(self.SocBox)
        xpos += 0.2
        self.Alone = visual.TextStim(window,text = str(int(StateInfo.CountAlone)),color = 'black',colorSpace='rgb', pos = [xpos,self.ypos],height = 0.06)
        self.Alone.autoDraw = True
        self.AloneBox = visual.Rect(window, width=.2, fillColor=None, opacity=1, height=.1, pos = [xpos, ypos], lineColor = 'black', lineWidth=4)
        self.AloneBox.autoDraw = True
        mainDraw.append(self.Alone);mainDraw.append(self.AloneBox)
        xpos += 0.2
        self.AvailableBox = visual.Rect(window, width=.2, fillColor=None, opacity=1, height=.1, pos = [xpos, ypos], lineColor = 'black', lineWidth=4)
        self.AvailableBox.autoDraw = True
        mainDraw.append(self.AvailableBox)
        xpos += 0.2
        self.WaitingBox = visual.Rect(window, width=.2, fillColor=None, opacity=1, height=.1, pos = [xpos, ypos], lineColor = 'black', lineWidth=4)
        self.WaitingBox.autoDraw = True
        mainDraw.append(self.WaitingBox)
        xpos += 0.2

    def _update(self,SessionFrame,StateFrame):
        SessInfo = SessionFrame.loc[self.SubjID]
        StateInfo = StateFrame.loc[self.SubjID]
        self.Run.setText(str(int(SessInfo.Run)))
        self.Trial.setText(str(int(SessInfo.Trial)))
        self.Game.setText(str(StateInfo.Playing))
        self.P2.setText(str(int(SessInfo.P2_ID)))
        self.Soc.setText(str(int(StateInfo.CountSocial)))
        self.Alone.setText(str(int(StateInfo.CountAlone)))
        
        if StateInfo.Available:
            self.AvailableBox.fillColor = u'black'
        else:
            self.AvailableBox.fillColor = None
        if StateInfo.Send:
            self.WaitingBox.fillColor = u'black'
        else:
            self.WaitingBox.fillColor = None



class Server():
    def __init__(self, configs):
        self.yP = 0.7
        self.playerList = []
        self.mainDraw = []
        self.basepath = os.path.dirname(os.path.realpath(__file__))

        try:
            self.FilePath = configs['FilePath']
        except KeyError:
            print 'No Path specified in configurations, using basepath'

        self.window = visual.Window(
                    size=[1000,500], monitor='testMonitor',color='white', colorSpace='rgb',fullscr=False, screen=0,
                    allowGUI=True
                    )

        self.TaskTimer = core.Clock()
        self.WorldClock = core.CountdownTimer()
        self.lastTime = self.TaskTimer.getTime()

        try:
            address = configs['address']
        except KeyError:
            print 'No host and port specified in configurations. Default address set to (localhost, 11111)'
            address = ('',11111)

        try:
            self.aloneTime = configs['aloneTime']
        except KeyError:
            print 'No alone block time specified in configurations. Default alone block time is 240 sec.'
            self.aloneTime = 240

        try:
            self.socialTime = configs['socialTime']
        except KeyError:
            print 'No alone block time specified in configurations. Default social block time is 900 sec.'
            self.socialTime = 900

        self.password = configs['password']
        self.Mother = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.Mother.bind(address)
        self.Mother.setblocking(0)

    def newConnection(self, player, message):
        '''
        Add a new subject to the dataframe with a unique Subject
        ID.
        '''

        # randomly generate a subjectID for player that is not yet used for experiment
        Subnum = int(np.random.randint(1, 500))
        while (str(Subnum) in os.listdir(os.getcwd() + '/Data')) or (Subnum in list(self.SessionFrame.SubjectID)):
            Subnum = int(np.random.randint(1, 500))

        # split message to get contactID
        contactID,compNum = message.split('-')

        # add subject to Session DataFrame
        self.SessionFrame.loc[Subnum] = [Subnum, player[0], int(player[1]),
                                         self.Session, 1, 0, 'Single Player',
                                         0, 0, 0, False,contactID,compNum]
        logging.debug(getTime() + ': Player %s: self.SessionFrame row added' % Subnum)

        # add subject to subject state dataframe
        self.StateFrame.loc[Subnum] = [False, 'Single Player', 0, 0, 0, 0, False]
        logging.debug(getTime() + ': Player %s: StateFrame row added' % Subnum)

        # Add a visual row for subject into UI maindraw
        self.yP -= .1
        self.playerList.append(row(Subnum, self.yP, self.window, self.mainDraw, self.SessionFrame, self.StateFrame))
        self.SingleUpdate(Subnum)

    def setSinglePlayer(self, sub):
        self.StateFrame.loc[sub, 'Available'] = False
        self.StateFrame.loc[sub, 'Playing'] = 'Single Player'
        self.SessionFrame.loc[sub, 'Game'] = 'Single Player'
        self.SessionFrame.loc[sub, 'P2_IP'] = 0
        self.SessionFrame.loc[sub, 'P2_PORT'] = 0
        self.SessionFrame.loc[sub, 'P2_ID'] = 0
        logging.debug(getTime() + ': Player %s: set to single player' % sub)

    def setMultiPlayer(self, sub):
        self.StateFrame.loc[sub, 'Available'] = True
        self.StateFrame.loc[sub, 'Playing'] = 'MultiPlayer'
        self.SessionFrame.loc[sub, 'Game'] = 'MultiPlayer'
        logging.debug(getTime() + ': Player %s: set to multiplayer' % sub)

    def RunChecker(self, sub):
        '''
        Checks the world timer to see if run timer has run out. If it has subject
        is placed in Break.
        '''
        logging.debug(getTime() + ': Player %s: checking run' % sub)
        if self.WorldClock.getTime() <= 0:
            if self.SessionFrame.loc[sub, 'Run'] == 6:  # if last run of experiment
                self.StateFrame.loc[sub, 'Playing'] = 'Done'
                logging.debug(getTime() + ': Player %s: set players playing to Done' % sub)
            else:  # otherwise go to break
                self.StateFrame.loc[sub, 'Playing'] = 'Break'
                logging.debug(getTime() + ': Player %s: set players playing to Break' % sub)
                self.StateFrame.loc[sub, 'Available'] = False

    def selectGame(self, sub):
        '''
        Selects what game subject will play.
        '''
        logging.debug(getTime() + ': Player %s: selecting game' % sub)

        if self.StateFrame.loc[sub, 'CountAlone'] < 2:
            if np.random.uniform(10) > 7:
                self.setSinglePlayer(sub)
            else:
                self.setMultiPlayer(sub)
        else:
            self.setMultiPlayer(sub)

        if self.SessionFrame.loc[sub, 'Run'] in [1, 6]:
            self.setSinglePlayer(sub)

        self.RunChecker(sub)

    def GetSubNum(self, player):
        '''
        find the correspoinding index for the subject's IP and PORT
        '''
        subnum = self.SessionFrame[(self.SessionFrame.IP == player[0])].index[0]
        self.SessionFrame.loc[subnum, 'PORT'] = player[1]
        return subnum

    def UpdateState(self, player, Issue=False):
        '''
        When subject sends a message, update their information. If Issue
        was sent to mother, than dont update any information and send
        back the current trial information.
        '''

        sub = self.GetSubNum(player)
        logging.debug(getTime() + ': Player %s: updating state' % sub)

        self.StateFrame.loc[sub, 'Send'] = True
        self.StateFrame.loc[sub, 'TimeIn'] = time.time()
        self.StateFrame.loc[sub, 'WaitTill'] = self.StateFrame.loc[sub, 'TimeIn'] + np.random.uniform(3, 6)
        if not Issue:
            if self.StateFrame.loc[sub, 'Playing'] == 'MultiPlayer':
                logging.debug(getTime() + ': Player %s: added a multiplayer trial' % sub)
                self.StateFrame.loc[sub, 'CountSocial'] += 1
                self.SessionFrame.loc[sub, 'Trial'] += 1
            elif self.StateFrame.loc[sub, 'Playing'] == 'Single Player':
                logging.debug(getTime() + ': Player %s: added a single player trial' % sub)
                self.StateFrame.loc[sub, 'CountAlone'] += 1
                self.SessionFrame.loc[sub, 'Trial'] += 1
            if self.SessionFrame.loc[sub, 'Rating']:
                self.SessionFrame.loc[sub, 'Rating'] = False
        self.selectGame(sub)
        self.SingleUpdate(sub)

    def TimeOut(self):
        '''
        checks StateFrame for individuals who timed out
        '''

        Available = self.StateFrame[self.StateFrame.Available]
        if len(Available) > 0:
            TimedOut = Available.WaitTill.apply(lambda x: x - time.time() <= 0)
            for sub in TimedOut[TimedOut].index:
                logging.debug(getTime() + ': Player %s: timed out' % sub)
                self.setSinglePlayer(sub)
                self.SingleUpdate(sub)


    def AssignPairs(self):
        '''
        If there are several individuals available, grab the player who
        has been waiting the longest, and assign them to another ranodm
        player.
        '''

        Available = self.StateFrame[self.StateFrame.Available]
        if len(Available) > 1:
            logging.debug(getTime() + ': available players for pairing')
            Available = Available.sort('TimeIn')
            AvailableSession = self.SessionFrame.loc[Available.index]

            p1 = Available.index[0]
            p1_info = self.SessionFrame.loc[p1]

            AvailableInRunFrame = AvailableSession[(AvailableSession.Run == p1_info.Run) &
                                                   (AvailableSession.SubjectID != p1_info.SubjectID) &
                                                   (AvailableSession.SubjectID != p1_info.P2_ID)].index


            if len(AvailableInRunFrame) > 0:
                AvailableInRun = Available.loc[AvailableInRunFrame]

                p2 = np.random.choice(AvailableInRun.index)
                p2_info = self.SessionFrame.loc[p2]

                self.SessionFrame.loc[p1, 'P2_IP'] = p2_info.IP
                self.SessionFrame.loc[p1, 'P2_PORT'] = p2_info.PORT
                self.StateFrame.loc[p1, 'Available'] = False
                self.SessionFrame.loc[p1, 'P2_ID'] = p2_info.SubjectID
                logging.debug(getTime() + ': Player %s: paired for multiplayer' % p1)
                self.SessionFrame.loc[p2, 'P2_IP'] = p1_info.IP
                self.SessionFrame.loc[p2, 'P2_PORT'] = p1_info.PORT
                self.StateFrame.loc[p2, 'Available'] = False
                self.SessionFrame.loc[p2, 'P2_ID'] = p1_info.SubjectID


                logging.debug(getTime() + ': Player %s: paired for multiplayer' % p2)
                self.SingleUpdate(p1)
                self.SingleUpdate(p2)

    def send(self, sub):
        IP = self.SessionFrame.loc[sub, 'IP']
        PORT = int(self.SessionFrame.loc[sub, 'PORT'])
        self.SessionFrame.loc[sub, "Game"] = self.StateFrame.loc[sub, 'Playing']
        MotherPacket = pickle.dumps(self.SessionFrame.loc[sub].to_dict())

        self.Mother.sendto(MotherPacket, (IP, PORT))

    def SendPackets(self):
        '''
        for all expired times, send that player's information`
        '''
        Ready = self.StateFrame[(self.StateFrame.WaitTill - time.time() <= 0) &
                                (self.StateFrame.Send)]
        # Before sending any information, check for timeouts
        self.TimeOut()
        for sub in Ready.index:
            self.send(sub)
            self.StateFrame.loc[sub, 'Send'] = False
            logging.debug(getTime() + ': Player %s: sent packet' % sub)
            self.SingleUpdate(sub)


    def breakbreaker(self):
        '''
        Allows players to take a break for 15s and begins next run
        with single player
        '''
        InBreak = list(self.StateFrame.Playing.apply(lambda x: x == 'Break'))
        if False not in InBreak and len(InBreak) > 0:
            if time.time() >= float(self.StateFrame.sort('TimeIn').tail(1).TimeIn + 15):

                logging.debug(getTime() + ': breaking out of break')
                for sub in list(self.StateFrame.index):
                    self.StateFrame.loc[sub, 'CountSocial'] = 0
                    self.StateFrame.loc[sub, 'CountAlone'] = 0
                    self.SessionFrame.loc[sub, 'Run'] += 1
                    self.SessionFrame.loc[sub, 'Rating'] = True


                    self.setSinglePlayer(sub)
                    MotherPacket = pickle.dumps(self.SessionFrame.loc[sub].to_dict())

                    IP = self.SessionFrame.loc[sub, 'IP']
                    PORT = int(self.SessionFrame.loc[sub, 'PORT'])

                    self.Mother.sendto(MotherPacket, (IP, PORT))
                    logging.debug(getTime() + ': Player %s: sent break out of break' % sub)
                    self.SingleUpdate(sub)

                if self.SessionFrame.loc[sub, 'Run'] == 6:
                    self.WorldClock.reset(self.aloneTime)
                else:
                    self.WorldClock.reset(self.socialTime)



    def FrameManipulations(self):
        self.AssignPairs()
        self.SendPackets()

        self.breakbreaker()

    def recv(self):
        '''
        Basic receive function
        '''
        try:
            a, b = self.Mother.recvfrom(1000)
            return (a, b)
        except:
            return (None, None)

    def DrawHeader(self):
        ListNames = ['SubjectID', 'Run', 'Trial', 'Game', 'P2', 'Soc', 'Alone', 'Available', 'Waiting']
        ypos = 0.75
        xpos = -0.8
        HeadersBox = []
        Headers = []
        for c, i in enumerate(ListNames):
            HeadersBox.append(
                visual.Rect(self.window, width=.2, fillColor='blue', opacity=0.5, height=.15, pos=[xpos, ypos],
                            lineColor='black', lineWidth=4))
            Headers.append(
                visual.TextStim(self.window, text=i, pos=[xpos, ypos], color='black', colorSpace='rgb', height=0.075))
            xpos += 0.2
        for i in HeadersBox:
            i.autoDraw = True
            self.mainDraw.append(i)
        for i in Headers:
            i.autoDraw = True
            self.mainDraw.append(i)
        
    def SingleUpdate(self,Sid):
        next((player for player in self.playerList if player.SubjID == Sid), None)._update(self.SessionFrame,
                                                                                           self.StateFrame)

    def FinishUpdate(self, player):
        Sid = self.GetSubNum(player)
        next((player for player in self.playerList if player.SubjID == Sid), None).AvailableBox.fillColor = 'red'
        next((player for player in self.playerList if player.SubjID == Sid), None).WaitingBox.fillColor = 'red'

    def setupSession(self):

        """
        Initializes session by requesting session number and setting up session dataframe.

        """
        sessionField = textField(window=self.window,
                                 drawList=[
                                     visual.TextStim(win=self.window, height=.08, wrapWidth=1.5,
                                                    text=('Session.'), color='black', colorSpace='rgb',
                                                    pos=[0, .3])
                                 ],
                                 clock=None, label='', labelColor='black', maxChars=3, size=.08, text=00, type='int')

        self.Session = int(sessionField[0][0])


        self.SessionFrame = pd.DataFrame(
            columns=['SubjectID', 'IP', 'PORT', 'Session', 'Run', 'Trial',
                     'Game', 'P2_ID', 'P2_IP', 'P2_PORT', 'Rating', 'ContactID','Computer'])

        self.StateFrame = pd.DataFrame(columns=['Available', 'Playing',
                                           'CountSocial', 'CountAlone',
                                           'TimeIn', 'WaitTill', 'Send'])



    def beginSession(self):
        start = False
        fin = False

        self.DrawHeader()
        
        StartB = Button(self.window, pos=[-0.2, 0.9], imagePath= self.basepath + '/Resources/gameImages/', im='Start.png')
        StopB = Button(self.window,pos = [0.2,0.9],imagePath = self.basepath + '/Resources/gameImages/', im = 'Stop.png')
        while not fin:
            message, player = self.recv()
            if message:
                if player[0] not in list(self.SessionFrame.IP):
                    self.newConnection(player,message)
                if start:
                    if message == 'NEWGAME':
                        self.UpdateState(player)
                    elif message == 'ISSUE':
                        self.UpdateState(player,Issue = True)
                    elif message == 'FIN':
                        self.FinishUpdate(player)

            if StartB.Pressed() and not start:
                start = True
                self.WorldClock.reset(self.aloneTime)
                

                for sub in list(self.StateFrame.index):
                    IP = self.SessionFrame.loc[sub,'IP']
                    PORT = int(self.SessionFrame.loc[sub,'PORT'])
                    self.Mother.sendto(str(int(sub)), (IP,PORT))
            
            elif StopB.Pressed():
                fin = True
                
                LinkerFrame = self.SessionFrame[['SubjectID','ContactID']]
                encryptBART(LinkerFrame,self.Session,self.basepath + '/payments',self.password)
                printframe = self.SessionFrame[['SubjectID','Computer','Session']]
                printframe.Time = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
                printframe.to_csv(self.basepath + '/payments/IP_subjects_%s.csv'%self.Session)

            self.FrameManipulations()

            if self.TaskTimer.getTime() - self.lastTime >= 0.5:
                self.window.update()
                self.lastTime = self.TaskTimer.getTime()
        
        for i in self.mainDraw:
            i.autoDraw = False
        
    def endTask(self):
        
        # calculate bonuses
        frame = payment_methods.GetAllSubs(self.basepath + '/Data',self.Session)
        frame.to_csv(self.basepath + '/payments/subjectPaymentFrame_%s.csv'%self.Session)
        

    def Run(self):
        self.setupSession()
        self.beginSession()
        self.endTask()



if __name__ == '__main__':
    expInfo = {'Linker_password': ''}
    dlg = gui.DlgFromDict(dictionary=expInfo)
    if dlg.OK is False:
        core.quit()

    Server({
        'aloneTime': 240,
        'socialTime': 600,
        'password': expInfo['Linker_password']
    }).Run()
