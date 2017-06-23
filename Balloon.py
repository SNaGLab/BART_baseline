'''
Balloon Class for BART_0.2 & 0.3
Code: Jacob M. Parelman
Date: 06-28-2016
'''

from psychopy import visual, event, core, gui
from pyglet.window import key
import numpy as np

class balloon:
    '''Balloon to be displayed for BART tasks. Can be player 1 or 2.
    All actions or events that can occur in BART are implemented in
    class method calls.
    '''

    def __init__(self,
                 window,            # The main task window
                 player = 1,        # Must be 0, 1 or 2
                 stimPath = None,   # Path to all stim
                 eventRecorder = None,
                 practice = False
                 ):
        '''
        window = the psychopy visual.window for displaying balloon
        player = 0 for single player (centered on screen)
                 1 for player 1 in multiplayer (left on screen)
                 2 for player 2 in multiplayer (right on screen)
        stimPath = path to images, should be stored in 'Resources' folder
        eventRecorder = Data_Handler class for recording all balloon events
        practice = if True does not record events
        '''
        # balloon state information
        self.practice = practice
        self.done = False           # True if popped or cashed
        self.popped = False
        self.cashed = False
        self.timedOut = False
        self.pumps = 0
        self.max = 0                # balloons pop point
        self.player = player
        self.eventRecorder = eventRecorder

        # Pump timing and key information for pumping behavior
        self.pumpTimer = core.Clock()
        self.FirstPump = True
        self.firstTime = 0
        self.eventTime = 0
        self.keyState = key.KeyStateHandler()
        window.winHandle.push_handlers(self.keyState)

        # Set balloon color and position
        if player == 1:
            self.xPos = -0.5
            self.bImage = stimPath + '/BlueBalloonFull.png'
        elif player == 2:
            self.xPos = 0.5
            self.bImage = stimPath + '/YellowBalloonFull.png'
        else:
            self.xPos = 0.0
            self.bImage = stimPath + '/BlueBalloonFull.png'

        # Visual Stim for the player
        self.aspectRatio = (float(window.size[1]) / float(window.size[0]))
        self.earned = visual.TextStim(win = window,
                                      text = '0',
                                      color = 'black',
                                      pos = [self.xPos - 0.10, 0.7],
                                      height = 0.15
                                      )

        self.Ex = visual.TextStim(win=window,
                            text=' ',
                            color='red',
                            pos = [self.xPos - 0.10, 0.7],
                            height = 0.2)

        self.balloon = visual.ImageStim(win = window,
                                        image = self.bImage,
                                        pos = [self.xPos, 0.0],
                                        size = (0.05 * self.aspectRatio, 0.05)
                                        )

        self.outcome = visual.TextStim(win = window,
                                       text = '',
                                       color = 'black',
                                       pos = self.balloon.pos
                                       )

        self.box = visual.Rect(win = window,
                               width=.8,
                               fillColor=None,
                               opacity=1,
                               height= 1.8,
                               pos = [self.balloon.pos[0],self.balloon.pos[1]],
                               lineColor = 'green',
                               lineWidth=4)


    def update(self):
        '''
        Update the display with current balloon states
        '''

        # set text stimuli for balloon based no state
        if not self.done:
            self.balloon.draw()
        else:
            self.outcome.draw()
        if self.cashed:
            self.box.draw()
        self.earned.draw()



    def reset(self):
        '''
        reset balloon information for new trial
        '''
        self.pumps = 0
        self.cashed = False
        self.popped = False
        self.timedOut = False
        self.done = False
        self.outcome.setText('')
        self.outcome.setColor(u'black')
        if self.player < 2:
            self.max = np.random.choice(range(1,65))
        else:
            self.max = 100 #P2 pop events are not implemented by class, implemented by messages from P2
        self.box.opacity = 0

        self.balloon.setSize(
            (((self.pumps + 5) * .01) * self.aspectRatio,
             (self.pumps + 5) * .01))  # sets balloon size according to pumps

        if self.pumps % 1 == 0:
            self.pumps = int(self.pumps)  # make sure that whole numbers don't print as floats

        self.earned.setText("%s" % (self.pumps))

    def pumpAction(self):
        '''
        Allows player to press or hold pump button to pump balloon.
        Returns bool for whether action was made.
        '''
        # if np.random.randint(0,1000000) < 100 and not self.done:   # FOR AUTO PUMP
        if self.keyState[key.SPACE] and not self.done: # if key is down and not done
            if self.FirstPump: # hold for an initial 500ms before rapid pumping
                self.firstTime = self.pumpTimer.getTime()
                self.pump()
                self.FirstPump = False
                self.eventTime = self.pumpTimer.getTime()
                return True
            if self.pumpTimer.getTime() >= self.firstTime + 0.5: # rapid pump if 500ms passed and key still down
                if self.pumpTimer.getTime() >= self.eventTime + 0.1:
                    self.pump()
                    self.eventTime = self.pumpTimer.getTime()
                    return True
        else: # once key is not down, initial 500ms resets
            self.FirstPump = True
            return False

    def pump(self):
        '''
        pumps balloon once, records event and checks for pop
        '''
        self.pumps += 1
        self.balloon.setSize(
            (((self.pumps + 5) * .01) * self.aspectRatio,
             (self.pumps + 5) * .01))  # sets balloon size according to pumps

        if self.pumps % 1 == 0:
            self.pumps = int(self.pumps)  # make sure that whole numbers don't print as floats

        self.earned.setText("%s" % (self.pumps))

        if not self.practice:
            if self.player == 2:
                self.eventRecorder.RecordEvent('P2_Pump')
            else:
                self.eventRecorder.RecordEvent('Pump')
        if self.pumps >= self.max:
            self.pumps = 0
            if not self.practice:
                if self.player == 2:
                    self.eventRecorder.RecordEvent('P2_Pop')
                else:
                    self.eventRecorder.RecordEvent('Pop')
            self.earned.setText('0')
            self.outcome.setText('Popped!')
            self.outcome.setColor(u'red')
            self.popped = True
            self.done = True


    def cash(self):
        '''
        Cashes balloon and records event
        '''
        if not self.done and self.pumps > 0:
            if not self.practice:
                if self.player == 2:
                    self.eventRecorder.RecordEvent('P2_Cash')
                else:
                    self.eventRecorder.RecordEvent('Cash')
            self.outcome.setText('Cashed In')
            self.cashed = True
            self.done = True
            return True
        else:
            return False

    def timeOut(self, world = None, countdown = None):
        '''
        Checks for whether participant has timed out.

        world = the world clock for trial 4 min max
        countdown = countdown clock for Timer condition
        '''
        if not self.done:
            if countdown:
                if countdown.getTime() <= 0:
                    self.timedOut = True
                    self.done = True
                    if not self.practice:
                        if self.player == 2:
                            self.eventRecorder.RecordEvent('P2_TimedOut')
                        else:
                            self.eventRecorder.RecordEvent('P1_TimedOut')
                    self.earned.setText('0')
                    self.outcome.setText('Timed out')
                    self.outcome.setColor(u'red')
                    self.pumps = 0
                    return True

            if world.getTime() <= 0:
                self.timedOut = True
                self.done = True
                if not self.practice:
                    if self.player == 2:
                        self.eventRecorder.RecordEvent('P2_TimedOut')
                    else:
                        self.eventRecorder.RecordEvent('P1_TimedOut')
                self.pumps = 0
                return True
        return False
