import json, itertools, operator
from operator import itemgetter

myFile = open('toygrammar.json','r')
grammar = json.load(myFile)
myFile.close()

phrase = 'the girl sees the telescope'
wordList = phrase.strip().split(' ')
matCKY = [[0 for i in range(len(wordList))] for j in range(len(wordList))]
for i in range(len(wordList)):
    for item in grammar['TR']:
        if wordList[i] == item[1]:
            matCKY[-1][i] = {tuple(item[0:2]): item[2]}

k = 1
backP = [[0 for i in range(len(wordList))] for j in range(len(wordList))] ## for backpointers
for i in reversed(range(len(wordList)-k)):
    for j in range(i+1):
        vals = []
        usedRules = []
        source = []
        ourRange = range(i+1,len(wordList))
        for s in range(len(ourRange)):
            n = list(reversed(ourRange))[s]
            m = list(ourRange)[s]
            # consider all rules coming from possibly multiple entries in the cell
            searchFor = list(itertools.product(list(map(itemgetter(0),list(matCKY[m][j].keys()))),
                                               list(map(itemgetter(0),(list(matCKY[n][n-(i-j)].keys()))))))
            for el in searchFor:
                for item in grammar['NTR']:
                    if list(el) == item[1:3]:
                        proba = item[3]*list(matCKY[m][j].values())[0]*list(matCKY[n][n-(i-j)].values())[0]
                        if item[0] not in list(map(itemgetter(0),usedRules)) or \
                                (item[0] in list(map(itemgetter(0),usedRules)) and
                                 proba > vals[list(map(itemgetter(0),usedRules)).index(proba)]):
                            vals.append(proba)
                            usedRules.append(item[0:3])
                            source.append([[m,j],[n,n-(i-j)]])
            print(str(m + 1) + 'and' + str(j + 1) + '&&' + str(n+1) + 'and' + str(n-(i-j)+1))
            backP[i][j] = source
            matCKY[i][j] = dict((tuple(usedRules[i]), vals[i]) for i in range(len(vals)))
    k = k + 1


## Get the tree using the backpointers
index, maxValue = max(enumerate(matCKY[0][0].values()), key=operator.itemgetter(1)) # choose the parse tree with highest probability
tree = []
for i in reversed(range(len(wordList))):
    for j in range(i+1):
        if backP[i][j] != 0 and backP[i][j] != []:
            lookFor = backP[i][j][index]
            for k in range(len(lookFor)):
                tree.append('(' + ' '.join(list(list(matCKY[lookFor[k][0]][lookFor[k][1]].keys())[index])) + ') ')
tree.append('(' + ' '.join(list(list(matCKY[0][0].keys())[index])) + ') ')
print('probability is ' + str(maxValue))
print('tree is ' + str(''.join(tree)))