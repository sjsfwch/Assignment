
import time
# 暂时先用纯字母做个测试，哈希查找比如a就是在第0个桶，aa在第27*1+1*1-1=27个桶
# indexList:[
#     "Si":[
#         Ti:count,
#     ],
# ]
class fuzzyMap:
    def __init__(self,dataset,q):
        self.dataset=dataset
        self.q=q
        self.indexList=[{} for i in range(pow(27,self.q))]
        self.database={}
        self.tokenization()
    
    def tokenization(self):
        for word in self.dataset:
            if word not in self.database.keys(): 
                self.qgramTokenizing(word)

    def qgramTokenizing(self,word):
        index=0
        ascBase=ord('a')-1
        # 第一个
        for i in range(self.q):
            index*=27
            index+=ord(word[i])-ascBase
        self.indexList[index-1][word]=1
        # 滑动窗口法
        for i in range(self.q,len(word)):
            # 减去原来的高位
            # print("start!!!!!")
            index-=(ord(word[i-self.q])-ascBase)*pow(27,self.q-1)
            # print(index)
            # 进一位
            index*=27
            # print(index)
            # 加上新滑进窗口的
            index+=ord(word[i])-ascBase
            # print(index)
            if word not in self.indexList[index-1].keys():
                self.indexList[index-1][word]=1
            else:
                self.indexList[index-1][word]+=1
        self.database[word]=len(word)

    def search(self,s,threshold=1,count=10):
        # 先计算s的qgram值
        sQgramDict={}
        index=0
        ascBase=ord('a')-1
        for i in range(self.q):
            index*=27
            index+=ord(s[i])-ascBase
        sQgramDict[index-1]=1
        for i in range(self.q,len(s)):
            index-=(ord(s[i-self.q])-ascBase)*pow(27,self.q-1)
            index*=27
            index+=ord(s[i])-ascBase
            if index-1 not in sQgramDict.keys():
                sQgramDict[index-1]=1
            else:
                sQgramDict[index-1]+=1

        qgramThreshold=2*threshold*self.q
        wordSet=[]
        for key in self.database.keys():
            wordSet.append((key,0))
        for key in sQgramDict.keys():
            # print(key)
            newWordSet=[]
            for word in wordSet:
                # print(word)
                # 长度超过，直接pass
                if abs(len(word[0])-len(s))>threshold:
                    continue
                # qgram距离超过qgram阈值，直接pass
                if word[0] not in self.indexList[key]:
                    qgramWord=0
                else:
                    qgramWord=self.indexList[key][word[0]]
                qgramDis=word[1]+abs(sQgramDict[key]-qgramWord)
                if qgramDis>qgramThreshold:
                    continue
                else:
                    newWordSet.append((word[0],qgramDis))
            wordSet=newWordSet
        # print(wordSet)
        # 到目前为止，wordSet里的word只是满足在计算s的所有qgram下不超过阈值，但不能保证计算全部qgramlist不超过阈值，还需进行qgram验算
        self.check(s,wordSet,qgramThreshold,count,sQgramDict)

    def check(self,s,wordSet,qgramThreshold,count,sQgramDict):
        wordSetQgramSet=set()
        newWordSet,result=[],[]
        for key in sQgramDict.keys():
            wordSetQgramSet.add(key)
        ascBase=ord('a')-1
        for wordTurple in wordSet:
            flag=True
            index=0
            # 存储仅在word里面出现的哈希值
            tempSet=set()
            qgramValue=wordTurple[1]
            word=wordTurple[0]
            # print(word)
            for i in range(self.q):
                index*=27
                index+=ord(word[i])-ascBase
            # 刚刚没计算过的，计算
            if index-1 not in wordSetQgramSet:
                qgramValue+=self.indexList[index-1][word]
                # print("qgramValue is 1",qgramValue)
                tempSet.add(index-1)
                # 超过阈值，直接pass
                if qgramValue>qgramThreshold:
                    flag=False
                    continue
            for i in range(self.q,len(word)):
                index-=(ord(word[i-self.q])-ascBase)*pow(27,self.q-1)
                index*=27
                index+=ord(word[i])-ascBase
                if index-1 not in wordSetQgramSet and index-1 not in tempSet:
                    # print(index-1)
                    qgramValue+=self.indexList[index-1][word]
                    # print("qgramValue is 2",qgramValue)
                    tempSet.add(index-1)
                    if qgramValue>qgramThreshold:
                        flag=False
                        break
            if flag:
                newWordSet.append(word)
        threshold=int(qgramThreshold/2/self.q)
        # print('threshold is',threshold)
        for word in newWordSet:
            editDis=self.editDistance(word,s)
            # print("editDis is",editDis)
            if editDis<=threshold:
                result.append(word)
        print(result)

    def editDistance(self,t,s):
        edit=[[0 for j in range(len(s)+1)] for i in range(len(t)+1)]
        for i in range(len(t)+1):
            edit[i][0]=i
        for j in range(len(s)+1):
            edit[0][j]=j
        flag=0
        for i in range(1,len(t)+1):
            for j in range(1,len(s)+1):
                if t[i-1]==s[j-1]:
                    flag=0
                else:
                    flag=1
                edit[i][j]=min(edit[i-1][j]+1,edit[i][j-1]+1,edit[i-1][j-1]+flag)
        # print(t,s,edit[len(t)][len(s)])
        return edit[len(t)][len(s)]

    def checkCorrection(self,s,threshold=1):
        result=[]
        for word in self.dataset:
            dis=self.editDistance(word,s)
            if dis<=threshold:
                result.append(word)
        print(result)

if __name__=="__main__":
    dataset=[]
    with open("data/wordlist.txt",'r') as f:
        line=f.readline()
        while line:
            dataset.append(line.strip('\n'))
            line=f.readline()
    searcher=fuzzyMap(dataset,2)
    startTime=time.time()
    searcher.search('aa')
    endTime=time.time()
    ("cost time is",endTime-startTime)
    searcher.checkCorrection('aa',1)
    endTime2=time.time()
    print("cost time is",endTime2-endTime)