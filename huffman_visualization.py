from manim import *

import numpy as np
import copy

class SubTree():
    def __init__(self, symbol, initialPosition, probability):
        self.leader = symbol
        self.probability = probability
        self.positions = {symbol : initialPosition}
        self.leftMostPosition = initialPosition[0]
        self.rightMostPosition = initialPosition[0]

    def __repr__(self):
        return f'(Leader: {self.leader}, Probability: {self.probability}, Positions: {self.positions})'

    def merge(self, mergeSubTree):
        self.probability += mergeSubTree.probability
        self.positions = {**self.positions, **mergeSubTree.positions}

        if mergeSubTree.leftMostPosition < self.leftMostPosition:
            self.leftMostPosition = mergeSubTree.leftMostPosition

        if mergeSubTree.rightMostPosition > self.rightMostPosition:
            self.rightMostPosition = mergeSubTree.rightMostPosition

    def move(self, movement):
        for node in self.positions:
            self.positions[node][0] += movement

        self.leftMostPosition += movement
        self.rightMostPosition += movement

class HuffTree():
    def __init__(self, inputSymbols, outputSymbols, probabilities):
        self.outputSymbols = outputSymbols
        self.codification = {symbol: "" for symbol in inputSymbols}
        self.tree = {}
        self.nodeCount = 1
        self.firstStep = True
        self.leadership = {symbol : {symbol} for symbol in inputSymbols}

        # Sort the nodes
        nodes = {}
        for i in range(0, len(inputSymbols)):
            symbol = inputSymbols[i]
            prob = probabilities[i]
            nodes[symbol] = prob

        nodes  = sorted(nodes.items(), key=lambda item : item[1])
        
        symbolsNum = len(inputSymbols)
        if symbolsNum % 2 == 0:
            pos = -1 - 2*((symbolsNum-1)//2)
        else:
            pos = - 2*(symbolsNum//2)

        # Place the nodes
        for symbol, prob in nodes:
            self.tree[symbol] = SubTree(symbol, [pos, -5, 0], prob)
            pos += 2

        #print(self.tree)

    def codificateStep(self):
        newEdges = []
        newLeadership = set()

        # Calculates the number of subTrees to group
        D = len(outputSymbols)

        if self.firstStep:
            self.firstStep = False

            r = (len(inputSymbols)-1) % (D-1)
            D = D - r
        
        # Groups the subtrees
        count = 0
        groupSubTrees = {}
        for leader in self.tree:
            if count == D: break

            groupSubTrees[leader] = self.tree[leader]

            # Codificate step
            for node in self.leadership[leader]:
                newLeadership.add(node)
                self.codification[node] = self.outputSymbols[count] + self.codification[node]

            # Delete leadership
            self.leadership.pop(leader)

            count += 1

        # Erase subtrees from tree
        for leader in groupSubTrees:
            self.tree.pop(leader)

        #print(groupSubTrees)

        # Create new subtree
        subTrees = [groupSubTrees[leader] for leader in groupSubTrees]

        first = subTrees[0]
        last = subTrees[-1]

        level = self.calculateLevel(subTrees)
        firstPosX = first.positions[first.leader][0]
        lastPosX = last.positions[last.leader][0]

        newNodePos = [(firstPosX+lastPosX)//2, level+2, 0]

        newSubTree = SubTree(str(self.nodeCount), newNodePos, 0)
        
        # Merge subtrees
        for s in subTrees:
            newSubTree.merge(s)
            newEdges.append((newSubTree.leader, s.leader))

        #print(newSubTree)

        # Update tree
        newElement = {newSubTree.leader: newSubTree}
        self.tree = {**newElement, **self.tree}

        # Update leadership
        self.leadership[newSubTree.leader] = newLeadership

        # Update nodeCount
        self.nodeCount += 1
        
        """
        print(self.tree)
        print(self.leadership)
        print(newEdges)
        print(self.codification)
        """

        return newEdges, newSubTree.leader

    def calculateLevel(self, subTrees):
        level = - 100
        for subTree in subTrees:
            if subTree.positions[subTree.leader][1] > level:
                level = subTree.positions[subTree.leader][1]

        return level

    def sortTree(self, newLeader):
        newPositions = {}

        # Store old tree
        oldTree = copy.deepcopy(self.tree)
        oldTreeOrder = [leader for leader in oldTree]
        print(oldTreeOrder)

        # Sort tree
        self.tree = dict(sorted(self.tree.items(), key=lambda item : item[1].probability))

        # Store overall order
        oldTreeOrder = [leader for leader in oldTree]
        print(oldTreeOrder)
        treeOrder = [leader for leader in self.tree]

        # Get old and new indexes
        oldIndex = oldTreeOrder.index(newLeader)
        newIndex = treeOrder.index(newLeader)

        subTreeAtIndex = oldTree[oldTreeOrder[newIndex]]

        newLeaderLeft = oldTree[newLeader].leftMostPosition
        newLeaderRight = oldTree[newLeader].rightMostPosition

        indexRight = subTreeAtIndex.rightMostPosition

        # Compute movements
        treeMovement = indexRight - newLeaderRight
        otherMovement = newLeaderLeft - newLeaderRight - 2

        # Move
        for leader in oldTreeOrder[0:newIndex+1]:

            if leader == newLeader:
                movement = treeMovement
            else:
                movement = otherMovement
            
            subTree = self.tree[leader]
            subTree.move(movement)
            
            # Update new positions
            for node in subTree.positions:
                newPositions[node] = subTree.positions[node]

        print(self.tree)
        return newPositions

inputSymbols = []
outputSymbols = []
probabilities = []

class HuffmanTree(MovingCameraScene):
    def construct(self):
        # Create HuffTree
        global inputSymbols, outputSymbols, probabilities
        huffTree = HuffTree(inputSymbols, outputSymbols, probabilities)
        tree = huffTree.tree
        #print(tree)
        # Create animation tree
        nodes = [sub for sub in tree]
        layout = {sub : tree[sub].positions[sub] for sub in tree}
        edges = []       

        animationTree = Graph(
            vertices=nodes,  # Nodos
            edges=edges,   # Aristas
            layout=layout,
            labels=True      # Mostrar etiquetas en los nodos
        )
        #print(nodes)
        self.camera.frame.scale(1.5)
        self.camera.frame.move_to(ORIGIN)

        self.play(Create(animationTree))
        self.wait(2)

       # Loops until done
        while len(tree) > 1:
            # Codificate and update tree
            newEdges, newNode = huffTree.codificateStep()
            tree = huffTree.tree
            newPos = {newNode: tree[newNode].positions[newNode]}

            # Animate new node
            self.play(animationTree.animate.add_vertices(newNode, positions=newPos, labels=True))
            for edge in newEdges:
                self.play(animationTree.animate.add_edges(edge))

            self.wait(2)
        
            # Sort new tree
            newPositions = huffTree.sortTree(newNode)

            # Animate sorting
            for node in newPositions:
                self.play(animationTree.vertices[node].animate.move_to(newPositions[node]))
            
            self.wait(2)

inputSymbols = ['A', 'B', 'C', 'D']
outputSymbols = ['0', '1']
probabilities = [0.25, 0.25, 0.25, 0.25]

scene = HuffmanTree()
scene.construct()
