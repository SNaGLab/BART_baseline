from psychopy import visual, event, core, gui
from GameClasses import Game
from Data_handler import Data_Handler
from socket import *
import os
import shutil
import Instructions
from shutil import move
from Supplementary import orange_white,risk_ambiguity_scale
import webbrowser
from Coin_distributor import Distributor


savePath = os.path.expanduser('~') + '/Desktop/Temp'

# Set up UDP socket for communication with server
gamesock = socket(AF_INET,SOCK_DGRAM)
Mother = ('10.201.193.116',11111) #server's (IP,port)


# Initial display to screen to see if subject is restarting
expInfo = {'Computer':'','Restart?': 'No','ContactID':'','skipIntro':'No','Competitive':"0"}
dlg = gui.DlgFromDict(dictionary=expInfo)
if dlg.OK is False:
    core.quit()

# Experiment Window
window = visual.Window(
                size=[800, 500], monitor='testMonitor',
                color=(0, 0, 0), fullscr=True, screen=0, allowGUI=False)

# Set up data_handler method and game class instance
eventRecorder = Data_Handler(savePath)
eventRecorder.Competitive = expInfo['Competitive']
games = Game(window, savePath, eventRecorder)

if expInfo['Restart?'] != 'No':
    restart = True

else: # dont want to restart (broke during tutorial)
    if expInfo['skipIntro'] == 'No': # do want to skip intro
        if 'Temp' in os.listdir(os.path.expanduser('~') + '/Desktop'):
            shutil.rmtree(savePath)
            print 'here'
        os.mkdir(savePath) # if subject did not restart, make a new temporary savepath dir.
    restart = False

    Instructions.Run_AllIntro(window, savePath,expInfo['skipIntro'],expInfo['Competitive'])
    games.window.flip()
    # Wait for main experiment to begin and tell server ready to play.
    visual.TextStim(win = window, text = 'Please wait while all participants ' +
                    'complete the instructions.\n\nThe game will begin shortly.').draw()
    games.window.flip()
    gamesock.sendto(expInfo['ContactID']+'-'+expInfo['Computer'],Mother)
    gamesock.setblocking(1)
    # When task begins server sends the subject their ID.
    SubjID = gamesock.recvfrom(100)[0]
    eventRecorder.clock.reset()

#___________________________________ LET THE GAMES BEGIN ___________________________________
while 1:
    # Ask for new game
    if restart:
        # tell mother not to count last trial as completed
        MotherPacket = games.drawFixationGetMotherPacket(gamesock,Mother,rStart = True)
        restart = False
        SubjID = MotherPacket['SubjectID'] # grab subject ID from motherpacket
    else:
        MotherPacket = games.drawFixationGetMotherPacket(gamesock,Mother)

    if MotherPacket['Game'] == 'Break': # Take a break and wait for new run to begin
        MotherPacket = games.drawBreak(gamesock)
    elif MotherPacket['Game'] == 'Done': # The experiment is over. Break out of main loop
        break

    # Play game that was assigned by server
    if MotherPacket['Game'] == 'Single Player':
        restart = games.Alone(MotherPacket)
    elif MotherPacket['Game'] == 'MultiPlayer':
        restart = games.Social(MotherPacket)

# ______________________ GAMEPLAY FINISHED, READY FOR QUESTIONNAIRES ______________________
visual.TextStim(win = games.window,
                    text = 'You are now finished with the '+
                    'gameplay portion of this experiment.\n\n'+
                    'You will now complete one more task and an online survey.',
                    color = 'black', wrapWidth = 1.8, pos = [0,0.75]
                    ).draw()

visual.TextStim(win = games.window,
                    text = 'Press the right key to continue.',
                    color = 'black', wrapWidth = 1.8, pos = [0,-0.9]
                    ).draw()
# if subject forgets ID, save it as well
games.window.flip()
event.waitKeys('space')
with open(savePath+'/SubjectID.csv',mode = 'w') as MyFile:
    MyFile.write('%s\n'%SubjID)


# Have subject select color for Risk/Amb gamble
orange_white(games.window,savePath)
instruction = visual.ImageStim(win = games.window)

def RamDisp(im):
    '''
    Displays instruction slide and waits for keypress to move on
    '''
    instruction.setImage(os.getcwd() + '/Resources/RiskAmb_Instructs/' + im)
    instruction.draw()
    games.window.flip()
    event.waitKeys('right')
    return os.getcwd() + '/Resources/RiskAmb_Instructs/' + im

# Complete Risk ambiguity questionnaires
RamDisp('Slide1.jpg')
if int(SubjID) %2 == 0:
    im = RamDisp('Slide2.jpg')
    risk_ambiguity_scale(games.window,'Risk',savePath,im)
    im = RamDisp('Slide3.jpg')
    risk_ambiguity_scale(games.window,'Ambiguity',savePath,im)
else:
    im = RamDisp('Slide3.jpg')
    risk_ambiguity_scale(games.window,'Ambiguity',savePath,im)
    im = RamDisp('Slide2.jpg')
    risk_ambiguity_scale(games.window,'Risk',savePath,im)

visual.TextStim(win = games.window,
                    text = 'You will now be redirected to the online survey.\n\n' +
                    'Please press space to begin the survey.',
                    color = 'black', wrapWidth = 1.8, pos = [0,0]
                    ).draw()
games.window.flip()
event.waitKeys('space')

# Move all data to server computer and inform server that subject data is moved
# Redirect to Qualtrics online Questionnaire
games.window.close()
webbrowser.open('https://cuboulder.qualtrics.com/jfe/form/SV_0UQNbiww2J0IgId', new=1)
move(savePath , os.getcwd() + '/Data/' + str(SubjID))
gamesock.sendto('FIN',Mother)
