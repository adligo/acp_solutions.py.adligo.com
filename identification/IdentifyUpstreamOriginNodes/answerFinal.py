import sys
from collections import deque
from typing import Callable
from logging import Logger, LogConfig

class AdjacencyMapMutant:

    def __init__(self, directional: bool):
        self.directional = directional
        # map of character to set of character
        self.nodeIdsToEdgeNodeIds = {}

    def isDirected(self):
        return self.directional

    def addNode(self, nodeId: str):
        self.nodeIdsToEdgeNodeIds.setdefault(nodeId, set())

    def addEdge(self, fromNodeId: str, toNodeId: str):
        self.nodeIdsToEdgeNodeIds.setdefault(fromNodeId, set()).add(toNodeId)
        self.addNode(toNodeId)

    def getAllNodes(self):
        return self.nodeIdsToEdgeNodeIds.keys()

    def getEdges(self, fromNodeId: str):
        return self.nodeIdsToEdgeNodeIds[fromNodeId]


class AdjacencyBitSlotMatrix:
    def __init__(self, adjacencyMap: AdjacencyMapMutant, logConfig: LogConfig):
        self.directional = adjacencyMap.isDirected()
        self.log = logConfig.getLog("AdjacencyBitSlotMatrix")

        # swapping sorted just allows for nicer printing :)
        asymptoticSmell = False
        if asymptoticSmell:
            # asymptotic smell
            self.log.log(Logger.WARNING, lambda: f" Sorting Node Keys for Pretty Printing, an asymptotic smell")
            self.allNodes = sorted(adjacencyMap.getAllNodes())
        else:
            self.allNodes = adjacencyMap.getAllNodes()

        # create the key (str) to id (int) matrix
        counter = 0
        self.keyToId = {}
        self.idToKey = []
        #
        # This must be done before assigning slots in the matrix
        #
        for n in self.allNodes:
            self.keyToId[n] = counter
            self.idToKey.append(n)
            counter += 1
        self.log.log(Logger.DEBUG, lambda: f" in log trace printing self.keyToId\n{self.keyToId}")

        self.size = len(self.allNodes)
        self.rowMap = {}
        self.colMap = {}
        # init all the colums
        for n in self.allNodes:
            self.colMap[n] = 0

        self.log.log(Logger.DEBUG, lambda: f"size {self.size} ")
        # do all the rows
        for n in self.allNodes:
            row = 0

            edges = adjacencyMap.getEdges(n)
            self.log.log(Logger.DEBUG, lambda: f"\n\nStarting node {n}")

            for edge in edges:
                edgeIntId = self.keyToId[edge]

                # Mutate the row
                # push the bit on to the number that represents the matrix
                self.log.log(Logger.DEBUG, lambda: f"pushing to slot {edgeIntId} in row for {n},{edge}")
                row |= 1 << edgeIntId
                self.log.log(Logger.DEBUG, lambda: format(row, str(self.size) + 'b')[::-1])

                # Mutate the column
                col = self.colMap[edge]
                self.log.log(Logger.DEBUG, lambda: "before col edits " + format(col, str(self.size) + 'b')[::-1])
                nodeIntId = self.keyToId[n]
                # push the bit on to the number that represents the matrix
                self.log.log(Logger.DEBUG, lambda: f"pushing to slot {nodeIntId} in col for {edge}, {n}")
                col |= 1 << nodeIntId
                self.log.log(Logger.DEBUG, lambda: format(col, str(self.size) + 'b')[::-1])
                self.colMap[edge] = col
            self.rowMap[n] = row

    def getAllNodes(self):
        return self.allNodes

    def isColZero(self, nodeKeyId: str):
        """
        Checks to see if anything references the node by looking at the
        column of the matrix and comparing the int
        (a [BitSlotMap#1.3.6.1.4.1.33097.1.1.3](https://adligo.github.io/papers.adligo.com/index.html#bitslotmaps)
        [aka a BitVector]) to zero.
        raise a Key error if the key is missing

        :param nodeKeyId:
        :return:
        """
        col = self.colMap[nodeKeyId]
        if col == 0:
            return True
        return False


    def printMatrix(self, alsoCols: bool = False):

        firstLineList = [" "]
        rowLines = []
        for i in range(0, len(self.idToKey)):
            k = self.idToKey[i]
            firstLineList.append(k)
            rowLines.append(k + format(self.rowMap[k], str(self.size) + 'b')[::-1])
        firstLine = "".join(firstLineList)
        print("The Matrix as Rows is:")
        print("".join(firstLineList))
        for row in rowLines:
            print(row)

        print("\n\nAs Columns")
        if alsoCols:
            rowStrings = []
            print(firstLine)
            for r in range(0, len(self.idToKey)):
                k = self.idToKey[r]
                rowText = [k]
                for c in range(0, len(self.idToKey)):
                    colKey = self.idToKey[c]
                    col = self.colMap[colKey]
                    isBitSet = col & (1 << r)
                    if isBitSet:
                        rowText.append("1")
                    else:
                        rowText.append("0")
                print("".join(rowText))





class AdjacencyBitSlotMatrixMap:
    def __init__(self, adjacencyMap: AdjacencyMapMutant, logConfig: LogConfig):
        self.log = logConfig.getLog("AdjacencyBitSlotMatrix")
        self.adjacencyMap = adjacencyMap
        self.matrix = AdjacencyBitSlotMatrix(adjacencyMap, logConfig)
        if self.log.getLevel() <= Logger.INFO:
            self.matrix.printMatrix(True)

    def identifyUpstreamOriginNodes(self):
        # Note these may have been sorted in the matrix
        allNodes = self.matrix.getAllNodes()
        nodesWithoutReferencesToThem = []
        for n in allNodes:
            if self.matrix.isColZero(n):
                nodesWithoutReferencesToThem.append(n)

        self.log.log(Logger.DEBUG, lambda: f"nodesWithoutReferencesToThem include \n {nodesWithoutReferencesToThem} ")

        # check that nodesWithoutReferencesToThem reference something (are upstream from something, and not just
        #    detached nodes)
        upstreamOriginNodes = []
        for n in nodesWithoutReferencesToThem:
            edges = self.adjacencyMap.getEdges(n)
            if len(edges) >= 1:
                upstreamOriginNodes.append(n)
        return upstreamOriginNodes


def identifyUpstreamOriginNodes(map: AdjacencyMapMutant) -> int:
    """
    Your code goes here
    :param map: The adjacency map with the populated values
    :return:
    """
    logConfig = LogConfig(Logger.WARNING)
    #logConfig = LogConfig(Logger.DEBUG)
    mm = AdjacencyBitSlotMatrixMap(map, logConfig)
    upNodes = mm.identifyUpstreamOriginNodes()
    mm.log.log(Logger.INFO, lambda: f"upNodes are \n {upNodes} ")
    return len(upNodes)