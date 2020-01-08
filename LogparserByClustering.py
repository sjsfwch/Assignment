import random
import json
from tqdm import tqdm
PARAM='#PARAM'

def countVecDis(vec1,vec2):
    dis=""
    #优化可以用字节表示一位
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

def checkPositionParam(positionList,setList,threshold=5):
    for i in positionList:
        if len(setList[i])<threshold:
            return False
    return True

def checkCanMerge1(key,threshold,punish):
    '''
    punish是一个turple，第一项是遇到1的惩罚项，第二项是遇到0的惩罚项
    '''
    count=0
    for c in key:
        if c=='1':
            count+=punish[0]
        else:
            count+=punish[1]
        count=max(0,count)
        if count<=threshold:
            return True
    return False

def checkCanMerge2(paramPosition,setList,threshold):
    for pos in paramPosition:
        if len(setList[pos])>=threshold:
            return True
    return False

def checkCanMerge3(positionList,setList1,setList2):
    for i in positionList:
        if setList1[i] & setList2[i]:
            return True
    return False

def outputModel(filePath):
    file=open(filePath,'r')
    model={"model":{"templates":[]}}
    for line in file.readlines():
        template={"token_sequences":[]}
        words=line.split(' ')
        for word in words:
            template["token_sequences"].append({"type":"word","value":word})
        model["model"]["templates"].append(template)
    with open("resJson.json",'w') as f:
        json.dump(model,f,indent=2)
    file.close()
    return

def changeModel(filePath):
    with open(filePath,'r') as f:
        model=json.load(f)
    res={"model":{"templates":[]}}
    for template in model["model"]["templates"]:
        res["model"]["templates"].append({"token_sequences":template["token_sequences"]})
    with open('model111111','w') as f:
        json.dump(res,f,indent=2)
    return

class Logparser:
    def __init__(self,filePath):
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
        # self.firstClustering()
        self.secondClustering()

    def firstClustering(self,threshold=3):
        res=[]
        file=open('res','w')
        self.semiFinalRes={}
        pbar=tqdm(total=len(self.hashGroup))
        for group in self.hashGroup.values():
            self.semiFinalRes[len(group[0])]=[]
            pbar.update(1)
            res=[]
            threshold=len(group[0])*0.3
            # with open('xxx','w') as f:
            #     for log in group:
            #         f.write(self.antiHash(log)+'\n')
            while len(group)>0:
                subgroup={}
                logDict={}
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
                setList=[set([stdLog[i]]) for i in range(len(stdLog))]
                for key in sortedSubgroupKeys:
                    # 完全一样的直接跳过
                    if key.count('1')==0:
                        for log in logDict[key]:
                            group.remove(log)
                    elif key.count('1')==1:
                        # 距离为1直接合并
                        template=mergeByDis(template,key)
                        first=False
                        # print(self.antiHash(template))
                        # print('----------')
                        setList=mergeSet(setList,subgroup[key])
                        for log in logDict[key]:
                            group.remove(log)
                    # 如果是第一次且距离小于阈值，也合并
                    elif first and key.count('1')<=threshold:
                        first=False
                        # 计算canMerge3
                        paramPosition=getParamPosition(key)
                        canMerge3=checkPositionParam(paramPosition,setList)
                        if not canMerge3:
                            break
                        template=mergeByDis(template,key)
                        setList=mergeSet(setList,subgroup[key])
                        for log in logDict[key]:
                            group.remove(log)
                    elif first and key.count('1')>threshold:
                        first=False
                        # 有离散1
                        canMerge=False
                        paramPosition=getParamPosition(key)
                        count=0
                        for i in range(len(paramPosition)-1):
                            if paramPosition[i+1]-paramPosition[i]==1:
                                count+=1
                            else:
                                count-=0.5
                        if count<=3:
                            canMerge=True
                        # 计算canMerge3
                        paramPosition=getParamPosition(key)
                        canMerge3=checkPositionParam(paramPosition,setList)
                        if not canMerge3:
                            break
                        if canMerge&canMerge3:
                            template=mergeByDis(template,key)
                            setList=mergeSet(setList,subgroup[key])
                            for log in logDict[key]:
                                group.remove(log)
                        else:
                            # log=self.antiHash(template)
                            # res.append(log+'\n')
                            break
                    else:
                        paramPosition=getParamPosition(key)
                        canMerge1,canMerge2=False,False
                        # 加一个离散机制
                        count=0
                        for i in range(len(paramPosition)-1):
                            if paramPosition[i+1]-paramPosition[i]==1:
                                count+=1
                            else:
                                count-=0.5
                            if count>3:
                                break
                            count=max(0,count)
                        if count<=3:
                            canMerge1=True
                        canMerge2=checkCanMerge3(paramPosition,setList,subgroup[key])
                        # for i in paramPosition:
                        #     if subgroup[key][i] & setList[i]:
                        #         canMerge=True
                        if canMerge1 or canMerge2:
                            template=mergeByDis(stdLog,key)
                            setList=mergeSet(setList,subgroup[key])
                            for log in logDict[key]:
                                group.remove(log)
                        else:
                            # 终止
                            # log=self.antiHash(template)
                            # res.append(log+'\n')
                            break
                self.semiFinalRes[len(template)].append(template)
                log=self.antiHash(template)
                res.append(log[:-1]+'\n')
            file.writelines(res)
            # file.write("---------------\n")
    
    def secondClustering(self,thresholdRate=0.3,minThreshold=3):
        res=[]
        totalCount=0
        self.semiFinalRes={}
        for group in self.hashGroup.values():
            totalCount+=1
            print('总进度{}/{}'.format(totalCount,len(self.hashGroup)))
            threshold=max(thresholdRate*len(group[0]),minThreshold)
            groupNum=len(group)
            groupCount=0
            while len(group)>0:
                
                # 随机拿出一条log，然后分subgroup
                subgroup={}
                logDict={}
                stdLogIdx=random.randint(0,len(group)-1)
                stdLog=group[stdLogIdx]
                setList=[set([stdLog[i]]) for i in range(len(stdLog))]
                # group.remove(stdLog)
                groupCount+=1
                template=stdLog
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
                first=True
                for key in sortedSubgroupKeys:
                    # 完全一样的直接跳过
                    if key.count('1')==0:
                        for log in logDict[key]:
                            group.remove(log)
                        # del logDict[key]
                    elif key.count('1')==1:
                        # 距离为1直接合并
                        template=mergeByDis(template,key)
                        first=False
                        # print(self.antiHash(template))
                        # print('----------')
                        setList=mergeSet(setList,subgroup[key])
                        for log in logDict[key]:
                            group.remove(log)
                        # del logDict[key],subgroup[key]
                    # 第一次
                    if first:
                        first=False
                        # 计算canMerge1 punish(遇1的，遇0的)
                        canMerge1=checkCanMerge1(key,threshold,(1,-0.5))
                        # 计算canMerge2
                        paramPosition=getParamPosition(key)
                        canMerge2=checkCanMerge2(paramPosition,subgroup[key],threshold)
                        if canMerge1:
                            # 符合则merge
                            template=mergeByDis(template,key)
                            setList=mergeSet(setList,subgroup[key])
                            for log in logDict[key]:
                                group.remove(log)
                                groupCount+=1
                            print('group进度：{}/{}'.format(groupCount,groupNum),end='\r')
                            # del subgroup[key]
                            # del logDict[key]
                        else:
                            # 否则，停止
                            break
                    else:
                        canMerge1=checkCanMerge1(key,threshold,(1,-0.5))
                        paramPosition=getParamPosition(key)
                        canMerge2=checkCanMerge2(paramPosition,subgroup[key],threshold)
                        canMerge3=checkCanMerge3(paramPosition,setList,subgroup[key])
                        if canMerge3 and canMerge1:
                            template=mergeByDis(template,key)
                            setList=mergeSet(setList,subgroup[key])
                            for log in logDict[key]:
                                group.remove(log)
                                groupCount+=1
                            print('group进度：{}/{}'.format(groupCount,groupNum),end='\r')
                            # del subgroup[key]
                            # del logDict[key]
                        else:
                            break
                log=self.antiHash(template)
                print(log)
                res.append(log+'\n')
        file=open('secondRes','w')
        file.writelines(res)
        file.close()

    def lastMerge(self):
        self.finalRes={}
        if not self.semiFinalRes:
            return
        for group in self.semiFinalRes.values():
            self.finalRes[len(group[0])]=[]
            for log in group:
                pass

if __name__=='__main__':
    lp=Logparser('guangda')
    lp.train()
    # outputModel('res')
    # changeModel("model.json")