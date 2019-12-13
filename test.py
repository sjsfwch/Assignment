import json
import pandas as pd

# with open("spd.json","r") as f:
#     dictF=json.load(f)
# json.dump(dictF,open("spdF.json","w"),indent=2)

# data=pd.read_csv("normal.csv")
# x=data["template"]
# s=set()
# file=open("template","w")
# for i,v in x.iteritems():
#     s.add(v+'\n')
# file.writelines(s)
# file.close()
import random
PARAM='#PRAM'
file = open("HDFS_2k.log",'r')
data=[]
for line in file.readlines():
    temp=line[:-1].split(" ")
    data.append(temp[2:])

hashDict={}
hashGroup={}
hashDict[hash(PARAM)]=PARAM
for log in data:
#     grouping&hashing
    temVec=[]
    for word in log:
        hashValue=hash(word)
        if hashValue not in hashDict.keys():
            hashDict[hashValue]=word
        temVec.append(hashValue)
    temLen=len(temVec)
    if temLen not in hashGroup.keys():
        hashGroup[temLen]=[temVec]
    else:
        hashGroup[temLen].append(temVec)

def countVecDis(vec1,vec2):
    dis=""
#     优化可以用字节表示一位
    for i in range(len(vec1)):
        if vec1[i]==vec2[i]:
            dis+='0'
        else:
            dis+='1'
    return dis

def antiHash(log):
    res=""
    for word in log:
        res+=hashDict[word]+' '
    print(res)

def merge(stdLog,dis):
    res=[]
    for i in range(len(stdLog)):
        if dis[i]=='1':
            res.append(hash(PARAM))
        else:
            res.append(stdLog[i])
    return res

parsedTemGroup={}
hashGroup
threshold=5
for temLen,group in hashGroup.items():
#     随机找一个log，它必属于某个模板
    logTemPool=[]
#     print(temLen)
    while len(group)>0:
        #若group里只有一条日志了，直接放入模板池，跳出循环
        if len(group)==1:
            logTemPool.append(group[0])
            break
        logDict={}
        stdLogIdx=random.randint(0,len(group)-1)
        stdLog=group[stdLogIdx]
        for i in range(0,len(group)):
            if i==stdLogIdx:
                continue
            else:
                dis=countVecDis(stdLog,group[i])
                if dis not in logDict.keys():
                    logDict[dis]=[group[i]]
                else:
                    logDict[dis].append(group[i])
        minDis="".join(['1' for i in range(len(stdLog))])
#         找出距离最近的group，放入logPool
        for key in logDict.keys():
            minDis=key if key.count('1')<minDis.count('1') else minDis
#         如果大于阈值，说明不属于任何一个模板，直接加入模板池
        if minDis.count('1')>threshold:
            logTemPool.append(stdLog)
            group.remove(stdLog)
            continue
#         否则合并并删除
        newTplt=merge(stdLog,minDis)
        antiHash(newTplt)
        logTemPool.append(newTplt)
#        删除合并过后的
        for log in logDict[minDis]:
            group.remove(log)
    parsedTemGroup[temLen]=logTemPool

# 对模板池进行第二步聚类，此时差异的基本是未被聚类的变量，阈值设为1就行
threshold=1
result={}
for key,group in parsedTemGroup.items():
#     至少有一个模版
    complete=False
    print("!!!!!!!!!!!!!!!!!!")
    while not complete:
        logDict={}
        for i in range(len(group)):
            stdLog=group[i]
            antiHash(stdLog)
            print("----------------------")
            for j in range(len(group)):
                if i==j:
                    continue
                dis=countVecDis(stdLog,group[j])
                if dis not in logDict.keys():
                    logDict[dis]=[group[j]]
                else:
                    logDict[dis].append(group[j])
#             计算最短距离
            minDis="".join(['1' for i in range(len(stdLog))])
            for key in logDict.keys():
                minDis=key if key.count('1')<minDis.count('1') else minDis
#             判断是不是大于阈值
            print("MINDIS--------")
            if minDis.count('1')<=threshold:
                newTplt=merge(stdLog,minDis)
#                 合并，然后重新开始
                print(logDict[minDis])
                for log in logDict[minDis]:
                    print("DELETE------------")
                    print(log)
                    group.remove(log)
                group.remove(stdLog)
                print(group)
                antiHash(newTplt)
                print(len(group))
                group.append(newTplt)
                break
#             所有模板都查找聚合完毕
            if i==len(group)-1:
                complete=True
                result[key]=group
                for log in group:
                    antiHash(log)
