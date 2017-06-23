from psychopy import visual, event, core, gui
import numpy as np
import os

Bins = []
Coins = []
Deleters = []
coinIndexes = []
def make_rectangle_vertices(x,y,width,height):
    topLeft = [x,y]
    topRight = [x+width,y]
    bottomRight = [x+width,y-height]
    bottomLeft = [x,y-height]
    return [topLeft,topRight,bottomRight,bottomLeft]
    
   
class Container:
    def __init__(self, win, xPos,yPos,width,height):
        self.xPos = xPos
        self.yPos = yPos
        self.width = width
        self.height = height
        Verts = make_rectangle_vertices(xPos,yPos,width,height)
        self.border = visual.ShapeStim(win,lineWidth=2,lineColor='black',closeShape=False,vertices=[[self.xPos,self.yPos],[self.xPos,self.yPos - self.height],[self.xPos + self.width, self.yPos - self.height],[self.xPos + self.height,self.yPos]])

class Bin:
    def __init__(self, win, xPos,index,container):
        self.xPos = xPos
        self.yPos = 0.65
        self.index = index
        self.width = container.width / 10
        self.height = container.height - 0.15
        self.bottom = container.yPos - container.height + 0.142
        self.inBin = 0
        Verts = make_rectangle_vertices(self.xPos,self.yPos,self.width,self.height)
        self.Bin = visual.ShapeStim(win, lineWidth=2,lineColor=None,closeShape=True,vertices=Verts)
        if index == 0: lineCo = None
        else: lineCo = '#666666'
        self.Border = visual.ShapeStim(win,lineWidth=2,lineColor=lineCo,vertices = [[self.xPos,self.yPos],[self.xPos,self.yPos - self.height]])
        self.Text = visual.TextStim(win,'%s-%s'%(self.index*10,(self.index+1)*10) + '%', alignHoriz = 'center', color='black',pos = [self.xPos + (self.width/2),self.yPos - self.height - 0.18], height = 0.04)

class Coin:
    def __init__(self, win, bin,container,ci):
        self.gravity = 0.005
        self.speed = 0.005
        self.gravitySpeed = 0
        self.xPos = bin.xPos
        self.index = bin.index
        self.width = bin.width
        self.height = bin.height/50
        self.container = container
        self.yPos = bin.bottom + (self.container.height/50)
        self.coinIndex = np.random.randint(0,1000000)
        while self.coinIndex in ci:
            self.coinIndex = np.random.randint(0,1000000)
            
        Verts = make_rectangle_vertices(self.xPos,self.yPos,self.width,self.height)
        self.Coin = visual.ShapeStim(win, fillColor="yellow", lineWidth=2,lineColor='black',closeShape=True,vertices=Verts)
        
class Deleter:
    def __init__(self,win, xPos,index,container):
        self.xPos = xPos
        self.yPos = container.yPos - container.height + 0.15
        self.index = index
        self.width = container.width / 10
        self.height = 0.15
        Verts = make_rectangle_vertices(self.xPos,self.yPos,self.width,self.height)
        self.Deleter = visual.ShapeStim(win, fillColor="#ff8080", lineWidth=2,lineColor='black',closeShape=True,vertices=Verts)
        self.Text = visual.TextStim(win,'remove', alignHoriz = 'left', color='black',pos = [self.xPos + 0.025,self.yPos - 0.075], height = 0.05)
        
class Distributor:
    def __init__(self, win, maxVal, instructions = None, maxTotal = 50):
        self.win = win
        self.maxTotal = maxTotal
        self.container = Container(self.win, -0.75,0.65,1.5,1.5)
        self.xp = self.container.xPos
        self.Bins = []
        self.Coins = []
        self.Deleters = []
        self.coinIndexes = []
        self.mouse = event.Mouse(win = self.win)
        self.clockT = core.Clock()
        self.lastClick = self.clockT.getTime()
        self.continueButton = visual.ImageStim(self.win, os.getcwd() + '/Resources/gameImages/right_arrow.png', pos=[0.85,0], size=[0.1,0.1])
        self.BetCounter = visual.TextStim(self.win, '%s Bets'%0, pos=[0,0.68],color='black',height = 0.06)
        if instructions:
            self.instructions = visual.TextStim(self.win, instructions, pos=[-0.9,0.85],color='black',height=0.05,alignHoriz='left', wrapWidth = 1.8)
        else: self.instructions = None
        self.otherstimList = [visual.TextStim(self.win, '0', pos=[-0.77,-0.91],color='black',height=0.05),
                              visual.ShapeStim(win,lineWidth=1,lineColor='black',vertices = [[-0.75,-0.85],[-0.76,-0.88]]),
                              visual.TextStim(self.win, '%s'%maxVal, pos=[0.77,-0.91],color='black',height=0.05),
                              visual.ShapeStim(win,lineWidth=1,lineColor='black',vertices = [[0.75,-0.85],[0.76,-0.88]]),
                              visual.TextStim(self.win, 'Balloon size', pos=[0,-0.94],height=0.05,color='black')]
        
    def initialize(self):
        self.container.border.setAutoDraw(True)
        for i in range(10):
            self.Bins.append(Bin(self.win, self.xp,i,self.container))
            self.Deleters.append(Deleter(self.win, self.xp,i,self.container))
            self.xp += (self.container.width / 10)
        for i in range(len(self.Bins)):
            self.Bins[i].Bin.setAutoDraw(True)
            self.Bins[i].Border.setAutoDraw(True)
            self.Bins[i].Text.setAutoDraw(True)

            self.Deleters[i].Deleter.setAutoDraw(True)
            self.Deleters[i].Text.setAutoDraw(True)
        self.BetCounter.setAutoDraw(True)
        if self.instructions: self.instructions.setAutoDraw(True)
        for s in self.otherstimList:
            s.setAutoDraw(True)
        while 1:
            x, y = self.mouse.getPos()
            for coin in self.Coins:
                coin.Coin.draw()
            if self.clockT.getTime() - self.lastClick > 0.13: allowCoin = True
            else: allowCoin = False
            if sum([b.inBin for b in self.Bins]) < self.maxTotal:
                event.clearEvents()
                for i in range(len(self.Bins)):
                    if (self.Bins[i].inBin < self.maxTotal and allowCoin and self.mouse.getPressed()[0] == 1 and x > self.Bins[i].xPos and x < self.Bins[i].xPos + self.Bins[i].width and y > self.Bins[i].yPos - self.Bins[i].height):
                        self.lastClick = self.clockT.getTime()
                        self.Coins.append(Coin(self.win, self.Bins[i],self.container,self.coinIndexes))
                        self.Bins[i].bottom += self.Bins[i].height / 50
                        self.Bins[i].inBin += 1
                        self.BetCounter.setText('%s Bets' % sum([b.inBin for b in self.Bins]))

            else:
                self.continueButton.draw()                
                if (self.mouse.getPressed()[0] == 1 and x > 0.8 and x < 0.9 and y > -0.05 and y < 0.05) or event.getKeys(['right']):
                    for x in range(len(self.Coins)):
                        self.Coins[x].Coin.setAutoDraw(False)
                    for i in range(len(self.Bins)):
                        self.Bins[i].Bin.setAutoDraw(False)
                        self.Bins[i].Border.setAutoDraw(False)
                        self.Bins[i].Text.setAutoDraw(False)
                        self.Deleters[i].Deleter.setAutoDraw(False)
                        self.Deleters[i].Text.setAutoDraw(False)
                    self.BetCounter.setAutoDraw(False)
                    if self.instructions: self.instructions.setAutoDraw(False)
                    for s in self.otherstimList:
                        s.setAutoDraw(False)
                    self.container.border.setAutoDraw(False)
                    return [b.inBin for b in self.Bins]

            for i in range(len(self.Deleters)):
                if (self.Bins[i].inBin > 0 and allowCoin and self.mouse.getPressed()[0] == 1 and x > self.Deleters[i].xPos and x < self.Deleters[i].xPos + self.Deleters[i].width and y > self.Deleters[i].yPos - self.Deleters[i].height and y < self.Deleters[i].yPos):
                    self.lastClick = self.clockT.getTime()
                    coinsHere = [c for c in self.Coins if c.index == self.Deleters[i].index][-1]
                    self.Coins = [_ for _ in self.Coins if _.coinIndex != coinsHere.coinIndex]
                    self.Bins[i].bottom -= self.Bins[i].height / 50
                    self.Bins[i].inBin -= 1
                    self.BetCounter.setText('%s Bets' % sum([b.inBin for b in self.Bins]))
            self.win.flip()

                
if __name__ == '__main__':
    
    win = visual.Window([600,600], monitor='testMonitor', units='norm',fullscr=False)
    Dist = Distributor(win,64,instructions ='')
    Dist.initialize()