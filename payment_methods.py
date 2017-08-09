import os
import pandas as pd
import numpy as np
import pickle

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


class Subject():
    def __init__(self, subpath):
        self.filepath = subpath
        self.subjectTrial = {}

    def _select_trial(self):
        """Select a random trial from the subjects dataframe."""

        # subset trial data
        indata = pd.read_csv(os.path.join(self.filepath, DS_cleaner(self.filepath)[0]))
        data = indata[indata.Game != 3] # remove break trials from dataframe
        subjID = int(float(self.filepath.split('/')[-1]))

        # random trial selection do-while loop
        selectedTrial = np.random.choice(pd.unique(data.Trial))
        trial_dataFrame = data[(data.SubjectID == subjID) & (data.Trial == selectedTrial)].reset_index()
        while 1:
            try:
                selectedTrial = np.random.choice(pd.unique(data.Trial))
                trial_dataFrame = data[(data.SubjectID == subjID) & (data.Trial == selectedTrial)].reset_index()
                trial_firstRow = trial_dataFrame.loc[1]
                break
            except:
                pass

        # store static info
        self.subjectTrial['SubjectID'] = subjID
        self.subjectTrial['Trial'] = selectedTrial
        self.subjectTrial['Run'] = trial_firstRow.Run
        self.subjectTrial['P2'] = trial_firstRow.P2_SubjectID
        self.subjectTrial['Game'] = trial_firstRow.Game
        self.subjectTrial['Competitive'] = trial_firstRow.Competitive

        # store p1 information
        self.subjectTrial['P1_max'] = max(trial_dataFrame.Tokens)
        if 1 in list(trial_dataFrame.Cash):
            self.subjectTrial['P1_end'] = 'Cash'
            self.subjectTrial['P1_endTime'] = float(list(trial_dataFrame[trial_dataFrame.Cash == 1].TimeOnset)[0])
        if 1 in list(trial_dataFrame.Pop):
            self.subjectTrial['P1_end'] = 'Pop'
            self.subjectTrial['P1_endTime'] = float(list(trial_dataFrame[trial_dataFrame.Pop == 1].TimeOnset)[0])
        if 1 in list(trial_dataFrame.P1_TimedOut):
            self.subjectTrial['P1_end'] = 'timed'
            self.subjectTrial['P1_endTime'] = float(list(trial_dataFrame[trial_dataFrame.P1_TimedOut == 1].TimeOnset)[0])

        # store p2 information
        self.subjectTrial['P2_max'] = max(trial_dataFrame.P2_Tokens)
        if 1 in list(trial_dataFrame.P2_Cash):
            self.subjectTrial['P2_end'] = 'Cash'
            self.subjectTrial['P2_endTime'] = float(list(trial_dataFrame[trial_dataFrame.P2_Cash == 1].TimeOnset)[0])
        elif 1 in list(trial_dataFrame.P2_Pop):
            self.subjectTrial['P2_end'] = 'Pop'
            self.subjectTrial['P2_endTime'] = float(list(trial_dataFrame[trial_dataFrame.P2_Pop == 1].TimeOnset)[0])
        elif 1 in list(trial_dataFrame.P2_TimedOut):
            self.subjectTrial['P2_end'] = 'timed'
            self.subjectTrial['P2_endTime'] = float(list(trial_dataFrame[trial_dataFrame.P2_TimedOut == 1].TimeOnset)[0])
        else:
            self.subjectTrial['P2_end'] = None
            self.subjectTrial['P2_endTime'] = 0

        # duration of trial
        self.subjectTrial['Duration'] = float(list(trial_dataFrame[trial_dataFrame.OutcomeScreen == 1].TimeOnset)[0]) - float(
            list(trial_dataFrame[trial_dataFrame.StartPlay == 1].TimeOnset)[0])

        # determine who ended first
        if self.subjectTrial['P1_endTime'] < self.subjectTrial['P2_endTime']:
            self.subjectTrial['P1_endedFirst'] = True
        elif self.subjectTrial['P1_endTime'] > self.subjectTrial['P2_endTime']:
            self.subjectTrial['P1_endedFirst'] = False

        # get tokens for trial
        if self.subjectTrial['P1_end'] == 'Cash':
            if self.subjectTrial['Game'] == 0:
                self.subjectTrial['TrialEndow'] = self.subjectTrial['P1_max']
            else:
                if self.subjectTrial['Competitive'] == 1:
                    if self.subjectTrial['P1_max'] > self.subjectTrial['P2_max']:
                        self.subjectTrial['TrialEndow'] = self.subjectTrial['P1_max']
                    else:
                        self.subjectTrial['TrialEndow'] = 0
                else:
                    self.subjectTrial['TrialEndow'] = self.subjectTrial['P1_max']
        else:
            self.subjectTrial['TrialEndow'] = 0

        self.subjectTrial['TrialEndow'] = str(self.subjectTrial['TrialEndow']) + '| $' + str(self.subjectTrial['TrialEndow'] * .2)

        self.subjectTrial = pd.Series(self.subjectTrial)



    def ratings(self,otherAvg):
        """Creates payment for various distributions and ratings during task"""

        # get average ratings for everyone else
        allratings = otherAvg

        # load in rating dataframes
        dist_data = pd.read_csv(os.path.join(self.filepath, 'DistRatings.csv'))
        dist_data = dist_data.reset_index()

        maxRatings = pd.read_csv(os.path.join(self.filepath, 'MaxRatings.csv'),header = None)
        maxRatings.columns =['run','max']
        Max = maxRatings.loc[0]['max']


        # subset specific ratings
        popsRatings = dist_data.loc[0]

        PopChoice = int(np.random.uniform(5,65))  # random pop point generated for payment draw

        # calculate percentage of distributed ratings in correct scaled bin
        if PopChoice > Max:
            PopCorrectBar = 0
        else:
            scaledPop = int(10 * round(((float(PopChoice)/float(Max))*100)/10))
            if scaledPop == 0:
                scaledPop = 10
            PopCorrectBar = popsRatings[str(scaledPop)]  # places pop point within distirbution
        # calculate bonus
        popSum = np.sum(list(popsRatings)[1:-3])
        popPercentCorrect = float(PopCorrectBar)/float(popSum)
        popPercentIncorrect = float(popSum - PopCorrectBar) / float(popSum)
        self.subjectTrial['popEndow'] = int(20 - (10*(1-popPercentCorrect)**2) - (10*(popPercentIncorrect)**2))
        self.subjectTrial['popEndow'] = str(PopCorrectBar) + '| $' + str(self.subjectTrial['popEndow'] * .2)

        # find a run rating to pay for rating accuracy
        while 1:
            # in small percentage of sesssions, a subject misses a rating. If this is the case, keep trying
            # until a viable run is selected
            try:
                othersRatings = dist_data.loc[np.random.randint(0,len(dist_data)) + 1]
                break
            except:
                pass

        # determine payment for social rating
        otherAvg = allratings
        if otherAvg > Max:
            OtherCorrectBar = 0
        else:
            print otherAvg
            if otherAvg < 1:
                OtherCorrectBar = 0
            else:
                scaledOther = int(10 * round(((float(otherAvg)/float(Max))*100)/10))
                if scaledOther == 0:
                    scaledOther = 10
                OtherCorrectBar = othersRatings[str(scaledOther)]
            
        otherSum = np.sum(list(othersRatings)[1:-2])
        otherPercentCorrect = float(OtherCorrectBar) / float(otherSum)
        otherPercentIncorrect = float(otherSum - OtherCorrectBar) / float(otherSum)
        self.subjectTrial['othersEndow'] = int(20 - (10 * (1 - otherPercentCorrect) ** 2) - (10 * (otherPercentIncorrect) ** 2))
        self.subjectTrial['othersEndow'] = str(OtherCorrectBar) + '| $' + str(self.subjectTrial['othersEndow'] * .2)


    def riskAmb(self):
        """ Calculates row for possible payment from risk ambiguity questionnaire"""

        self.subjectTrial['color'] = pickle.load(open(os.path.join(self.filepath, 'OtherInfo.p'),'r'))['Color']
        riskamb = pd.read_csv(os.path.join(self.filepath, 'RiskAmb.csv'),header=None)
        riskamb.columns = ['type','ix','value','choice']
        row = riskamb.loc[np.random.choice(len(riskamb))]
        self.subjectTrial['riskAmb'] = row['type']
        self.subjectTrial['RAvalue'] = row['value']
        self.subjectTrial['RAchoice'] = row['choice']

    def getAll(self,avgs):
        """ Run protocol """

        self._select_trial()
        self.ratings(avgs)
        self.riskAmb()

def allSubAvgs(path,sess):
    """ Calculate the average Adj. pumps for all subjects"""

    subvals = []    # for all subjects
    for i in DS_cleaner(path):
        subpath = os.path.join(path, i)
        data = pd.read_csv(os.path.join(subpath, DS_cleaner(subpath)[0]))
        print data.loc[0]
        if data.loc[0,'Session'] == sess:
            subvals.append(np.mean(list(data.Tokens)))
    return np.mean(subvals)

def GetAllSubs(path,sess):

    allAvgs = allSubAvgs(path,sess)  # get the averages for every subjects cash in points
    for i in DS_cleaner(path):  # for every subject grab a trial, distribution ratings, and risk ambiguity
        # only select subjects from current session
        subpath = os.path.join(path, i)
        tempSub = pd.read_csv(os.path.join(subpath, DS_cleaner(subpath)[0]))
        if int(tempSub.loc[0,'Session']) == int(sess):
            sub = Subject(subpath)
            sub.getAll(allAvgs)

            # add subject to subject dataframe
            try:
                subframe.loc[sub.subjectTrial['SubjectID']] = sub.subjectTrial
            except:
                subframe = pd.DataFrame(columns=sub.subjectTrial.keys())
                subframe.loc[sub.subjectTrial['SubjectID']] = sub.subjectTrial

    # give added bonus for other participants' behavior
    subframe['fromOther'] = 0
    for i in subframe.index:
        p2frame = subframe[subframe.P2 == i].reset_index()  # if multiplayer selected for other
        if len(p2frame) > 0:
            if p2frame.loc[0]['P2_end'] == 'Cash':
                subframe.loc[i, 'fromOther'] += p2frame.loc[0]['P2_max']

    for i in subframe.index:
        subframe.loc[i, 'fromOther'] = str(subframe.loc[i, 'fromOther']) + '| $'+ str(subframe.loc[i, 'fromOther'] * .2)

    return subframe

if __name__ == '__main__':
    path = '/Users/JMP/Documents/S_BART/S_BART.0.3/Data'
    GetAllSubs(path,64).to_csv('/users/JMP/Desktop/hi.csv')