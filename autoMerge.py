
# dataset 模版的string List，param统一用#PARAM表示，比如“value is #PARAM”
import json

PARAM = "#PARAM"


class autoMerge:
    def __init__(self, threshold, dataset, isCarpenterModel=0):
        self.threshold = threshold
        self.dataset = dataset
        self.isCarpenterModel = isCarpenterModel
        self.result = []
        self.words = {}

    def grouping(self):
        self.group = {}
        for i in range(len(self.dataset)):
            temp = self.dataset[i].split(" ")
            if len(temp) not in self.group.keys():
                self.group[len(temp)] = [temp]
            else:
                self.group[len(temp)].append(temp)

    def groupingByCarpenterModel(self):
        self.group = {}
        templates = self.dataset["model"]["templates"]
        for template in templates:
            temp = []
            for token in template["token_sequences"]:
                if "value" in token.keys() and token["value"] != "":
                    temp.append(token["value"])
                else:
                    temp.append(PARAM)
            if len(temp) not in self.group.keys():
                self.group[len(temp)] = [temp]
            else:
                self.group[len(temp)].append(temp)
        self.group = dict((x, y) for x, y in sorted(
            self.group.items(), key=lambda d: d[0]))

    def hashing(self):
        self.hashingGroup = {}
        self.words[hash(PARAM)] = PARAM
        for key, group in self.group.items():
            # 只有一个模板的group不需要聚类 直接加入res
            if len(group) == 1:
                self.result.append("group"+str(len(group[0])))
                template = ""
                for word in group[0]:
                    template += word+" "
                # 去掉结尾的那个空格
                self.result.append(template[:-1])
                self.result.append('\n\n')
            else:
                self.hashingGroup[key] = []
                for template in group:
                    templateVec = []
                    for word in template:
                        value = hash(word)
                        self.words[value] = word
                        templateVec.append(value)
                    self.hashingGroup[key].append(templateVec)

    def clustering(self):
        if self.isCarpenterModel:
            self.groupingByCarpenterModel()
        else:
            self.grouping()
        # self.printRawGroup()
        self.hashing()
        file = open("group", 'w')
        newHashingGroup = {}
        for key, group in self.hashingGroup.items():
            # print(group)
            groupDis, minDis = counting(group)
            while minDis[2] <= self.threshold and len(group) > 1 and minDis[0] != minDis[1]:
                minDis, groupDis, group = merge(
                    minDis[0], minDis[1], groupDis, group)
                # self.printByGroup("midoutput", group)
            newHashingGroup[key] = group
            json.dump(groupDis, file, indent=2)
        self.hashingGroup = newHashingGroup

    def output(self, fliePath):
        # 把哈希值还原为模版
        self.hashingGroup = dict((x, y) for x, y in sorted(
            self.hashingGroup.items(), key=lambda d: d[0]))
        # self.hashingGroup=dict((x,y) for x,y in sorted(self.hashingGroup.items(),key=lambda d: d[0]))
        for group in self.hashingGroup.values():
            self.result.append("group"+str(len(group[0])))
            for temVec in group:
                template = ""
                for value in temVec:
                    template += self.words[value]+' '
                self.result.append(template)
            self.result.append("\n"+'\n')
        # 输出
        with open(fliePath, 'w') as f:
            for template in self.result:
                f.write(template+'\n')

    def printByGroup(self, filePath, group):
        res = []
        for temVec in group:
            template = ""
            for value in temVec:
                template += self.words[value]+' '
            res.append(template[:-1])
        f = open(filePath, 'a')
        for template in res:
            f.write(template+"\n")
        f.write('\n'+'\n'+'\n')

    def clusteringByOnce(self):
        pass

    def printRawGroup(self):
        rawTemp = []
        for lens, group in self.group.items():
            rawTemp.append("group"+str(lens)+'\n')
            for temVec in group:
                template = ""
                for word in temVec:
                    template += word+' '
                rawTemp.append(template[:-1]+"\n")
            rawTemp.append('\n\n')
        with open("rawGroup", 'w') as f:
            f.writelines(rawTemp)


def counting(group):
    groupDis = []
    minDis = (0, 0, len(group[0])+1)
    for i in range(len(group)-1):
        for j in range(i+1, len(group)):
            dis = countingDis(group[i], group[j])
            groupDis.append((i, j, dis))
            if minDis[2] > dis:
                minDis = (i, j, dis)
    return groupDis, minDis


def countingDis(temVec1, temVec2):
    dis = 0
    for i in range(len(temVec1)):
        if temVec1[i] == temVec2[i]:
            continue
        elif temVec1[i] == hash(PARAM) or temVec2[i] == hash(PARAM):
            dis += 1
        else:
            dis += 1
    return dis


def merge(Ti, Tj, groupDis, group):
    newTem = []
    minDis = (0, 0, len(group[0]))
    # 先合并
    for i in range(len(group[Ti])):
        if group[Ti][i] == group[Tj][i]:
            newTem.append(group[Ti][i])
        else:
            newTem.append(hash(PARAM))
    # 删除旧的加入新的，并更新groupDis
    x, y = group[Ti], group[Tj]
    group.remove(x)
    group.remove(y)

    newGroupDis = []
    for item in groupDis:
        if not (item[0] == Ti or item[0] == Tj or item[1] == Ti or item[1] == Tj):
            if item[2] < minDis[2]:
                x, y = -1, -1
                # 位置变动，三种情况，小于Ti和Tj，大于Ti但小于Tj，大于Ti和Tj
                if item[0] < Ti:
                    x = item[0]
                elif item[0] < Tj:
                    x = item[0]-1
                else:
                    x = item[0]-2
                if item[1] < Ti:
                    y = item[1]
                elif item[1] < Tj:
                    y = item[1]-1
                else:
                    y = item[1]-2

            newGroupDis.append(item)
    for i in range(len(group)):
        dis = countingDis(group[i], newTem)
        if dis < minDis[2]:
            minDis = (i, len(group), dis)
        newGroupDis.append((i, len(group), dis))
    group.append(newTem)
    # print(group)
    return minDis, newGroupDis, group


if __name__ == "__main__":
    dataset = []
    # f = open("midoutput", 'w')
    # f.close()
    with open("HDFS_2k.log", 'r') as f:
        dataLine = f.readlines()
        for line in dataLine:
            dataset.append(line[:-1])
    # with open("model-ceph.json", 'r') as f:
    #     dataset = json.load(f)
    x = autoMerge(8, dataset)
    x.clustering()
    x.output("result")
