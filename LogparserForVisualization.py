import random
import json
from tqdm import tqdm
import os
PARAM='#PARAM'
DELIMPREFIX="#delim#"
# 数据结构区
# ------------------------------------------------------------------------
'''
res{
    'group':{
        'template':{
            'count':count,
            'paramList':paramList
        }
    }
}
subGroup{
    'dis':paramList
}

logDict{
    'dis':[log]
}

paramList:[
    {
        'paramValue1':count,
        'paramValue2':count
    },
    {...}
]
'''
# ------------------------------------------------------------------------
# 公共函数区
# ------------------------------------------------------------------------
def mergeLogToParamList(log,paramList,count=1):
    if not paramList:
        for i in range(len(log)):
            paramList.append({log[i]:count})
    else:
        for i in range(len(log)):
            if log[i] in paramList[i].keys():
                paramList[i][log[i]]+=count
            else:
                paramList[i][log[i]]=count
    return paramList

def mergeDict(dict1,dict2):
    if not dict1:
        return dict2
    elif not dict2:
        return dict1
    elif len(dict1)<len(dict2):
        return mergeDict(dict2,dict1)
    else:
        for key in dict2.keys():
            if key not in dict1.keys():
                dict1[key]=dict2[key]
            else:
                dict1[key]+=dict2[key]
        return dict1

def mergeParamLists(paramList1,paramList2):
    # 两个paramList必须有一样的长度
    assert(len(paramList1)==len(paramList2))
    paramList=[]
    for pos in range(len(paramList1)):
        paramList.append(mergeDict(paramList1[pos],paramList2[pos]))
    return paramList

def countVecDis(vec1,vec2):
    dis=""
    #优化可以用字节表示一位
    for i in range(len(vec1)):
        if vec1[i]==vec2[i]:
            dis+='0'
        else:
            dis+='1'
    return dis

def getParamPosition(string):
    res=[]
    for i in range(len(string)):
        if string[i]=='1':
            res.append(i)
    return res

def divideGroupByDis(stdLog,group):
    subGroup,logDict={},{}
    for log in group:
        dis=countVecDis(stdLog,log)
        if dis not in subGroup.keys():
            logDict[dis]=[log]
            subGroup[dis]=mergeLogToParamList(log,[])
        else:
            logDict[dis].append(log)
            subGroup[dis]=mergeLogToParamList(log,subGroup[dis])
    return subGroup,logDict

def mergeByDis(stdLog,dis):
    res=[]
    for i in range(len(stdLog)):
        if dis[i]=='1':
            res.append(hash(PARAM))
        else:
            res.append(stdLog[i])
    return res

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

def checkCanMerge2(positionList,paramList1,paramList2):
    for pos in positionList:
        if paramList1[pos].keys()&paramList2[pos].keys():
            return True
    return False

def checkAndGetDelim(word):
    pos=word.find(DELIMPREFIX)
    if pos==-1:
        return False,word
    else:
        return True,word[pos+len(DELIMPREFIX):]

def getLogKeyByDelim(log):
    key=''
    for word in log:
        # 不是int说明没做hash，肯定是delim
        if type(word)==int:
            key+='*'
        else:
            key+=word
    return key

def groupingByDelim(group):
    resGroup={}
    for log in group:
        logKey=getLogKeyByDelim(log)
        if logKey not in resGroup.keys():
            resGroup[logKey]=[log]
        else:
            resGroup[logKey].append(log)
    return resGroup


def masterMerge(stdLog,subGroup,logDict,paramList,group,threshold=3):
    template=stdLog
    first,canMerge=True,False
    sortedSubgroupKeys=sorted(subGroup.keys(),key=lambda d:d.count('1'))
    count=0
    for key in sortedSubgroupKeys:
        # 完全一样的，直接删除+mergeParam
        if key.count('1')==0:
            canMerge=True
            # deleteLog=True
            # paramList=mergeLogToParamList(stdLog,paramList,len(logDict[key]))
        # 第一次合并
        # elif key.count('1')==1:
        #     first=False
        #     deleteLog=True
        #     template=mergeByDis(template,key)
        #     paramList=mergeParamLists(paramList,subGroup[key])
        elif first:
            first=False
            canMerge1=checkCanMerge1(key,threshold,(1,-0.5))
            canMerge=canMerge1
        else:
            canMerge1=checkCanMerge1(key,threshold,(1,-0.5))
            positionList=getParamPosition(key)
            canMerge2=checkCanMerge2(positionList,paramList,subGroup[key])
            canMerge=canMerge2
        if canMerge:
            template=mergeByDis(template,key)
            paramList=mergeParamLists(paramList,subGroup[key])
            for log in logDict[key]:
                group.remove(log)
                count+=1
        else:
            break
    print("合并成功，共合并{}条日志".format(count))
    return template,paramList,group,count




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
        self.logCount=0
        self.allTemplates=[]

    def readFile(self,maxCount=500000):
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
        self.logCount=count
        file.close()

    def groupingAndHashing(self):
        self.hashDict[hash(PARAM)]=PARAM
        for log in self.data:
            logVec=[]
            for word in log:
                isDelim,word=checkAndGetDelim(word)
                # delim不哈希
                if isDelim:
                    hashValue=word
                else:
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
        totalLog=0
        # 先对每个group 按照delim绝对匹配分组
        for group in self.hashGroup.values():
            groupsByDelim=groupingByDelim(group)
            templates=[]
            for group in groupsByDelim.values():
                groupLen=len(group[0])
                threshold=min(len(group[0])*thresholdRate,minThreshold)
                while len(group)>0:
                    # 三个结构见数据结构区
                    subGroup,logDict,paramList={},{},[]
                    # 随机选一条log
                    stdLogIdx=random.randint(0,len(group)-1)
                    stdLog=group[stdLogIdx]
                    paramList=mergeLogToParamList(stdLog,paramList)
                    group.remove(stdLog)
                    # 获取subGroup logDict
                    subGroup,logDict=divideGroupByDis(stdLog,group)
                    # merge
                    template,paramList,group,count=masterMerge(stdLog,subGroup,logDict,paramList,group,threshold)
                    template=self.antiHash(template)
                    totalLog+=count
                    templates.append({'template':template,'count':count,'paramList':paramList})
            res[groupLen]={"template":templates}
        self.antiHashRes(res)
        with open('newRes','w') as f:
            json.dump(res,f,indent=2)
        self.outputAsSpecificFormat(res)
        print("模版提取完成，共有{}条log".format(totalLog))
    
    def oneKey(self):
        self.readFile()
        self.groupingAndHashing()
        self.clustering()
    
    def antiHashRes(self,res):
        for group in res.values():
            for template in group["template"]:
                template['paramList']=self.antiHashParamList(template['paramList'])
                self.allTemplates.append({'count':template['count'],'paramList':template['paramList']})
        return res

    def antiHashParamList(self,paramList):
        antiRes=[]
        for d in paramList:
            antiD={}
            for key in d.keys():
                antiD[self.hashDict[key]]=d[key]
            antiRes.append(antiD)
        return antiRes
    
    def outputAsSpecificFormat(self, res):
        assert(self.allTemplates)
        output = {'model': {'profile': {
            'count': self.logCount,
            'max_value': 1541473200000.0,
            'min_value': 1541383200000.0,
            'window_size': 1541473200000.0-1541383200000.0,
            'cnt_by_window': [self.logCount]
        },
        'templates':[]
        }}
        for template in self.allTemplates:
            newTemplate={
                'profile':{
                    'count': template['count'],
                    'max_value': 1541473200000.0,
                    'min_value': 1541383200000.0,
                    'window_size': 1541473200000.0-1541383200000.0,
                    'cnt_by_window': template['count']
                },
                'samples':[],
                'token_sequences':[]
            }
            tokens=[]
            count=0
            for param in template['paramList']:
                # 只有一个词 说明是模板单词，否则是变量
                if len(param.keys())==1:
                    tokens.append({'type':'word','value':list(param.keys())[0]+' '})
                else:
                    tem={
                        'profile':{'type':'enumerable','counts':[],'values':[]},
                        'index':count,
                        'value':'',
                        'subtype':'string',
                        'var_group':'',
                        'type':'tree_var'
                    }
                    for value in param.items():
                        tem['profile']['values'].append(value[0])
                        tem['profile']['counts'].append(value[1])
                    count+=1
                    tokens.append(tem)
            newTemplate['token_sequences']=tokens
            output["model"]["templates"].append(newTemplate)
        with open('newmodel','w') as f:
            json.dump(output,f,indent=2)






if __name__=="__main__":
    lp=Logparser('guangda')
    lp.oneKey()
    os.system("rm ../../carpenter-web/data/spd/model.json")
    os.system("mv newModel ../../carpenter-web/data/spd/model.json")
