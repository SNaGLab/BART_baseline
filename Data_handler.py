'''
Data Handler for S_BART_0.2 & 0.3
Code: Jacob M. Parelman
Date: 06-28-2016
'''

import os
from psychopy import core

class Data_Handler:
    '''Records all events during the S_BART test
    '''

    def __init__(self, FilePath, p1 = None, p2 = None):
        self.headerMade = False
        self.Group = 0
        self.Session = 0        # The Session that the subject is in
        self.SubjectID = 0      # Subject ID
        self.Belief = 0          # Social belief or no
        self.In = 0            # In group or outgroup play
        self.Run = 1            # Run that subject is in
        self.Game = 0           # 0 = Alone, 1 = Comp
        self.Trial = 1          # Trial number for specific game
        self.Max = 0            # Players poppoint
        self.P2 = 0             # Player 2's unique ID
        self.path = FilePath    # Path to file for data writing
        self.p1 = p1,           # Balloon class for player 1
        self.p2 = p2,           # Balloon class for possible player 2
        self.clock = core.Clock()
        self.Header = ['Session',
                  'SubjectID',
                  'Group',
                  'Belief',
                  'In',
                  'Run',
                  'Game',
                  'Trial',
                  'Fixation',
                  'StartPlay',
                  'OutcomeScreen',
                  'Winner',
                  'Pump',
                  'Cash',
                  'Pop',
                  'P1_TimedOut',
                  'Tokens',
                  'P1_PopPoint',
                  'P2_SubjectID',
                  'P2_Pump',
                  'P2_Cash',
                  'P2_Pop',
                  'P2_Tokens',
                  'P2_TimedOut',
                  'TimeOnset',
                  'Restart'
                  ]

    def MakeHeader(self):
        '''
        Once subject has their subject ID assigned by server, a header is made
        for the top of the csv file.
        '''
        self.headerMade = True
        with open(self.path + '/Data_%s.csv'%self.SubjectID, mode = 'a') as MyFile:
            row = ','.join(str(element) for element in self.Header)
            MyFile.write('%s\n'%row)


    def RecordEvent(self,event):
        '''
        grabs all possible information available from p1 and p2 and records
        such informaion along with event.
        '''
        row = [0 for i in range(len(self.Header))]
        # Record all available information to row
        row[self.Header.index(event)] = '1' # event receives a 1 if occuring
        row[self.Header.index('TimeOnset')] = self.clock.getTime()
        row[self.Header.index('Session')] = self.Session
        row[self.Header.index('SubjectID')] = self.SubjectID
        row[self.Header.index('Group')] = self.Group
        row[self.Header.index('Belief')] = self.Belief
        row[self.Header.index('In')] = self.In
        row[self.Header.index('Run')] = self.Run
        row[self.Header.index('Game')] = self.Game
        row[self.Header.index('Trial')] = self.Trial

        if self.p1: # grab informatio nfrom P1 balloon if available
            row[self.Header.index('Tokens')] = self.p1.pumps
            row[self.Header.index('P1_PopPoint')] = self.p1.max

        if self.p2: # grab informatio nfrom P2 balloon if available
            row[self.Header.index('P2_SubjectID')] = self.P2
            row[self.Header.index('P2_Tokens')] = self.p2.pumps

        # Outcome/Winner recording logic
        if event == 'OutcomeScreen':
            # Determine winner of trial
            if self.Game == 'MultiPlayer' or self.Game == 'Learning Multi Rules':
                if (self.p1.pumps >= self.p2.pumps) and not self.p1.popped:
                    row[self.Header.index('Winner')] = 1

            else:
                if self.p1.cashed:
                    row[self.Header.index('Winner')] = 1

        with open(self.path + '/Data_%s.csv'%self.SubjectID, mode = 'a') as MyFile:
            Row = ','.join(str(element) for element in row)
            MyFile.write('%s\n'%Row)


    def ConfigureDataHandlerGameInformation(self, MotherPacket):
        '''
        All information about computers is stored on the server.
        Every communication with a client is in the form of a
        serialized dictionary. The information contained includes
        the following information about the player.
        '''
        print MotherPacket
        self.Session = MotherPacket['Session']
        self.SubjectID = MotherPacket['SubjectID']
        self.Belief = 1 if MotherPacket['Belief'] else 0
        self.In = 1 if MotherPacket['In'] else 0
        self.Run = MotherPacket['Run']
        if MotherPacket['Game'] == 'MultiPlayer':
            self.Game = 1
        elif MotherPacket['Game'] == 'Break':
            self.Game = 3
        else:
            self.Game = 0
        self.Trial = MotherPacket['Trial']
        self.P2 = MotherPacket['P2_ID']
        self.Group = MotherPacket['Group']
        if not self.headerMade:
            self.MakeHeader()
