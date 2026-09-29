class GameState():

    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunction = {'p': self.getPawnMoves, 'R': self.getRookMoves,
                             'N': self.getKnightMoves, 'B': self.getBishopMoves,
                             'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        self.enpassantPossibleLog =[self.enpassantPossible]
        self.currentCastlingRight = CastleRight(True, True, True, True)
        self.castleRightsLog = [CastleRight(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        self.drawByRepetition = False

        self.positionCounts = {}
        self.positionLog = []

        initialPosition = self.getPositionKey()

        self.positionCounts[initialPosition] = 1
        self.positionLog.append(initialPosition)

    def makeMove(self, move):

        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = (
                move.pieceMoved[0] + move.promotionChoice
            )

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'

        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  #kingside castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'

            else:  #queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        self.enpassantPossibleLog.append(self.enpassantPossible)

        self.updateCastleRight(move)
        self.castleRightsLog.append(CastleRight(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        self.updatePositionHistory()

    def undoMove(self):

        if len(self.moveLog) != 0:

            # Undo repetition tracking first
            if len(self.positionLog) > 1:
                currentPosition = self.positionLog.pop()

                self.positionCounts[currentPosition] -= 1

                if self.positionCounts[currentPosition] == 0:
                    del self.positionCounts[currentPosition]

            move = self.moveLog.pop()

            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured

            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)

            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            self.castleRightsLog.pop()

            newRights = self.castleRightsLog[-1]

            self.currentCastlingRight = CastleRight(
                newRights.wks,
                newRights.bks,
                newRights.wqs,
                newRights.bqs
            )

            if move.isCastleMove:

                if move.endCol - move.startCol == 2:

                    self.board[move.endRow][move.endCol + 1] = \
                        self.board[move.endRow][move.endCol - 1]

                    self.board[move.endRow][move.endCol - 1] = '--'

                else:

                    self.board[move.endRow][move.endCol - 2] = \
                        self.board[move.endRow][move.endCol + 1]

                    self.board[move.endRow][move.endCol + 1] = '--'

            self.checkMate = False
            self.staleMate = False

            # Restore repetition state
            currentPosition = self.getPositionKey()

            self.drawByRepetition = (
                self.positionCounts.get(currentPosition, 0) >= 3
            )

    def updateCastleRight(self, move):
        # If a king moves, both castling rights are lost
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False

        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False

        # If a rook moves from its original square,
        # disable the corresponding castling side
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False

        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

        # If a rook gets captured on its original square,
        # that side can no longer castle
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False

        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    def getValidMoves(self):

        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRight(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                       self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = self.getAllPossibleMoves()

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    def inCheck(self):

        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):

        enemyColor = "b" if self.whiteToMove else "w"

        # -----------------------
        # Pawn attacks
        # -----------------------

        if enemyColor == "b":
            pawnRow = r - 1

            if pawnRow >= 0:
                if c - 1 >= 0 and self.board[pawnRow][c - 1] == "bp":
                    return True

                if c + 1 < 8 and self.board[pawnRow][c + 1] == "bp":
                    return True

        else:
            pawnRow = r + 1

            if pawnRow < 8:
                if c - 1 >= 0 and self.board[pawnRow][c - 1] == "wp":
                    return True

                if c + 1 < 8 and self.board[pawnRow][c + 1] == "wp":
                    return True


        # -----------------------
        # Knight attacks
        # -----------------------

        knightMoves = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1)
        )

        for dr, dc in knightMoves:

            endRow = r + dr
            endCol = c + dc

            if 0 <= endRow < 8 and 0 <= endCol < 8:

                if self.board[endRow][endCol] == enemyColor + "N":
                    return True


        # -----------------------
        # Rook / Queen attacks
        # -----------------------

        straightDirections = (
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        )

        for dr, dc in straightDirections:

            for distance in range(1, 8):

                endRow = r + dr * distance
                endCol = c + dc * distance

                if not (0 <= endRow < 8 and 0 <= endCol < 8):
                    break

                piece = self.board[endRow][endCol]

                if piece == "--":
                    continue

                if piece[0] == enemyColor and piece[1] in ("R", "Q"):
                    return True

                break


        # -----------------------
        # Bishop / Queen attacks
        # -----------------------

        diagonalDirections = (
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1)
        )

        for dr, dc in diagonalDirections:

            for distance in range(1, 8):

                endRow = r + dr * distance
                endCol = c + dc * distance

                if not (0 <= endRow < 8 and 0 <= endCol < 8):
                    break

                piece = self.board[endRow][endCol]

                if piece == "--":
                    continue

                if piece[0] == enemyColor and piece[1] in ("B", "Q"):
                    return True

                break


        # -----------------------
        # King attacks
        # -----------------------

        kingMoves = (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1)
        )

        for dr, dc in kingMoves:

            endRow = r + dr
            endCol = c + dc

            if 0 <= endRow < 8 and 0 <= endCol < 8:

                if self.board[endRow][endCol] == enemyColor + "K":
                    return True

        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):

        if self.whiteToMove:
            if self.board[r - 1][c] == '--':  #1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':  #2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0:  #capture to the left
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))

            if c + 1 <= 7:  #capture to the right
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:
            if self.board[r + 1][c] == '--':  #1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':  #2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:  #capture to the left
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))

            if c + 1 <= 7:  #capture to the right
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):

        direction = ((-1, 0), (1, 0), (0, -1), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):

        direction = ((-1, -1), (1, 1), (1, -1), (-1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):

        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):

        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1), (0, -1), (0, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def isInsufficientMaterial(self):

        minorPieces = []

        for row in range(8):
            for col in range(8):

                piece = self.board[row][col]

                if piece == "--" or piece[1] == "K":
                    continue

                # If any pawn, rook or queen exists,
                # there is enough material to potentially mate.
                if piece[1] in ("p", "R", "Q"):
                    return False

                # Save bishops and knights
                minorPieces.append(
                    (piece, row, col)
                )

        # King vs King
        if len(minorPieces) == 0:
            return True

        # King + Bishop vs King
        # King + Knight vs King
        if len(minorPieces) == 1:
            return minorPieces[0][0][1] in ("B", "N")

        # Only bishops remain
        if all(piece[0][1] == "B" for piece in minorPieces):

            bishopSquareColors = []

            for piece, row, col in minorPieces:
                squareColor = (row + col) % 2
                bishopSquareColors.append(squareColor)

            # All bishops operate on the same colour squares
            if len(set(bishopSquareColors)) == 1:
                return True

        return False

    def getPositionKey(self):

        boardState = tuple(
            tuple(row)
            for row in self.board
        )

        castlingState = (
            self.currentCastlingRight.wks,
            self.currentCastlingRight.wqs,
            self.currentCastlingRight.bks,
            self.currentCastlingRight.bqs
        )

        return (
            boardState,
            self.whiteToMove,
            castlingState,
            self.enpassantPossible
        )

    def updatePositionHistory(self):

        position = self.getPositionKey()

        self.positionLog.append(position)

        self.positionCounts[position] = (
            self.positionCounts.get(position, 0) + 1
        )

        if self.positionCounts[position] >= 3:
            self.drawByRepetition = True

class CastleRight():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.promotionChoice = "Q"
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
                self.pieceMoved == 'bp' and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    #overriding the str() function
    def __str__(self):

        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare


if __name__ == "__main__":
    gs = GameState()

    print("Initial draw:", gs.drawByRepetition)

    for i in range(10):
        gs.getValidMoves()

        print(
            "Call",
            i + 1,
            "- Draw:",
            gs.drawByRepetition
        )