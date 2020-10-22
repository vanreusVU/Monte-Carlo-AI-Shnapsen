# Import the API objects
from api import State, util, Deck
import random, array
import numpy as np


class Node:
    def __init__(self):
        # DEBUG ONLY
        self.card = None

        self.state = None
        self.v = 0
        self.n = 0
        self.parent = None
        self.children = []


bestRoot = None


class Bot:
    root = None
    player = None
    N = 100
    DL = 100
    debug = False


    def __init__(self):
        pass

    def get_move(self, state):
        self.player = state.whose_turn()

        if state.get_phase() == 1:
            try:
                state = state.make_assumption()
            except:
                pass

        if bestRoot is None:
            self.root = Node()
            self.root.state = state

            if self.debug:
                if self.root.state.get_opponents_played_card() is not None:
                    self.root.card = util.get_card_name(self.root.state.get_opponents_played_card())
                    print(self.root.card[0], self.root.card[1])
                else:
                    print("Started With An Empty Deck")
                    print("Trump suit is: ", self.root.state.get_trump_suit())
                    print("Start...\n")

            self.expansion(self.root)
        else:
            if self.root.state.get_opponents_played_card() is not None:
                self.root = bestRoot
            else:
                for nodes in bestRoot.children:
                    if state == nodes.state:
                        self.root = nodes.state
                        break

        return self.root.state.moves()[self.MCTS(state)]

    def MCTS(self, state):
        for iteration in range(0, self.DL):
            if iteration == 0:
                simulationResult = self.rollout(self.root.children[self.selection(self.root)])
                self.backPropogation(simulationResult, self.root.children[self.selection(self.root)])
            else:
                search = True
                crNode = self.root
                while search:
                    crNode = crNode.children[self.selection(crNode)]

                    if len(crNode.children) == 0:
                        expansion = self.expansion(crNode)
                        if expansion:
                            selection = self.selection(crNode)
                            simulationResult = self.rollout(crNode.children[selection])
                            self.backPropogation(simulationResult, crNode.children[self.selection(crNode)])
                        search = False

        # self.printTree(self.root)
        # print()
        '''
        self.printTree(self.root.children[0])
        print()
        self.printTree(self.root.children[0].children[1])
        print()
        '''
        bestScore = bestIndex = i = 0
        for child in self.root.children:
            if not child.n or not child.v:
                score = 0
            else:
                score = child.v / child.n
            if score > bestScore:
                bestScore = score
                bestIndex = i
            i += 1

        bestRoot = self.root.children[bestIndex]
        if self.debug:
            print("Chosed Index= ", bestIndex)
        # Return a random choice
        return bestIndex

    def selection(self, currentNode=Node(), C=0.5):
        t = self.root.n

        index = bestIndex = bestSi = 0

        for child in currentNode.children:
            if child.n is 0:
                bestIndex = index
                break

            Xi = child.v / child.n
            Ni = child.n
            Si = Xi + C * np.sqrt(np.log(t) / Ni)

            if Si > bestSi:
                bestSi = Si
                bestIndex = index

            index += 1
       # if currentNode.children[bestIndex].state.finished() == True:
            #print("IM IN A TERMINAL NODE----------------------------------------")
        return bestIndex

    def expansion(self, currentNode=Node()):
        state = currentNode.state
        if state.finished() is True:
            return False
        for move in state.moves():
            # Play the card and set the state acording to the result
            st = state.clone()

            childNode = Node()

            if st.finished() is True:
                return False

            st = st.next(move)
            childNode.state = st
            childNode.parent = currentNode
            currentNode.children.append(childNode)

            # DEBUG ONLY
            if move[0] is not None:
                childNode.card = util.get_card_name(move[0])

        return True

    def rollout(self, currentNode=Node()):
        score = 0
        for ooo in range(0, self.N):
            st = currentNode.state.clone()
            i = 0
            # Do some random moves
            while not st.finished():
                st = st.next(random.choice(st.moves()))
                i += 1
            score += self.heuristics(st)
        return score


    def backPropogation(self, result, currentNode):
        while True:
            currentNode.n = currentNode.n + self.N
            currentNode.v = currentNode.v + result

            if currentNode.parent is None:
                break
            currentNode = currentNode.parent
        return

    def heuristics(self, state):
        Bonus = 0

        '''
        for card in state.moves():
            if card[0] == None:
                pass
            elif util.get_suit(card[0]) == state.get_trump_suit():
                    Bonus += -1
        '''

        if state.winner()[1] == 3:
            Bonus = 5
        elif state.winner()[1] == 2:
            Bonus = 20
        elif state.winner()[1] == 1:
            Bonus = 0
        return 1 + Bonus if state.winner()[0] == self.player else 0
