import os
import math

##################################  E X P E R I M E N T 1 ###################################################            
# Train part

trainpath = 'C:/Users/andre/Documents/CloudStation/UNIGE/NaturalLanguageProcessing/TP2/movie-reviews-en/train'
trainFile = sorted(os.listdir(trainpath))
print(trainFile)
NoClasses = len(trainFile)
NoDocInClass = [0]*NoClasses
vocabulary = {}
# Create vocabulary as a dictionnary where words are key and as values we use an array as follows:
# counts for negative class, counts for positive class, log(cond proba negative class), log(cond proba positive class)
for i in range(NoClasses) :
    currDir = os.listdir(trainpath + '/' + trainFile[i])
    NoDocInClass[i] = len(currDir)
    for j in currDir:
        myFile = open(trainpath + '/' + trainFile[i] + '/' + j,encoding="utf8")
        wordList = []
        for line in myFile:
            wordList = wordList + line.split(' ')
        myFile.close()
        for word in wordList:
            if word in vocabulary:
                vec = vocabulary[word]
            else:
                vec = [1]*(NoClasses + 2)
            vec[i] +=1
            vocabulary[word] = vec
        myFile.close()

                                    
priorClass = [math.log(no/sum(NoDocInClass)) for no in NoDocInClass]
print(priorClass)

# Remove words from the vocabulary that do not appear in both classes 
todelete = []
for i in range(NoClasses) :
    for item in vocabulary:
        if vocabulary[item][i] == 0:
            todelete.append(item)
for k in todelete:
    del vocabulary[k]

# Compute the loglikelihoods of the words
sumVocClass = [0]*NoClasses
for i in range(NoClasses) :
    sumVocClass[i] = sum([vocabulary[item][i] for item in vocabulary])
    for item in vocabulary:
        vocabulary[item][NoClasses+i] = math.log(vocabulary[item][i]/sumVocClass[i])
print('Voc size ' + str(len(vocabulary)))

#####################################################################################            
# Test part

testpath = 'C:/Users/andre/Documents/CloudStation/UNIGE/NaturalLanguageProcessing/TP2/movie-reviews-en/test'
testFile = sorted(os.listdir(testpath))

NoClasses = len(testFile)
NoDocInClass = [0]*NoClasses
testdocs = {}
for i in range(NoClasses) :
    currDir = os.listdir(testpath + '/' + testFile[i])
    NoDocInClass[i] = len(currDir)
    for doc in currDir: # for each review, compute the loglik of each class using the loglik of the words it contains
        loglik = [0]*NoClasses
        vec = [0]*4
        vec[i] = 1 # mark the true class of the doc
        myFile = open(testpath + '/' + testFile[i] + '/' + doc,encoding="utf8")
        wordList = myFile.read().lower().split(' ')
        myFile.close()
        loglik[0] = priorClass[0] + sum([vocabulary[word][NoClasses+0] for word in wordList if word in vocabulary])
        loglik[1] = priorClass[1] + sum([vocabulary[word][NoClasses+1] for word in wordList if word in vocabulary])
        vec[loglik.index(max(loglik))+2] = 1 # mark the predicted class
        testdocs[testFile[i] + '/' + doc] = vec

TNTP = [0]*2
FNFP = [0]*2
for item in sorted(testdocs.keys()):
    if (testdocs[item][1] == 0) & (testdocs[item][3] == 1): # flase positive
            FNFP[1] +=1
    elif (testdocs[item][0] == 0) & (testdocs[item][2] == 1): # false negative
            FNFP[0] +=1  
    else:
        for k in range(NoClasses):
            if (testdocs[item][k] == 1) & (testdocs[item][k+2] == 1):
                TNTP[k] +=1
                
print('true positive rate = recall = ' + str(TNTP[1]/NoDocInClass[1]))
print('true negative rate = specificity = ' + str(TNTP[0]/NoDocInClass[0]))
print('precision = ' + str(TNTP[1]/(TNTP[1] + FNFP[1])))         
print('Accuracy is ' + str(sum(TNTP)/sum(NoDocInClass)))
# The confusion matrix is based on TNTP and FNFP
print('FNFP is ' + str(FNFP))
print('TNTP is ' + str(TNTP))
print(NoDocInClass)
print('No of test docs is ' + str(len(testdocs)))

#############################################


    


