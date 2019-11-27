import random
import json
PARAM='#PARAM'

def countVecDis(vec1,vec2):
    dis=""
#     优化可以用字节表示一位
    for i in range(len(vec1)):
        if vec1[i]==vec2[i]:
            dis+='0'
        else:
            dis+='1'
    return dis

def mergeByDis(stdLog,dis):
    res=[]
    for i in range(len(stdLog)):
        if dis[i]=='1':
            res.append(hash(PARAM))
        else:
            res.append(stdLog[i])
    return res

def mergeSet(set1,set2):
    res=[]
    for i in range(len(set1)):
        res.append(set1[i]|set2[i])
    return res

def getParamPosition(string):
    res=[]
    for i in range(len(string)):
        if string[i]=='1':
            res.append(i)
    return res

class Logparser:
    def __init__(self,filePath):
        self.filePath=filePath
        self.hashDict={}
        self.hashGroup={}
        self.data=[]

    def readFile(self):
        file=open(self.filePath,'r')
        for line in file.readlines():
            temp=line[:-1].split(" ")
            self.data.append(temp)

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

    def naiveCluster(self):
        res=[]
        for group in self.hashGroup.values():
            stdLogIdx=random.randint(0,len(group)-1)
            stdLog=group[stdLogIdx]
            disSet=set()
            disDict={}
            for log in group:
                dis=countVecDis(stdLog,log)
                disSet.add(dis)
                if dis not in disDict.keys():
                    disDict[dis]=[log]
                else:
                    disDict[dis].append(log)
            disSet=sorted(disSet,key=lambda p: p.count('1'))
            for dis in disSet:
                if dis.count('1')==0:
                    continue
                disDict[dis]
                self.statistic(disDict[dis])
                break
            break
        #     res.append('\n')
        # file=open('res','w')
        # file.writelines(res)
        # file.close()

    def statistic(self,group):
        res=[]
        count=[set() for i in range(len(group[0]))]
        for log in group:
            for i in range(len(log)):
                count[i].add(log[i])
        temp=[len(count[i]) for i in range(len(count))]
        res.append(temp)
        res.append(len(group))
        with open('statistic','w') as f:
            for group in res:
                json.dump(group,f,indent=2)

    def train(self):
        self.readFile()
        self.groupingAndHashing()
        # self.naiveCluster()
        self.firstClustering()

    def firstClustering(self,threshold=3):
        res=[]
        file=open('res','w')
        for group in self.hashGroup.values():
            with open('xxx','w') as f:
                for log in group:
                    f.write(self.antiHash(log)+'\n')
            while len(group)>0:
                subgroup={}
                logDict={}
                paramSets=[set() for i in range(len(group[0]))]
                stdLogIdx=random.randint(0,len(group)-1)
                stdLog=group[stdLogIdx]
                group.remove(stdLog)
                # 按距离分subgroup
                for log in group:
                    dis=countVecDis(stdLog,log)
                    if dis not in subgroup.keys():
                        subgroup[dis]=[set([log[i]]) for i in range(len(log))]
                        logDict[dis]=[log]
                    else:
                        logDict[dis].append(log)
                        for i in range(len(log)):
                            subgroup[dis][i].add(log[i])
                sortedSubgroupKeys=sorted(subgroup.keys(),key=lambda d:d.count('1'))
                # merge
                first=True
                template=stdLog
                for key in sortedSubgroupKeys:
                    # 完全一样的直接跳过
                    setList=[set([stdLog[i]]) for i in range(len(stdLog))]
                    if key.count('1')==0:
                        for log in logDict[key]:
                            group.remove(log)
                    elif key.count('1')==1:
                        # 距离为1直接合并
                        template=mergeByDis(template,key)
                        first=False
                        print(self.antiHash(template))
                        print('----------')
                        setList=mergeSet(setList,subgroup[key])
                        for log in logDict[key]:
                            group.remove(log)
                    # 如果是第一次且距离小于阈值，也合并
                    elif first and key.count('1')<=threshold:
                        first=False
                        template=mergeByDis(template,key)
                        setList=mergeSet(setList,subgroup[key])
                        for log in logDict[key]:
                            group.remove(log)
                    elif first and key.count('1')>threshold:
                        first=False
                        res.append(template)
                    else:
                        paramPosition=getParamPosition(key)
                        canMerge=False
                        for i in paramPosition:
                            if subgroup[key][i] & setList[i]:
                                canMerge=True
                        if canMerge:
                            template=mergeByDis(stdLog,key)
                            setList=mergeSet(setList,subgroup[key])
                            for log in logDict[key]:
                                group.remove(log)
                        else:
                            # 终止
                            res.append(template)
                            break
            for log in res:
                file.write(self.antiHash(log)+'\n')
    def check(self):
        pass



if __name__=='__main__':
    lp=Logparser('guangda')
    lp.train()