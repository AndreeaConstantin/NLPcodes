import countfreqs, numpy, math, evaltagger, os
import operator, itertools

rf = open('gene.train','r')
wf = open('gene.counts','w')
countfreqs.countNgrams(rf, 3, wf)
rf.close()
wf.close()

extendedTags = ['*', 'GENE', 'NOGENE', 'STOP']
tagSet = ['GENE','NOGENE']

NoClasses = len(tagSet)
emissionParams = {} # key = word, value = list[countsC1, countsC2, emissionC1, emissionC2]
transitionParams = {} # key = tag, value = matrix where line = previous tag, column = anteprevious tag
myFile = open('gene.counts','r')
combKeys = list(itertools.combinations_with_replacement(extendedTags[:-1], 2))
combKeys.append(('NOGENE','GENE'))
print(combKeys)
for line in myFile:
    wordList = line.strip().split(' ')
    if (wordList[1] == 'WORDTAG'): # create emissionParams dictionary
        tags = ['']
        for i in range(len(tagSet)):
            if wordList[2] == tagSet[i]:
                if wordList[3] not in emissionParams:
                    vec = [0]*i + [int(wordList[0])] + [0]*(3-i)
                else:
                    vec = emissionParams[wordList[3]]
                    vec[i] = int(wordList[0])
                emissionParams[wordList[3]] = vec
    else:
        if (wordList[1] == '3-GRAM'): # create transitionParams dictionary for trigrams
            if wordList[4] not in transitionParams:
                val = dict((el,[0,0]) for el in combKeys)
            else:
                val = transitionParams[wordList[4]]
            val[(wordList[2], wordList[3])] = [int(wordList[0]),0]
            transitionParams[wordList[4]] = val
myFile.close()

myFile = open('gene.counts','r')
for line in myFile:
    wordList = line.strip().split(' ')
    if (wordList[1] == '2-GRAM'):
        if (wordList[2]!='STOP') & (wordList[3]!='STOP'):
            for item in transitionParams:
                transitionParams[item][(wordList[2], wordList[3])][1] = transitionParams[item][(wordList[2], wordList[3])][0] / int(wordList[0])
                # val = transitionParams[item]
                # innerVal = val[(wordList[2], wordList[3])]
                # innerVal[1] = innerVal[0]/int(wordList[0])
                # val[(wordList[2], wordList[3])] = innerVal
                # transitionParams[item] = val
myFile.close()

# noRare = numpy.sum([vocabulary[item] for item in vocabulary if (sum(vocabulary[item])<5)])
# toDelete = [item for item in vocabulary if (sum(vocabulary[item])<5)]

noRare = [0, 0, 0, 0]
toDelete = []
for item in emissionParams:
    if (sum(emissionParams[item]) < 5) :
        noRare = numpy.sum([noRare, emissionParams[item]], axis=0)
        toDelete.append(item)

emissionParams['_RARE_'] = noRare.tolist()
for k in toDelete:
    del emissionParams[k]

sumVocClass = [0]*NoClasses
for i in range(NoClasses) :
    sumVocClass[i] = sum([emissionParams[item][i] for item in emissionParams])
    for item in emissionParams:
        emissionParams[item][NoClasses + i] = emissionParams[item][i] / sumVocClass[i]

# ###################    T R I G R A M     H M M    T A G G E R   ######################

myFile = open('gene.test','r')
resultFile = open('gene.test.p2.out','w')
sentence = []
for line in myFile:
    word = line.strip()
    if word != '': # did not reach the end of the current sentence
        sentence.append(word)
    else: # work with the previous sentence
        Viterbi = dict((el, 0) for el in combKeys)  # initiate Viterbi dictionary as a running window of 2 steps
        Viterbi[('*', '*')] = 1
        backP = dict((el, [0] * len(sentence)) for el in combKeys)
        k = 0
        for word in sentence:
            newViterbi = dict((el, 0) for el in combKeys)
            for i in range(len(tagSet)):
                if word in emissionParams:
                    emissionVal = emissionParams[word][i + 2]
                else:
                    emissionVal = emissionParams['_RARE_'][i + 2]
                tag = tagSet[i]
                newBigram = [(x[1], tag) for x in combKeys]
                transKeys = transitionParams[tag]
                newVals = numpy.array([piVals for piVals in Viterbi.values()]) * \
                          numpy.array([transVals[1] for transVals in transKeys.values()]) * \
                          emissionVal

                for item in list(set(newBigram)):
                    indices = [i for i, tupl in enumerate(newBigram) if tupl == item]
                    index, maxValue = max(enumerate(newVals[indices]), key=operator.itemgetter(1))
                    if maxValue != 0:  # save indices(index) as maximum backpointer
                        newViterbi[item] = maxValue
                        backP[item][k] = indices[index] + 1
            Viterbi = newViterbi
            k = k + 1
        transKeys = transitionParams['STOP']
        stopVals = numpy.array([piVals for piVals in Viterbi.values()]) * \
                          numpy.array([transVals[1] for transVals in transKeys.values()])
        stopIndex, maxValue = max(enumerate(stopVals), key=operator.itemgetter(1))
        tagging = [combKeys[stopIndex]]
        for t in reversed(range(k)):
            tagging.append(combKeys[backP[tagging[-1]][t]-1])
        tagSeq = [x[1] for x in reversed(tagging)]
        for t in range(k):
            resultFile.write("{} {} \n".format(sentence[t], tagSeq[t+1]))
        resultFile.write("{}\n".format(''))
        sentence = []
        tagging = []

myFile.close()
resultFile.close()


# PS C:\> cd C:\Users\andre\Documents\CloudStation\UNIGE\NaturalLanguageProcessing\TP3
# PS C:\Users\andre\Documents\CloudStation\UNIGE\NaturalLanguageProcessing\TP3> python.exe .\evaltagger.py .\gene.key .\gene.dev.p2.out
# Found 373 GENEs. Expected 642 GENEs; Correct: 202.
#
#         precision       recall          F1-Score
# GENE:   0.541555        0.314642        0.398030





