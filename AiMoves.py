import random
import time


# =========================================================
# PIECE VALUES
# =========================================================

pieceScore = {
    "K": 0,
    "Q": 10,
    "R": 5,
    "B": 3,
    "N": 3,
    "p": 1
}


# =========================================================
# POSITIONAL SCORE TABLES
# =========================================================

knightScores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]


bishopScores = [
    [2, 1, 1, 1, 1, 1, 1, 2],
    [2, 3, 2, 2, 2, 2, 3, 2],
    [3, 3, 3, 3, 3, 3, 3, 3],
    [2, 3, 3, 4, 4, 3, 3, 2],
    [2, 3, 3, 4, 4, 3, 3, 2],
    [3, 3, 3, 3, 3, 3, 3, 3],
    [2, 3, 2, 2, 2, 2, 3, 2],
    [2, 1, 1, 1, 1, 1, 1, 2]
]


queenScores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [2, 2, 2, 2, 2, 2, 2, 2],
    [2, 4, 4, 3, 3, 4, 4, 2],
    [2, 4, 4, 3, 3, 4, 4, 2],
    [2, 4, 4, 3, 3, 4, 4, 2],
    [2, 4, 4, 3, 3, 4, 4, 2],
    [2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 3, 1, 1, 1, 1]
]


rookScores = [
    [4, 2, 4, 4, 4, 4, 2, 4],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 3, 3, 4, 4, 3, 3, 1],
    [1, 2, 4, 4, 4, 4, 2, 1],
    [1, 2, 4, 4, 4, 4, 2, 1],
    [1, 3, 3, 4, 4, 3, 3, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [4, 2, 4, 4, 4, 4, 2, 4]
]


whitePawnScores = [
    [8, 8, 8, 8, 8, 8, 8, 8],
    [7, 7, 7, 8, 8, 7, 7, 7],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 7, 7, 3, 2, 1],
    [1, 1, 2, 5, 5, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0]
]


blackPawnScores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 5, 5, 2, 1, 1],
    [1, 2, 3, 7, 7, 3, 3, 1],
    [2, 3, 3, 6, 6, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [7, 7, 7, 8, 8, 7, 7, 7],
    [8, 8, 8, 8, 8, 8, 8, 8]
]


kingScores = [
    [4, 5, 4, 3, 3, 4, 5, 4],
    [1, 3, 2, 1, 1, 2, 3, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 2, 1, 1, 2, 3, 1],
    [4, 5, 4, 3, 3, 4, 5, 4]
]


piecePositionalScores = {
    "N": knightScores,
    "B": bishopScores,
    "Q": queenScores,
    "R": rookScores,
    "wp": whitePawnScores,
    "bp": blackPawnScores,
    "K": kingScores
}


# =========================================================
# SEARCH CONSTANTS
# =========================================================

CHECKMATE = 1000
STALEMATE = 0

# =========================================================
# TRANSPOSITION TABLE FLAGS
# =========================================================

TT_EXACT = 0
TT_LOWERBOUND = 1
TT_UPPERBOUND = 2


# =========================================================
# GLOBAL SEARCH STATE
# =========================================================

transpositionTable = {}

moveGenerationTime = 0

nextMove = None
counter = 0

ttHits = 0
ttStores = 0

rootMoveScores = []

# =========================================================
# RANDOM FALLBACK MOVE
# =========================================================

def findRandomMove(validMoves):

    return validMoves[
        random.randint(
            0,
            len(validMoves) - 1
        )
    ]


# =========================================================
# MOVE ORDERING
# =========================================================

def scoreMove(move):

    score = 0

    if move.isPawnPromotion:
        score += 100

    if move.pieceCaptured != "--":

        victim = pieceScore[move.pieceCaptured[1]]

        attacker = pieceScore[move.pieceMoved[1]]

        score += (10 * victim - attacker)

    if move.isCastleMove:
        score += 1

    return score


def scoreOpeningMove(gs, move):

    if len(gs.moveLog) >= 8:
        return 0

    bonus = 0
    piece = move.pieceMoved
    pieceType = piece[1]
    color = piece[0]

    # -----------------------------------------------------
    # 1. Encourage central pawn occupation
    # -----------------------------------------------------

    if pieceType == "p":

        if move.endCol in (3, 4):

            if color == "w" and move.endRow in (4, 5):
                bonus += 0.25

            elif color == "b" and move.endRow in (2, 3):
                bonus += 0.25

        if move.startCol in (0, 7):
            bonus -= 0.25


    # -----------------------------------------------------
    # 2. Encourage knight development
    # -----------------------------------------------------

    elif pieceType == "N":

        whiteKnightStarts = {(7, 1), (7, 6)}

        blackKnightStarts = {(0, 1), (0, 6)}

        if (color == "w" and (move.startRow, move.startCol) in whiteKnightStarts):
            bonus += 0.25

        elif (color == "b" and (move.startRow, move.startCol) in blackKnightStarts):
            bonus += 0.25

        if move.endCol in (0, 7):
            bonus -= 0.80


    # -----------------------------------------------------
    # 3. Encourage bishop development
    # -----------------------------------------------------

    elif pieceType == "B":

        whiteBishopStarts = {(7, 2), (7, 5)}

        blackBishopStarts = {(0, 2), (0, 5)}

        if (color == "w" and (move.startRow, move.startCol) in whiteBishopStarts):
            bonus += 0.20

        elif (color == "b" and (move.startRow, move.startCol) in blackBishopStarts):
            bonus += 0.20

    # -----------------------------------------------------
    # 4. Encourage castling
    # -----------------------------------------------------

    if move.isCastleMove:
        bonus += 0.30

    # -----------------------------------------------------
    # 5. Discourage early queen adventures
    # -----------------------------------------------------

    if pieceType == "Q" and len(gs.moveLog) < 6:
        bonus -= 0.20

    # -----------------------------------------------------
    # 6. Discourage moving the same developed piece twice
    # -----------------------------------------------------

    for previousMove in gs.moveLog:

        if (
            previousMove.pieceMoved[0] == color
            and
            previousMove.endRow == move.startRow
            and
            previousMove.endCol == move.startCol
        ):

            bonus -= 0.15
            break

    return bonus


def orderMoves(validMoves):

    return sorted(validMoves, key=scoreMove, reverse=True)


# =========================================================
# MAIN AI ENTRY POINT
# =========================================================

def findBestMove(gs, validMoves, returnQueue, depth, qDepth):

    global nextMove
    global counter
    global moveGenerationTime

    global transpositionTable
    global ttHits
    global ttStores
    global rootMoveScores

    nextMove = None

    counter = 0

    moveGenerationTime = 0

    ttHits = 0
    ttStores = 0
    rootMoveScores = []

    transpositionTable = {}

    validMoves = orderMoves(validMoves)

    start_time = time.perf_counter()

    findMoveNegaMaxAlphaBeta(gs, validMoves, depth, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1, depth,qDepth)

    # ---------------------------------------------------------
    # Opening move selection
    # ---------------------------------------------------------

    OPENING_PLIES = 8

    if (len(gs.moveLog) < OPENING_PLIES and rootMoveScores):

        bestScore = max(score for move, score in rootMoveScores)

        # ---------------------------------------------
        # Difficulty-specific tolerance
        # ---------------------------------------------

        if depth == 2:
            scoreMargin = 0.30

        elif depth == 3:
            scoreMargin = 0.10

        else:
            scoreMargin = 0.05

        closeMoves = [
            (move, score)
            for move, score in rootMoveScores
            if score >= bestScore - scoreMargin
        ]

        if depth >= 4:

            nextMove = max(
                closeMoves,
                key=lambda item:
                    item[1] + scoreOpeningMove(gs, item[0])
            )[0]

        elif len(closeMoves) > 1:

            nextMove = random.choice(
                [
                    move
                    for move, score in closeMoves
                ]
            )

    elapsed = (time.perf_counter() - start_time)

    print("Nodes searched:", counter)

    print("TT hits:", ttHits)

    print("TT stores:", ttStores)

    print(f"Move generation time: "f"{moveGenerationTime:.3f} seconds")

    print(f"Total search time: "f"{elapsed:.3f} seconds")

    returnQueue.put(nextMove)


# =========================================================
# QUIESCENCE SEARCH
# =========================================================

def quiescenceSearch(
    gs,
    validMoves,
    alpha,
    beta,
    turnMultiplier,
    qDepth
):

    global moveGenerationTime

    if (
        gs.staleMate or gs.drawByRepetition or gs.isInsufficientMaterial()
    ):
        return STALEMATE

    # -----------------------------------------------------
    # Checkmate
    # -----------------------------------------------------

    if gs.checkMate:
        return (
            turnMultiplier
            *
            scoreBoard(gs)
        )

    inCheck = gs.inCheck()

    if not inCheck:

        standPat = (turnMultiplier * scoreBoard(gs))

        if qDepth == 0:
            return standPat

        if standPat >= beta:
            return beta

        if standPat > alpha:
            alpha = standPat

        tacticalMoves = [
            move
            for move in validMoves
            if (move.pieceCaptured != "--" or move.isPawnPromotion)
        ]
        
    else:

        if not validMoves:

            return (
                turnMultiplier * scoreBoard(gs)
            )

        tacticalMoves = validMoves

        if qDepth == 0:
            qDepth = 1

    if not tacticalMoves:
        return alpha

    tacticalMoves = orderMoves(tacticalMoves)

    for move in tacticalMoves:

        gs.makeMove(move)

        start_move_gen = (time.perf_counter())

        nextMoves = (gs.getValidMoves())

        moveGenerationTime += (time.perf_counter() - start_move_gen)

        score = -quiescenceSearch(
            gs,
            nextMoves,
            -beta,
            -alpha,
            -turnMultiplier,
            qDepth - 1
        )

        gs.undoMove()

        if score >= beta:
            return beta

        if score > alpha:
            alpha = score

    return alpha


# =========================================================
# NEGAMAX + ALPHA-BETA + TRANSPOSITION TABLE
# =========================================================

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, rootDepth, qDepth):

    global nextMove
    global counter
    global moveGenerationTime

    global transpositionTable
    global ttHits
    global ttStores
    global rootMoveScores

    counter += 1

    # -----------------------------------------------------
    # Terminal draw states
    # -----------------------------------------------------

    if (gs.staleMate or gs.drawByRepetition or gs.isInsufficientMaterial()):
        return STALEMATE

    # -----------------------------------------------------
    # Create key for current board position
    # -----------------------------------------------------

    positionKey = gs.getPositionKey()

    positionOccurrences = gs.positionCounts.get(positionKey, 0)

    useTT = positionOccurrences <= 1

    originalAlpha = alpha
    originalBeta = beta

    # -----------------------------------------------------
    # Check transposition table
    # -----------------------------------------------------

    entry = None

    if useTT:
        entry = transpositionTable.get(positionKey)

    if entry is not None:

        storedDepth = entry["depth"]
        storedScore = entry["score"]
        storedFlag = entry["flag"]

        # Only reuse a result if it was searched
        # at least as deeply as we need now
        if storedDepth >= depth:

            ttHits += 1

            if storedFlag == TT_EXACT:

                return storedScore

            elif storedFlag == TT_LOWERBOUND:

                alpha = max(alpha, storedScore)

            elif storedFlag == TT_UPPERBOUND:

                beta = min(beta, storedScore)

            # Cached bound is already enough
            # to prove a cutoff
            if alpha >= beta:

                return storedScore

    # -----------------------------------------------------
    # Leaf node
    # -----------------------------------------------------

    if depth == 0:

        return quiescenceSearch(gs, validMoves, alpha, beta, turnMultiplier, qDepth)

    if len(validMoves) == 0:

        return (turnMultiplier * scoreBoard(gs))

    maxScore = -CHECKMATE

    # -----------------------------------------------------
    # Move ordering
    # -----------------------------------------------------

    validMoves = orderMoves(validMoves)

    # -----------------------------------------------------
    # Search child positions
    # -----------------------------------------------------

    for move in validMoves:

        gs.makeMove(move)

        start_move_gen = (time.perf_counter())

        nextMoves = (gs.getValidMoves())

        moveGenerationTime += (time.perf_counter() - start_move_gen)

        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier, rootDepth, qDepth)

        gs.undoMove()

        # -------------------------------------------------
        # New best score
        # -------------------------------------------------

        if depth == rootDepth:

            rootMoveScores.append((move, score))

        if score > maxScore:

            maxScore = score

            if depth == rootDepth:
                nextMove = move

        # -------------------------------------------------
        # Alpha update
        # -------------------------------------------------

        if maxScore > alpha:

            alpha = maxScore

        # -------------------------------------------------
        # Beta cutoff
        # -------------------------------------------------

        if alpha >= beta:

            break

    # -----------------------------------------------------
    # Determine what type of result we have
    # -----------------------------------------------------

    if maxScore <= originalAlpha:

        flag = TT_UPPERBOUND

    elif maxScore >= originalBeta:

        flag = TT_LOWERBOUND

    else:

        flag = TT_EXACT

    # -----------------------------------------------------
    # Store result in transposition table
    # -----------------------------------------------------

    if useTT:

        oldEntry = transpositionTable.get(positionKey)

        if (oldEntry is None or depth >= oldEntry["depth"]):

            transpositionTable[positionKey] = {
                "depth": depth,
                "score": maxScore,
                "flag": flag
            }

            ttStores += 1

    return maxScore


# =========================================================
# BOARD EVALUATION
# =========================================================


def scoreBoard(gs):

    # -----------------------------------------------------
    # Checkmate
    # -----------------------------------------------------

    if gs.checkMate:

        if gs.whiteToMove:

            return -CHECKMATE

        else:

            return CHECKMATE

    # -----------------------------------------------------
    # Draw / stalemate
    # -----------------------------------------------------

    elif gs.staleMate:

        return STALEMATE

    elif gs.isInsufficientMaterial():

        return STALEMATE

    elif gs.drawByRepetition:

        return STALEMATE

    # -----------------------------------------------------
    # Normal board evaluation
    # -----------------------------------------------------

    score = 0

    for row in range(len(gs.board)):

        for col in range(len(gs.board[row])):

            square = (gs.board[row][col])

            if square != "--":
                piecePositionalScore = 0

                if square[1] == "p":
                    piecePositionalScore = (piecePositionalScores[square][row][col])

                else:
                    piecePositionalScore = (piecePositionalScores[square[1]][row][col])

                if square[0] == "w":
                    score += (pieceScore[square[1]] + piecePositionalScore * 0.1)

                elif square[0] == "b":
                    score -= (pieceScore[square[1]] + piecePositionalScore * 0.1)

    return score