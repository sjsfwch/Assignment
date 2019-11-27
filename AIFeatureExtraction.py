import pandas as pd
import sys
import math
# 核心思想，根据过去t时间内该变量出现值的个数和2t，3t，...，nt内出现值的个数判断是不是离散型变量，并且量要大


class Extractor:
    def __init__(self, timeslice, n, ocurrTimesThreshold, limits, dataset):
        '''
        timeslice是选定的时间t，单位是秒
        n是进行多少个nt时间内的统计
        ocurrTimesThreshold是该变量出现的次数，低于阈值的直接pass
        limits是nt时间的统计可以有多大的出入|sum(nt)-sum(t)|<=limits
        dataset：{"timestamp":, "tid":, "variables":[variables]}
        '''
        self.timeslice = timeslice
        self.n = n
        self.ocurrTimesThreshold = ocurrTimesThreshold
        self.limits = limits
        self.dataset = dataset
        self.statisticData = {}

    def getStartEnd(self):
        start, end = sys.maxsize, 0
        for data in self.dataset:
            start = min(data["timestamp"])
            end = max(data["timestamp"])
        return start, end

    def statistic(self):
        start, end = self.getStartEnd()
        seg = self.n if self.n * self.timeslice <= end - start else math.floor(
            (end - start) / self.timeslice) + 1
        for data in self.dataset:
            if data["tid"] not in self.statisticData.keys():
                self.statisticData[data["tid"]] = [[
                    set() for j in range(len(data["variables"]))
                ] for i in range(seg)]
            index = math.floor((data["timestamp"] - start) / seg)
            for i in range(len(data["variables"])):
                self.statisticData[data["tid"]][i][index].add(
                    data["variables"][i])

    def analyze(self):
        '''
        '''
        res = []
        for tid, data in self.statisticData.items():
            for i in range(len(data)):
                minLen, maxLen = sys.maxsize, 0
                for j in range(len(data[i])):
                    minLen = min(minLen, len(data[i][j]))
                    maxLen = min(maxLen, len(data[i][j]))
                # 小于阈值，则加入结果，结构为（tid，paramIndex）
                if maxLen - minLen < self.limits:
                    res.append((tid, i))
        return res
