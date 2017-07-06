import pandas as pd
import numpy as np
import os


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


def Questionnaire_link

