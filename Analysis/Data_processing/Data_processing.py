import pandas as pd
import numpy as np
import os
from datetime import datetime
# from simplecrypt import encrypt, decrypt
from StringIO import StringIO

"""
BART_Baseline data processing functions
Jacob M. Parelman (jmparelman@gmail.com)
"""

def DS_cleaner(FilePath):
    ''' Removes .DS_Store file from list of directory
        and reindexes when using os.listdir()
        '''
    Files = os.listdir(FilePath)
    popper = []
    for F in Files:
        if F[0] == '.':
            popper.append(Files.index(F))
    for I in reversed(popper):
        Files.pop(I)
    return Files


def makeSessionFrame(paymentDir):
    """
    makes dataframes of subject information for linking questionnaire
    Args:
        paymentDir: payment and linker file directory

    Returns: Sessions = dataframe with first row of session frame as examplar of session time
             allData = concatenated Session frames

    """
    files = DS_cleaner(paymentDir)
    Sessions = pd.DataFrame(np.nan, index=range(len([_ for _ in files if "copy" in _])), columns=['Session','Time'])
    i = 0
    for f in files:
        if "IP" in f:
            session = pd.read_csv(paymentDir + f)
            Sessions.loc[i] = session.loc[0]['Session'],datetime.strptime(session.loc[0]['Time'],"%Y-%m-%d %H:%M:%S")
            i += 1
            try:
                allData = pd.concat([allData,session])
            except:
                allData = session

    Sessions = Sessions.reset_index()
    return Sessions, allData


def determineSession(Qdata,paymentDir):
    """
    Links questionnaire data to subject IDs
    Args:
        Qdata: Questionnaire dataframe from Qualtrics
        paymentDir: directory to pass to makeSessionFrame()

    Returns: Questionnaire with subject ID column

    """
    Sessions, allData = makeSessionFrame(paymentDir)

    Qdat = Qdata.loc[2:]  # top two rows of qualtrics data are nonsense
    Qdat = Qdat.reset_index()

    Qdat['SubjectID'] = 0  # empty row for subject IDs
    for ix in Qdat.index:
        #  get startDate for subject questionnaire and make into datetime
        date = Qdat.loc[ix]['StartDate']
        strp = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

        IP = Qdat.loc[ix]['IPAddress']  # get subject's external IP

        #  find session that has the smallest timedelta (find the session subject was most likely in)
        diffs = [np.abs(x - strp) for x in Sessions.Time]
        session = Sessions.loc[diffs.index(min(diffs))]['Session']

        Qdat.loc[ix,('SubjectID')] = int(allData[(allData.Session == session) & (allData.IP == IP)]['SubjectID'])
    return Qdat


def decryptAllCombine(paymentDir,password):
    """
    combines all linker files and encrypts for security
    Args:
        paymentDir: directory to linkers
        password: password for linker files

    Returns: combined and encrypted linker file

    """
    for F in DS_cleaner(paymentDir):
        if "Linker" in F:

            #  read amd decrypt linker files
            filepath = os.path.join(paymentDir,F)
            File = open(filepath, 'r')
            Text = File.read()
            File.close()
            text = decrypt(password,Text)

            # concat all linkers
            try:
                NewFrame = pd.concat([NewFrame,pd.read_csv(StringIO(text),sep=',')])
            except:
                NewFrame = pd.read_csv(StringIO(text),sep=',')

    # encrypt and save concatenated lnkers
    Alltext = encrypt(password, NewFrame.to_string())
    File = open(os.path.join(paymentDir,'allLinks.csv'), 'w')
    File.write(Alltext)
    File.close()


def combinePayments(paymentDir):
    for F in DS_cleaner(paymentDir):
        if 'subjectPayment' in F:
            S = F.split('_')[1][:-4]
            df = pd.read_csv(os.path.join(paymentDir,F))
            df['Session'] = S
            try:
                NewFrame = pd.concat([NewFrame,df])
            except:
                NewFrame = df
    return NewFrame

def RatingCombine(dir):
    """
    adds the maxrating as a column to distributions for each subject
    Args:
        dir: directory containing subject directories

    Returns: None (places updated dists file in each subject directory)

    """
    for Subj in DS_cleaner(dir):
        # read in data
        MaxRating = pd.read_csv(os.path.join(dir,Subj,'MaxRatings.csv'),header = None)
        dists = pd.read_csv(os.path.join(dir,Subj,'DistRatings.csv'))
        MaxRating.columns = ['Run','Rating']

        # make max ratings long enough for distributions
        maxList = []
        for R in MaxRating.Rating[:-1]:
            for i in range(2):
                maxList.append(R)
        maxList.append(list(MaxRating.Rating)[-1])

        # export updated distribution file
        dists['Max'] = maxList
        dists['SubjID'] = Subj
        dists.to_csv(os.path.join(dir,Subj,'dists_with_max.csv'))


def formatTutorial(data,subjID):
    """
    converts variables to be consistent with main task data
    Args:
        data: pandas dataframe of tutorial data

    Returns: updates pandas dataframe

    """

    for t in pd.unique(data.Trial):
        trial = data[data.Trial == t]
        if 1 in list(trial.P2_Pump):
            trial.Game = 1
        else:
            trial.Game = 0
        try:
            DataOut = pd.concat([DataOut,trial])
        except:
            DataOut = trial
    DataOut.SubjectID = subjID

    for d in pd.unique(DataOut.Trial):
        dt = DataOut[DataOut.Trial == d]
        dt = dt.reset_index()
        if np.sum(list(dt.Pop)) > 1:
            ix = dt.index[dt.OutcomeScreen == 1][0]

            dt = dt.loc[:ix]
        try:
            Final = pd.concat([Final,dt])
        except:
            Final = dt
    return Final

def appendTutorial(dir):
    """
    appends tutorial to the beginning of subjects data
    Args:
        dir: subject folder directory

    Returns: None (places combined data in subject directory)

    """
    for Subj in DS_cleaner(dir):
        #  get tutorial and experiment data
        Tutorial = formatTutorial(pd.read_csv(os.path.join(dir,Subj,'Data_Tutorial.csv')),Subj)
        Data = pd.read_csv(os.path.join(dir,Subj,'Data_%s.csv'%float(Subj)))

        #  change trials in experiment data
        maxTutorialTrial = max(Tutorial.Trial)
        Data['Trial'] = Data['Trial'].apply(lambda x: x + maxTutorialTrial)
        combined = pd.concat([Tutorial,Data])
        combined = combined[combined.Trial != max(combined.Trial)]
        #  export to subject directory
        combined.to_csv(os.path.join(dir,Subj,'combined_%s.csv'%float(Subj)))


def fixfixations(data):
    startTrial = min(data.Trial) - 1
    Trials = []
    for t in list(data.Fixation):
        if t == 1:
            startTrial += 1
        Trials.append(startTrial)
    return Trials




def SummarizeTrial(Trial):
    """
    creates a row for every trial with summary information
    Args:
        data: subject pandas dataframe

    Returns: row

    """

    Trial = Trial.reset_index()
    InitialRow = Trial.loc[0]
    TrialDict = {}
    TrialDict['SubjectID'] = InitialRow['SubjectID']
    TrialDict['Competitive'] = InitialRow['Competitive']
    TrialDict['Run'] = InitialRow['Run']
    TrialDict['Game'] = InitialRow['Game']
    TrialDict['Trial'] = InitialRow['Trial']
    TrialDict['maxP1_Tokens'] = max(Trial.Tokens)

    if 1 in list(Trial.Cash):
        TrialDict['P1_endState'] = 1
        TrialDict['p1_endTime'] = float(Trial[Trial.Cash == 1].TimeOnset)
    elif 1 in list(Trial.Pop):
        TrialDict['P1_endState'] = 0
        TrialDict['p1_endTime'] = float(Trial[Trial.Pop == 1].TimeOnset)
    elif 1 in list(Trial.P1_TimedOut):
        print 'Timed out on trial %s, P2 was %s'%(TrialDict['Trial'],InitialRow['P2_SubjectID'])
        TrialDict['P1_endState'] = 2
        TrialDict['p1_endTime'] = float(Trial[Trial.P1_TimedOut == 1].TimeOnset)

    if InitialRow['Game'] == 1:
        TrialDict['maxP2_Tokens'] = max(Trial.P2_Tokens)
        if 1 in list(Trial.P2_Cash):
            TrialDict['P2_endState'] = 1
            TrialDict['p2_endTime'] = float(Trial[Trial.P2_Cash == 1].TimeOnset)
        elif 1 in list(Trial.P2_Pop):
            TrialDict['P2_endState'] = 0
            TrialDict['p2_endTime'] = float(Trial[Trial.P2_Pop == 1].TimeOnset)
        elif 1 in list(Trial.P2_TimedOut):
            TrialDict['P2_endState'] = 2
            TrialDict['p2_endTime'] = float(Trial[Trial.P2_TimedOut == 1].TimeOnset)

        if TrialDict['p1_endTime'] < TrialDict['p2_endTime']:
            TrialDict['P1First'] = 1
        elif TrialDict['p1_endTime'] > TrialDict['p2_endTime']:
            TrialDict['P1First'] = 0

    else:
        TrialDict['maxP2_Tokens'] = None
        TrialDict['P2_endState'] = None
        TrialDict['p2_endTime'] = None
        TrialDict['P1First'] = None


    TrialDict['Duration'] = float(Trial[Trial.OutcomeScreen == 1].TimeOnset) - float(
        Trial[Trial.StartPlay == 1].TimeOnset)

    series = pd.Series(TrialDict)
    return series

def removeRestarts(data):
    pretrials = len(pd.unique(data.Trial))
    data.Trial = fixfixations(data)
    removeList = []
    for t in pd.unique(data.Trial):
        if 1 in list(data[data.Trial == t].Restart):
            removeList.append(t)
    data = data[~data.Trial.isin(removeList)]
    data.Trial = fixfixations(data)
    return data


def performSummarize(dir):
    appendTutorial(dir)
    for sub in DS_cleaner(dir):
        print sub
        data = pd.read_csv(os.path.join(dir,sub,'combined_%s.csv'%float(sub)))
        data = removeRestarts(data)
        data = data[data.Trial != max(data.Trial)]
        summarized = data.groupby(['Trial']).apply(SummarizeTrial)
        summarized.to_csv(os.path.join(dir,sub,'summarized_data_combined_%s.csv'%sub))


if __name__ == '__main__':
    performSummarize('/Users/JMP/Documents/S_BART/BART_baseline/Data')


