import countfreqs, numpy, math, evaltagger
import os
import operator

rf = open('gene.train','r')
wf = open('gene.counts','w')
countfreqs.countNgrams(rf, 3, wf)
rf.close()
wf.close()

classes = ['GENE','NOGENE']
NoClasses = len(classes)
vocabulary = {}
myFile = open('gene.counts','r')

for line in myFile:
    wordList = line.strip().split(' ')
    if (wordList[1] == 'WORDTAG'):
        if wordList[2] == 'GENE':
            if wordList[3] not in vocabulary:
                vec = [int(wordList[0])] + [0, 0, 0]
            else:
                vec = vocabulary[wordList[3]]
                vec[0] = int(wordList[0])
        elif wordList[2] == 'NOGENE':
            if wordList[3] not in vocabulary:
                vec = [0] + [int(wordList[0])] + [0, 0]
            else :
                vec = vocabulary[wordList[3]]
                vec[1] = int(wordList[0])
        vocabulary[wordList[3]] = vec
myFile.close()


# noRare = numpy.sum([vocabulary[item] for item in vocabulary if (sum(vocabulary[item])<5)])
# toDelete = [item for item in vocabulary if (sum(vocabulary[item])<5)]

noRare = [0, 0, 0, 0]
toDelete = []
for item in vocabulary:
    if (sum(vocabulary[item]) < 5) :
        noRare = numpy.sum([noRare, vocabulary[item]], axis=0)
        toDelete.append(item)

vocabulary['_RARE_'] = noRare.tolist()
for k in toDelete:
    del vocabulary[k]

sumVocClass = [0]*NoClasses
for i in range(NoClasses) :
    sumVocClass[i] = sum([vocabulary[item][i] for item in vocabulary])
    for item in vocabulary:
        vocabulary[item][NoClasses + i] = vocabulary[item][i] / sumVocClass[i]

###################    U N I G R A M     T A G G E R   ######################
myFile = open('gene.test','r')
resultFile = open('gene.test.p1.out','w')
for line in myFile:
    word = line.strip()
    if word != '':
        if word in vocabulary:
                vals = vocabulary[word][2:]
                index, value = max(enumerate(vals), key=operator.itemgetter(1))
                resultFile.write("{} {} \n".format(word, classes[index]))
        else:
            vals = vocabulary['_RARE_'][2:]
            index, value = max(enumerate(vals), key=operator.itemgetter(1))
            resultFile.write("{} {}\n".format(word, classes[index]))
    else:
        resultFile.write("{}\n".format(word))
myFile.close()
resultFile.close()

# gs_iterator = evaltagger.corpus_iterator(open('gene.key'))
# pred_iterator = evaltagger.corpus_iterator(open('gene.dev.p1.out'), with_logprob=False)
# evaluator = evaltagger.Evaluator()
# evaluator.compare(gs_iterator, pred_iterator)
# evaluator.print_scores()

# PS C:\> cd C:\Users\andre\Documents\CloudStation\UNIGE\NaturalLanguageProcessing\TP3
# PS C:\Users\andre\Documents\CloudStation\UNIGE\NaturalLanguageProcessing\TP3> python.exe .\evaltagger.py .\gene.key .\gene.dev.p1.out
# Found 2669 GENEs. Expected 642 GENEs; Correct: 424.
#
#         precision       recall          F1-Score
# GENE:   0.158861        0.660436        0.256116



