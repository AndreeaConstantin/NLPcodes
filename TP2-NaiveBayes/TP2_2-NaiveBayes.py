
import nltk, os, re, string, math
nltk.download('punkt')
nltk.download('stopwords')

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

##################################  E X P E R I M E N T 2 ###################################################   

def tokenizingAndStopwords(str):
    text = ''
    for c in str:
        if c in ['.', '...', '?', '!', ':', ';', '&', ',', '"', '*', '(', ')', '[', ']', '{', '}', '#', '~', '_', '=', '+', '-','/','\\']:
            text += ' ' + c + ' '
        else: text += c

    text = re.sub(' +', ' ',text) # replaces one or more spaces with single space
    text = text.lower().split(' ')
                 
    mf = open('googleStopwords.txt','r') # use Google stopwords
    stopwords = mf.read()
    mf.close()
    stopwords = stopwords.split('\n')
    stopwords = stopwords + ['&', '*', '(', ')', '[', ']', '{', '}', '#', '~', '_', '=', '+', '-', '\'','\n']
    result = []
    for word in text:
        if word not in stopwords:
            result.append(word)
            
    return result


#####################################################################################            
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
        myFile = open(trainpath + '/' + trainFile[i] + '/' + j, encoding="utf8")
        wordList = []
        for line in myFile:
            wordList = wordList + tokenizingAndStopwords(line)  
        myFile.close()
        for word in wordList:
            if word in vocabulary:
                vec = vocabulary[word]
            else:
                vec = [1]*(NoClasses + 2)
            vec[i] +=1
            vocabulary[word] = vec
        myFile.close()

# Compute priors                                    
priorClass = [math.log(no/sum(NoDocInClass)) for no in NoDocInClass]
print(priorClass)

# Compute the loglikelihoods
sumVocClass = [0]*NoClasses
for i in range(NoClasses) :
    sumVocClass[i] = sum([vocabulary[item][i] for item in vocabulary])
    for item in vocabulary:
            vocabulary[item][NoClasses+i] = math.log(vocabulary[item][i]/sumVocClass[i])
            
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
    for doc in currDir: # for each review, compute the sum of loglik for both classes based on the words and their own loglik
        loglik = [0]*NoClasses
        vec = [0]*4
        vec[i] = 1 # mark the true class of the review
        myFile = open(testpath + '/' + testFile[i] + '/' + doc, encoding="utf8")
        wordList = []
        for line in myFile:
            wordList = wordList + tokenizingAndStopwords(line)  
        myFile.close()
        loglik[0] = priorClass[0] + sum([vocabulary[word][NoClasses+0] for word in wordList if word in vocabulary])
        loglik[1] = priorClass[1] + sum([vocabulary[word][NoClasses+1] for word in wordList if word in vocabulary])
        vec[loglik.index(max(loglik))+2] = 1 # mark the predicted class
        testdocs[testFile[i] + '/' + doc] = vec

TNTP = [0]*2
FNFP = [0]*2
for item in sorted(testdocs.keys()):
    if (testdocs[item][1] == 0) & (testdocs[item][3] == 1): # flase positive
            FNFP[1] += 1
    elif (testdocs[item][0] == 0) & (testdocs[item][2] == 1): # false negative
            FNFP[0] += 1
    else:
        for k in range(NoClasses):
            if (testdocs[item][k] == 1) & (testdocs[item][k+2] == 1): # correct prediction
                TNTP[k] += 1

print('true positive rate = recall = ' + str(TNTP[1]/NoDocInClass[1]))
print('true negative rate = specificity = ' + str(TNTP[0]/NoDocInClass[0]))
print('precision = ' + str(TNTP[1]/(TNTP[1] + FNFP[1])))         
print('Accuracy is ' + str(sum(TNTP)/sum(NoDocInClass)))
# The confusion matrix is based on FNFP and TNTP
print('FNFP is ' + str(FNFP))
print('TNTP is ' + str(TNTP))
print(NoDocInClass)
print('No of test docs is ' + str(len(testdocs)))


    


