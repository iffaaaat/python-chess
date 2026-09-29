import pygame as p
import ChessEngine
import AiMoves
import ChessUI

from multiprocessing import Process, Queue
import random


MAX_FPS = 15


# ---------------------------------------------------------
# Main game
# ---------------------------------------------------------

def main():

    p.init()

    screen = p.display.set_mode(
    (
        ChessUI.BOARD_WIDTH + ChessUI.MOVE_LOG_PANEL_WIDTH, ChessUI.BOARD_HEIGHT
    )
)

    p.display.set_caption("Python Chess")

    clock = p.time.Clock()

    screen.fill(p.Color('white'))

    moveLogFont = p.font.SysFont('Arial', 14, False, False)

    # Load chess images before menus
    ChessUI.loadImages()

    # -----------------------------------------------------
    # Start menu
    # -----------------------------------------------------

    menuResult = ChessUI.startMenu(screen)

    if menuResult is None:
        return

    gameMode, aiDepth = menuResult

    if aiDepth == 2:
        aiQDepth = 1

    elif aiDepth == 3:
        aiQDepth = 3

    elif aiDepth == 4:
        aiQDepth = 2

    # -----------------------------------------------------
    # Decide human / AI players
    # -----------------------------------------------------

    if gameMode == "pvp":

        playerOne = True
        playerTwo = True

        boardFlipped = False


    elif gameMode == "pvai":

        humanIsWhite = random.choice([True, False])

        if humanIsWhite:

            playerOne = True
            playerTwo = False

            boardFlipped = False

            print("You are playing White")

        else:

            playerOne = False
            playerTwo = True

            boardFlipped = True

            print("You are playing Black")

    # -----------------------------------------------------
    # Game state
    # -----------------------------------------------------

    gs = ChessEngine.GameState()

    validMoves = gs.getValidMoves()

    moveMade = False
    animate = False

    running = True

    sqSelected = ()

    playerClick = []

    gameOver = False

    AIThinking = False

    moveFinderProcess = None

    moveUndone = False

    # -----------------------------------------------------
    # Main game loop
    # -----------------------------------------------------

    while running:

        humanTurn = (
            (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo))

        # -------------------------------------------------
        # Events
        # -------------------------------------------------

        for event in p.event.get():

            if event.type == p.QUIT:
                running = False

            # ---------------------------------------------
            # Mouse input
            # ---------------------------------------------

            elif event.type == p.MOUSEBUTTONDOWN:

                if not gameOver:

                    location = p.mouse.get_pos()
                    displayCol = (location[0] // ChessUI.SQ_SIZE)
                    displayRow = (location[1] //ChessUI.SQ_SIZE)

                    if displayCol >= 8:

                        sqSelected = ()
                        playerClick = []

                    else:

                        if boardFlipped:

                            row = 7 - displayRow
                            col = 7 - displayCol

                        else:

                            row = displayRow
                            col = displayCol

                        if sqSelected == (row, col):

                            sqSelected = ()
                            playerClick = []

                        else:

                            sqSelected = (row, col)
                            playerClick.append(sqSelected)

                    # -------------------------------------
                    # Player has clicked two squares
                    # -------------------------------------

                    if (len(playerClick) == 2 and humanTurn):

                        move = ChessEngine.Move(
                            playerClick[0], playerClick[1], gs.board)

                        for i in range(len(validMoves)):

                            if move == validMoves[i]:

                                chosenMove = (validMoves[i])

                                print(chosenMove.getChessNotation())

                                # -------------------------
                                # Pawn promotion
                                # -------------------------

                                if chosenMove.isPawnPromotion:

                                    color = (chosenMove.pieceMoved[0])

                                    chosenMove.promotionChoice = ChessUI.getPromotionChoice(
                                        screen,
                                        color
                                    )

                                gs.makeMove(chosenMove)

                                moveMade = True
                                animate = True

                                sqSelected = ()
                                playerClick = []

                                break

                        if not moveMade:

                            playerClick = [sqSelected]

            # ---------------------------------------------
            # Keyboard input
            # ---------------------------------------------

            elif event.type == p.KEYDOWN:

                # Undo move
                if event.key == p.K_z:

                    # ---------------------------------------------
                    # PvAI undo
                    # ---------------------------------------------
                    if gameMode == "pvai":

                        if AIThinking:

                            if moveFinderProcess is not None:
                                moveFinderProcess.terminate()

                            AIThinking = False

                            # Undo only the player's move
                            if len(gs.moveLog) > 0:
                                gs.undoMove()

                        else:

                            if len(gs.moveLog) > 0:
                                gs.undoMove()

                            if len(gs.moveLog) > 0:
                                gs.undoMove()

                    # ---------------------------------------------
                    # PvP undo
                    # ---------------------------------------------
                    else:

                        if len(gs.moveLog) > 0:
                            gs.undoMove()

                    moveMade = True
                    animate = False
                    gameOver = False
                    moveUndone = True

                # Restart game
                if event.key == p.K_ESCAPE:

                    gs = ChessEngine.GameState()

                    validMoves = (gs.getValidMoves())

                    sqSelected = ()
                    playerClick = []

                    moveMade = False
                    animate = False
                    gameOver = False

                    if AIThinking:
                        if (moveFinderProcess is not None):
                            moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = False

        # -------------------------------------------------
        # AI move
        # -------------------------------------------------

        if (not gameOver and not humanTurn and not moveUndone):

            if not AIThinking:

                AIThinking = True
                returnQueue = Queue()
                moveFinderProcess = Process(
                    target=AiMoves.findBestMove,
                    args=(
                        gs,
                        validMoves,
                        returnQueue,
                        aiDepth,
                        aiQDepth
                    )
                )

                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():

                AIMove = returnQueue.get()

                if AIMove is None:

                    AIMove = (AiMoves.findRandomMove(validMoves))

                gs.makeMove(AIMove)

                moveMade = True
                animate = True

                AIThinking = False

        # -------------------------------------------------
        # Update after move
        # -------------------------------------------------

        if moveMade:

            if animate:

                ChessUI.animateMove(
                    gs.moveLog[-1],
                    screen,
                    gs.board,
                    clock,
                    boardFlipped
                )

            validMoves = (gs.getValidMoves())

            moveMade = False
            animate = False
            moveUndone = False

        # -------------------------------------------------
        # Draw board
        # -------------------------------------------------

        ChessUI.drawGameState(
            screen,
            gs,
            validMoves,
            sqSelected,
            moveLogFont,
            boardFlipped
        )

        # -------------------------------------------------
        # Game over
        # -------------------------------------------------

        if gs.checkMate:

            gameOver = True

            if gs.whiteToMove:
                ChessUI.drawEndGameText(screen, "BLACK WINS BY CHECKMATE!")
            else:
                ChessUI.drawEndGameText(screen, "WHITE WINS BY CHECKMATE!")

        elif gs.staleMate:

            gameOver = True

            ChessUI.drawEndGameText(screen, "DRAW BY STALEMATE!")


        elif gs.isInsufficientMaterial():

            gameOver = True

            ChessUI.drawEndGameText(screen, "DRAW - INSUFFICIENT MATERIAL!")


        elif gs.drawByRepetition:

            gameOver = True

            ChessUI.drawEndGameText(screen,"DRAW BY REPETITION!")

        clock.tick(MAX_FPS)

        p.display.flip()

    p.quit()


if __name__ == '__main__':
    main()