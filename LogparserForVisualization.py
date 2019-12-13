import random
import json
from tqdm import tqdm
PARAM='#PARAM'
# 数据结构区
# ------------------------------------------------------------------------
'''
res{
    'group':{
        'template':{
            'count':count,
            'paramList':[{paramDict}]
        }
    }
}
subGroup{
    'dis':{
        'pos':{
            'paramValue1':count,
            'paramValue2':count
        }
    }
}

logDict{
    'dis':[log]
}

paramDict{
    'pos':{
        'paramValue1':count,
        'paramValue2':count
    }
}
'''
# ------------------------------------------------------------------------
# 公共函数区
# ------------------------------------------------------------------------
def mergeLogToParamdict(log,paramDict):
    if not paramDict:
        for i in range(len(log)):
            if log[i] in paramDict[i].keys():
                paramDict[i][log[i]]+=1
            else:
                paramDict[i][log[i]]=1
    else:
        for i in range(len(log)):
            paramDict[i]={log[i]:1}
    return paramDict

def countVecDis(vec1,vec2):
    dis=""
    #优化可以用字节表示一位
    for i in range(len(vec1)):
        if vec1[i]==vec2[i]:
            dis+='0'
        else:
            dis+='1'
    return dis

def divideGroupByDis(stdLog,group):
    subGroup,logDict={},{}
    for log in group:
        dis=countVecDis(stdLog,log)
        if dis not in subGroup.keys():
            logDict[dis]=[log]
            subGroup[dis]=mergeLogToParamdict(log,{})
        else:
            logDict[dis].append(log)
            subGroup[dis]=mergeLogToParamdict(log,subGroup[dis])
    return subGroup,logDict

# ------------------------------------------------------------------------
# Logparser类
# ------------------------------------------------------------------------
class Logparser:
    def __init__(self,filePath):
        self.filePath=filePath
        self.filePath=filePath
        self.hashDict={}
        self.hashGroup={}
        self.data=[]

    def readFile(self,maxCount=200000):
        file=open(self.filePath,'r')
        count=0
        line=file.readline()
        while line:
            count+=1
            if count>maxCount:
                break
            temp=line[:-1].split(" ")
            self.data.append(temp)
            line=file.readline()
        file.close()

    def groupingAndHashing(self):
        self.hashDict[hash(PARAM)]=PARAM
        for log in self.data:
            logVec=[]
            for word in log:
                hashValue=hash(word)
                if hashValue not in self.hashDict.keys():
                    self.hashDict[hashValue]=word
                logVec.append(hashValue)
            temLen=len(logVec)
            if temLen not in self.hashGroup.keys():
                self.hashGroup[temLen]=[logVec]
            else:
                self.hashGroup[temLen].append(logVec)

    def antiHash(self,log):
        res=""
        for word in log:
            res+=self.hashDict[word]+' '
        return res

    def clustering(self,minThreshold=3,thresholdRate=0.3):
        res={}
        for group in self.hashGroup.values():
                pbar=tqdm(total=len(group))
                threshold=min(len(group[0])*thresholdRate,minThreshold)
                while len(group)>0:
                    # 三个结构见数据结构区
                    subGroup,logDict,paramDict={},{},{}
                    # 随机选一条log
                    stdLogIdx=random.randint(0,len(group)-1)
                    stdLog=group[stdLogIdx]
                    paramDict=mergeLogToParamdict(stdLog,paramDict)
                    group.remove(stdLog)
                    # 获取subGroup logDict
                    subGroup,logDict=divideGroupByDis(stdLog,group)
                    # 按距离从近到远排序
                    sortedSubgroupKeys=sorted(subgroup.keys(),key=lambda d:d.count('1'))
