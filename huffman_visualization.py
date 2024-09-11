from manim import *
import numpy as np

class SubTree():
    def __init__(self, symbol, initialPosition, probability):
        self.leader = symbol
        self.probability = probability
        self.positions = {symbol : initialPosition}
        self.leftMostPosition = initialPosition
        self.rightMostPosition = initialPosition

    def __repr__(self):
        return f'(Node: {self.leader}, Probability: {self.probability}, Positions: {self.positions})'

    def merge(self, mergeSubTree, newLeader, newLeaderPosition):
        self.probability += mergeSubtree.probability
        self.leader = newLeader
        self.positions = {**self.positions, **mergeSubTree.positions}
        self.positions[newLeader] = newLeaderPosition

        if mergeSubTree.leftMostPosition[0] < self.leftMostPosition[0]:
            self.leftMostPosition = mergeSubTree.leftMostPosition

        if mergeSubTree.rightMostPosition[0] > self.rightMostPosition[0]:
            self.rightMostPosition = mergeSubTree.rightMostPosition

    def move_to(self, newLeaderPosition):
        movement = newLeaderPosition - positions[self.leader]
        for node in positions:
            positions[node] += movement

class HuffTree():
    def __init__(self, inputSymbols, outputSymbols, probabilities):
        self.codification = {}
        self.tree = {}

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

        print(self.tree)

    #def codificate(self):
        

        
    def sortTree(self):
        self.tree = dict(sorted(self.tree.items(), key=lambda item : item[1].probability))
        print(self.tree)


inputSymbols = []
outputSymbols = []
probabilities = []

class HuffmanTree(MovingCameraScene):
    def construct(self):
        # Create HuffTree
        global inputSymbols, outputSymbols, probabilities
        huffTree = HuffTree(inputSymbols, outputSymbols, probabilities)
        tree = huffTree.tree
        print(tree)
        # Create animation tree
        nodes = [sub for sub in tree]
        layout = {sub : tree[sub].leftMostPosition for sub in tree}
        edges = []       

        animationTree = Graph(
            vertices=nodes,  # Nodos
            edges=edges,   # Aristas
            layout=layout,
            labels=True      # Mostrar etiquetas en los nodos
        )
        print(nodes)
        self.camera.frame.scale(1.5)
        self.camera.frame.move_to(ORIGIN)

        # Mostrar el árbol
        self.play(Create(animationTree))
        self.wait(2)

"""# --------------- Agregar un nuevo nodo H -------------------
        # Definir el nuevo nodo y arista
        nuevo_nodo = "H"
        nueva_arista = ("N", "A")  # Nodo H conectado a E

        # Definir la posición del nuevo nodo en el layout

        # Agregar el nuevo nodo y arista al grafo
        #arbol.add_vertices(nuevo_nodo)
        #arbol.add_edges(nueva_arista)

        # Animar la aparición del nuevo nodo y arista
        self.play(arbol.animate.add_vertices("1", positions = {"1":[-2, 1, 0]}, labels= True))
        self.play(arbol.animate.add_edges(("1", "D")))
        self.play(arbol.animate.add_edges(("1", "E")))
        self.wait(2)

        self.play(
                arbol.vertices["1"].animate.move_to([2, 1, 0]),
                arbol.vertices["C"].animate.move_to([-2, 1, 0]),
                arbol.vertices["D"].animate.move_to([1, 0, 0]),
                arbol.vertices["F"].animate.move_to([-3, 0, 0]),
                arbol.vertices["E"].animate.move_to([3, 0, 0]),
                arbol.vertices["G"].animate.move_to([-1, 0, 0])
                )

        
        self.wait(2)"""


inputSymbols = ['A', 'B', 'C', 'D']
outputSymbols = ['0', '1']
probabilities = [0.4, 0.2, 0.2, 0.1]

scene = HuffmanTree()
scene.construct()
