import numpy as np
from psychopy import core


class simulated_player:
    def __init__(self, Type, b1, b2):
        self.Type = Type
        self.opponenet = b1
        self.agent = b2
        self.EV = np.random.randint(20,64)
        self.InitEV = self.EV
        self.timer = core.Clock()
        self.lastActionTime = 0
        self.pumpRate = 0.08
        self.stopCount = False

    def action_gating(self):
        if np.random.randint(10) > 8:# add some randomnness in action gating
            if self.agent.pumps < self.EV:
                if self.timer.getTime() - self.lastActionTime > self.pumpRate:
                    self.agent.pump()
                    self.lastActionTime = self.timer.getTime()

            if self.Type in ['AGR','HES']:
                Go = True if self.opponenet.done else False
            else:
                Go = True
            if self.agent.pumps == self.EV and Go:
                if self.timer.getTime() - self.lastActionTime > 1:
                    self.agent.cash()
                    self.lastActionTime = self.timer.getTime()


    def non_social_action(self):
        """
        The non social agent should pump to where it wants to go to.
        However, if P1 pups above the agent's EV, it should ajust its
        EV accordingly in order to win.
        """

        if not self.agent.done:
            if self.opponenet.cashed and self.opponenet.pumps >= self.agent.pumps:
                self.EV = self.opponenet.pumps + np.random.randint(1,5)

            self.action_gating()


    def non_social_action_SB(self):
        """
        same as non_social_action but has no access to player 1's behavior.

        """
        self.pumpRate = 0.4
        if not self.agent.done:
            self.action_gating()


    def aggressive_action(self):
        """
        always makes an attempt to pump a few more than the other player.
        if the other player ends, pumps a few more tiems.
        """
        if not self.agent.done:
            if not self.opponenet.done:
                self.EV = self.opponenet.pumps + np.random.randint(1,5)
            else:
                if not self.stopCount:
                    if self.opponenet.cashed:
                        self.EV = self.agent.pumps + np.random.randint(1,5)
                    elif self.opponenet.popped:
                        self.EV = self.agent.pumps + np.random.randint(1,10)
                    self.stopCount = True
            self.action_gating()


    def hesitant_action(self):
        """
        always stays a few pumps behind the player.If the player cashes in
        makes a very fast attempt to win. If the player pops, cashes in
        immediately.
        """
        if not self.agent.done:
            if not self.opponenet.done:
                self.EV = self.opponenet.pumps - np.random.randint(1,5)
            else:
                if self.opponenet.cashed:
                    self.EV = self.opponenet.pumps + 1
                elif self.opponenet.popped:
                    if not self.stopCount:
                        if self.agent.pumps == 0:
                            self.EV = np.random.randint(1,10)
                        else:
                            self.EV = self.agent.pumps
                        self.stopCount = True
            self.action_gating()


    def make_action(self):
        if self.Type == 'HES':
            self.hesitant_action()
        elif self.Type == 'AGR':
            self.aggressive_action()
        elif self.Type == 'NS':
            self.non_social_action()
        elif self.Type == 'SB':
            self.non_social_action_SB()
