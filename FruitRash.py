import time
import os
import sys


class FruitRash:
    def __init__(self):
        self.boardSize = 0
        self.timeLeft = 0.0
        self.fruitTypes = 0
        self.board = []
        self.currentChoiceScore = 0
        self.boolBoardVisited = None
        self.tempBoard = []
        self.columnsForGravity = dict()
        self.decideNextMove = []
        self.depthLimit = 3
        self.answer = False

    def displayBoard(self, board):
        print()
        for row in range(len(board)):
            for col in range(len(board)):
                if board[row][col] == -1:
                    print("*", end=" ")
                else:
                    print(board[row][col], end=" ")
            print()

    def writeOutput(self, board, nextMove):
        col = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
               'V', 'W', 'X', 'Y', 'Z']
        line1 = col[nextMove[2]] + str(nextMove[1] + 1) + "\n"

        with open("output.txt", 'w') as f:
            f.write(line1)

            for row in range(len(board)):
                for col in range(len(board)):
                    if board[row][col] == -1:
                        f.write("*")
                    else:
                        f.write(str(board[row][col]))
                f.write("\n")

    def writeOutput2(self, board, nextMove):

        with open("input.txt", 'w') as f:
            f.write(str(self.boardSize) + "\n")
            f.write(str(9) + "\n")
            f.write(str(30) + "\n")
            for row in range(len(board)):
                for col in range(len(board)):
                    if board[row][col] == -1:
                        f.write("*")
                    else:
                        f.write(str(board[row][col]))
                f.write("\n")

    def readInputFile(self, path):

        with open(path, 'r') as f:
            a = f.readlines()
            self.boardSize = int(a[0])
            self.fruitTypes = int(a[1])
            self.timeLeft = float(a[2]) - 0.05

            matrix = [row.strip() for row in a[3:]]

            transformMatrix = []
            for r in matrix:
                transformMatrix.append(list(map(lambda x: int(x) if x.isdigit() else -1, r)))

            self.board = transformMatrix

    def refreshVisitedMatrix(self):

        self.boolBoardVisited = [[False for i in range(self.boardSize)] for j in range(self.boardSize)]

    def dfsExploreConnectedComponents(self, board, boardSize, row, col, currentFruit):

        if row < 0 or col < 0 or row > boardSize - 1 or col > boardSize - 1 or board[row][col] == -1 or \
                self.boolBoardVisited[row][col] or board[row][col] != currentFruit:
            return

        self.boolBoardVisited[row][col] = True
        self.currentChoiceScore += 1

        self.dfsExploreConnectedComponents(board, boardSize, row + 1, col, currentFruit)
        self.dfsExploreConnectedComponents(board, boardSize, row - 1, col, currentFruit)
        self.dfsExploreConnectedComponents(board, boardSize, row, col - 1, currentFruit)
        self.dfsExploreConnectedComponents(board, boardSize, row, col + 1, currentFruit)

    def ProcessCurrentBoardSate(self, boardSize, board):
        '''

        :param boardSize: Dimension of the board
        :param board: current state of the board
        :return:
        '''

        validNextMoves = []

        for row in range(boardSize):
            for col in range(boardSize):
                if board[row][col] != -1 and not self.boolBoardVisited[row][col]:
                    self.currentChoiceScore = 0
                    self.dfsExploreConnectedComponents(board, boardSize, row, col, board[row][col])
                    validNextMoves.append([self.currentChoiceScore ** 2, row, col])

        return validNextMoves

    def pickFruit(self, board, row, col, currentFruit, boardSize):

        if row < 0 or col < 0 or row > boardSize - 1 or col > boardSize - 1 or board[row][col] == -1 or \
                self.boolBoardVisited[row][col] or board[row][col] != currentFruit:
            return

        self.boolBoardVisited[row][col] = True
        board[row][col] = -1

        if col not in self.columnsForGravity:
            self.columnsForGravity[col] = len(self.columnsForGravity)

        self.pickFruit(board, row + 1, col, currentFruit, boardSize)
        self.pickFruit(board, row - 1, col, currentFruit, boardSize)
        self.pickFruit(board, row, col - 1, currentFruit, boardSize)
        self.pickFruit(board, row, col + 1, currentFruit, boardSize)

    def applyGravity(self, parentBoard):

        for col in self.columnsForGravity.keys():

            emptyIndex = len(parentBoard) - 1
            filledIndex = emptyIndex - 1

            while emptyIndex >= 0 and filledIndex >= 0:
                while emptyIndex >= 0 and parentBoard[emptyIndex][col] != -1:
                    emptyIndex -= 1

                filledIndex = emptyIndex - 1

                while filledIndex >= 0 and parentBoard[filledIndex][col] == -1:
                    filledIndex -= 1

                if emptyIndex > filledIndex and emptyIndex >= 0 and filledIndex >= 0:
                    parentBoard[emptyIndex][col], parentBoard[filledIndex][col] = parentBoard[filledIndex][col], \
                                                                                  parentBoard[emptyIndex][col]
                    emptyIndex -= 1

    def getCurrentChildState(self, parentBoard, childState):

        row = childState[1]
        col = childState[2]
        currentFruit = parentBoard[row][col]
        boardSize = self.boardSize

        self.refreshVisitedMatrix()

        self.columnsForGravity = {}
        self.pickFruit(parentBoard, row, col, currentFruit, boardSize)

        self.applyGravity(parentBoard)

        return parentBoard

    def alphaBetaAlgo(self, depth, currentPlayerMaxBool, alpha, beta, currentBoardState, startTime, eval, depthLimit):

        self.refreshVisitedMatrix()

        # exit the program if too less time left
        if time.clock() - startTime > self.timeLeft:
            self.initSafeWriteForKill()
            self.answer = True
            return eval

        # 1. @ terminal node decided on the based of self.depthLimit
        if depth >= self.depthLimit:
            return eval

        validNextMoves = self.ProcessCurrentBoardSate(self.boardSize, currentBoardState)

        if depth == 1 and len(validNextMoves) <= 70:
            self.depthLimit = 5

        if depth == 1 and len(validNextMoves) <= 200 and len(validNextMoves) > 70:
            self.depthLimit = 4

        if depth == 1 and len(validNextMoves) > 200:
            self.depthLimit = 3

        if not validNextMoves:
            return eval

        parentEval = eval

        # 2. if current player is MAX player
        if currentPlayerMaxBool:
            v = -float('inf')

            for childState in sorted(validNextMoves, key=lambda x: x[0], reverse=True):
                tempBoard = [x[:] for x in currentBoardState]
                eval = parentEval + childState[0]

                # print("===check current board")
                # self.displayBoard(tempBoard)
                # print("check end === \n")
                # print("current alpha move", childState, "MAX eval:", eval, "  Depth:", depth, "--- selecting:",
                #       childState, " o/f", sorted(validNextMoves, key=lambda x:x[0], reverse= True), " gain:", childState[0])
                v = max(v, self.alphaBetaAlgo(depth + 1, False, alpha, beta,
                                              self.getCurrentChildState(tempBoard, childState), startTime, eval,
                                              depthLimit))
                alpha = max(alpha, v)
                if alpha >= beta:
                    # print("pruned ", alpha, beta, v)
                    break
            # print("terminal Return ")
            if depth == 2:
                self.decideNextMove.append(v)
            return v

        else:
            v = float('inf')
            for childState in sorted(validNextMoves, key=lambda x: x[0], reverse=True):
                tempBoard = [x[:] for x in currentBoardState]
                eval = parentEval - childState[0]
                # print("===check current board")
                # self.displayBoard(tempBoard)
                # print("check end === \n")
                # print("current alpha move", childState, "MIN eval", eval, " DEPTH:", depth, " -selecting", childState,
                #       "o/f", sorted(validNextMoves, key=lambda x:x[0], reverse= True), " Loss:", childState[0])
                v = min(v, self.alphaBetaAlgo(depth + 1, True, alpha, beta,
                                              self.getCurrentChildState(tempBoard, childState), startTime, eval,
                                              depthLimit))
                beta = min(beta, v)
                if alpha >= beta:
                    # print("pruned ", alpha, beta, v)
                    break
            # print("terminal Return ")
            if depth == 2:
                self.decideNextMove.append(v)
            return v

    def initSafeWriteForKill(self):
        tempBoard = [x[:] for x in self.board]

        self.refreshVisitedMatrix()
        validNextMoves = sorted(self.ProcessCurrentBoardSate(self.boardSize, tempBoard),
                                key=lambda x: x[0], reverse=True)

        if not validNextMoves:
            return

        if len(validNextMoves) == 1:
            self.getCurrentChildState(tempBoard, childState=validNextMoves[0])
            self.writeOutput(tempBoard, validNextMoves[0])
            return

        self.getCurrentChildState(tempBoard, childState=validNextMoves[0])
        self.writeOutput(tempBoard, validNextMoves[0])

    def initPlay(self, startTime):

        depth = 1
        currentPlayerMaxBool = True
        alpha = -float('inf')
        beta = float('inf')

        eval = 0

        if self.boardSize > 14:
            self.depthLimit = 3
        else:
            self.depthLimit = 4

        self.alphaBetaAlgo(depth, currentPlayerMaxBool, alpha, beta, self.board, startTime, eval, self.depthLimit)


def main():

    startTime = time.clock()

    fruitRash = FruitRash()
    fruitRash.readInputFile("input.txt")

    fruitRash.initPlay(startTime)

    fruitRash.refreshVisitedMatrix()

    validNextMoves = sorted(fruitRash.ProcessCurrentBoardSate(fruitRash.boardSize, fruitRash.board), key=lambda x: x[0],
                            reverse=True)

    if not validNextMoves:
        return

    if not fruitRash.answer:

        if len(validNextMoves) == 1:
            fruitRash.getCurrentChildState(fruitRash.board, childState=validNextMoves[0])
            fruitRash.writeOutput(fruitRash.board, validNextMoves[0])

            #print("total time taken", round(time.clock() - startTime, 4), "seconds", "  score = ", validNextMoves[0][0])
            return

        nextMove = validNextMoves[fruitRash.decideNextMove.index(max(fruitRash.decideNextMove))]

        fruitRash.getCurrentChildState(fruitRash.board, childState=nextMove)

        fruitRash.writeOutput(fruitRash.board, nextMove)

        #print("Branching factor:", len(validNextMoves), "   Depth Limit:", fruitRash.depthLimit, "   Score:", nextMove[0])
        #print("total time taken", round(time.clock() - startTime, 4), "seconds")


if __name__ == '__main__':
    main()

