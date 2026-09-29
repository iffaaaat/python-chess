import pygame as p


BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
CAPTURE_PANEL_HEIGHT = 150

DIMENSIONS = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSIONS

IMAGES = {}

COLORS = [p.Color("white"), p.Color("gray")]


def loadImages():

    pieces = [
        'wp', 'wR', 'wN', 'wB', 'wQ', 'wK',
        'bp', 'bR', 'bN', 'bB', 'bQ', 'bK'
    ]

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("ChessImage/" + piece + ".png"),
            (SQ_SIZE, SQ_SIZE)
        )


# ---------------------------------------------------------
# Pawn promotion menu
# ---------------------------------------------------------

def getPromotionChoice(screen, color):

    choices = ["Q", "R", "B", "N"]

    menu_width = SQ_SIZE * 4
    menu_height = SQ_SIZE

    x = (BOARD_WIDTH - menu_width) // 2
    y = (BOARD_HEIGHT - menu_height) // 2

    while True:

        p.draw.rect(screen, p.Color("white"), (x, y, menu_width, menu_height))

        p.draw.rect(screen, p.Color("black"), (x, y, menu_width, menu_height), 2)

        for index, piece in enumerate(choices):

            piece_code = color + piece
            piece_x = x + index * SQ_SIZE

            screen.blit(
                IMAGES[piece_code],
                p.Rect(piece_x, y, SQ_SIZE, SQ_SIZE)
            )

        p.display.flip()

        for event in p.event.get():

            if event.type == p.QUIT:
                return "Q"

            if event.type == p.MOUSEBUTTONDOWN:

                mouse_x, mouse_y = p.mouse.get_pos()

                if (
                    x <= mouse_x < x + menu_width
                    and
                    y <= mouse_y < y + menu_height
                ):

                    selected_index = (
                        mouse_x - x
                    ) // SQ_SIZE

                    return choices[selected_index]


# ---------------------------------------------------------
# Menu button
# ---------------------------------------------------------

def drawButton(screen, text, x, y, width, height, font):

    button_rect = p.Rect(x, y, width, height)

    p.draw.rect(screen, p.Color("lightgray"), button_rect)

    p.draw.rect( screen, p.Color("black"), button_rect, 2)

    text_surface = font.render(text, True, p.Color("black"))

    text_rect = text_surface.get_rect( center=button_rect.center)

    screen.blit(text_surface, text_rect)

    return button_rect


# ---------------------------------------------------------
# AI difficulty menu
# ---------------------------------------------------------

def difficultyMenu(screen):

    font_title = p.font.SysFont("Arial", 36, True)

    font_button = p.font.SysFont("Arial", 24)

    while True:

        screen.fill(p.Color("white"))

        title = font_title.render(
            "Choose Difficulty",
            True,
            p.Color("black")
        )

        title_rect = title.get_rect(
            center=(
                BOARD_WIDTH // 2,
                80
            )
        )

        screen.blit(title, title_rect)

        easy_button = drawButton(
            screen,
            "Easy",
            120,
            150,
            270,
            60,
            font_button
        )

        medium_button = drawButton(
            screen,
            "Medium",
            120,
            230,
            270,
            60,
            font_button
        )

        hard_button = drawButton(
            screen,
            "Hard",
            120,
            310,
            270,
            60,
            font_button
        )

        p.display.flip()

        for event in p.event.get():

            if event.type == p.QUIT:
                return None

            if event.type == p.MOUSEBUTTONDOWN:

                mouse_pos = p.mouse.get_pos()

                # Easy = depth 2
                if easy_button.collidepoint(mouse_pos):
                    return 2

                # Medium = depth 3
                if medium_button.collidepoint(mouse_pos):
                    return 3

                # Hard = depth 4
                if hard_button.collidepoint(mouse_pos):
                    return 4


# ---------------------------------------------------------
# Start menu
# ---------------------------------------------------------

def startMenu(screen):

    font_title = p.font.SysFont("Arial", 40, True)

    font_button = p.font.SysFont( "Arial", 24)

    while True:

        screen.fill(p.Color("white"))

        title = font_title.render(
            "CHESS",
            True,
            p.Color("black")
        )

        title_rect = title.get_rect(
            center=(BOARD_WIDTH // 2, 80)
        )

        screen.blit(title, title_rect)

        pvp_button = drawButton(
            screen,
            "Player vs Player",
            120,
            160,
            270,
            60,
            font_button
        )

        pvai_button = drawButton(
            screen,
            "Player vs AI",
            120,
            250,
            270,
            60,
            font_button
        )

        p.display.flip()

        for event in p.event.get():

            if event.type == p.QUIT:
                return None

            if event.type == p.MOUSEBUTTONDOWN:

                mouse_pos = p.mouse.get_pos()

                # Player vs Player
                if pvp_button.collidepoint(mouse_pos):
                    return "pvp", None

                # Player vs AI
                if pvai_button.collidepoint(mouse_pos):

                    difficulty = difficultyMenu(screen)

                    if difficulty is None:
                        return None

                    return "pvai", difficulty


def toDisplayCoords(r, c, boardFlipped):
    if boardFlipped:
        return 7 - r, 7 - c
    return r, c


# ---------------------------------------------------------
# Draw game state
# ---------------------------------------------------------

def drawGameState(
    screen,
    gs,
    validMoves,
    sqSelected,
    moveLogFont,
    boardFlipped
):

    drawBoard(screen)

    highlightSquares(
        screen,
        gs,
        validMoves,
        sqSelected,
        boardFlipped
    )

    drawPieces(
        screen,
        gs.board,
        boardFlipped
    )

    drawMoveLog(
        screen,
        gs,
        moveLogFont
    )

    drawCapturedPieces(
        screen,
        gs,
        moveLogFont
    )


# ---------------------------------------------------------
# Draw chess board
# ---------------------------------------------------------

def drawBoard(screen):

    for r in range(DIMENSIONS):

        for c in range(DIMENSIONS):

            color = COLORS[(r + c) % 2]

            p.draw.rect(
                screen,
                color,
                p.Rect(
                    c * SQ_SIZE,
                    r * SQ_SIZE,
                    SQ_SIZE,
                    SQ_SIZE
                )
            )

# ---------------------------------------------------------
# Highlight selected piece / legal moves
# ---------------------------------------------------------

def highlightSquares(
    screen,
    gs,
    validMoves,
    sqSelected,
    boardFlipped
):

    if sqSelected != ():

        r, c = sqSelected

        if (gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b')):

            s = p.Surface((SQ_SIZE, SQ_SIZE))

            s.set_alpha(100)

            s.fill(p.Color('blue'))

            drawRow, drawCol = toDisplayCoords(
                r,
                c,
                boardFlipped
            )

            screen.blit(
                s,
                (
                    drawCol * SQ_SIZE,
                    drawRow * SQ_SIZE
                )
            )

            s.fill(p.Color('yellow'))

            for move in validMoves:

                if (
                    move.startRow == r
                    and
                    move.startCol == c
                ):

                    endDrawRow, endDrawCol = toDisplayCoords(
                        move.endRow,
                        move.endCol,
                        boardFlipped
                    )

                    screen.blit(
                        s,
                        (
                            endDrawCol * SQ_SIZE,
                            endDrawRow * SQ_SIZE
                        )
                    )


# ---------------------------------------------------------
# Draw pieces
# ---------------------------------------------------------

def drawPieces(screen, board, boardFlipped):

    for r in range(DIMENSIONS):

        for c in range(DIMENSIONS):

            piece = board[r][c]

            if piece != "--":

                drawRow, drawCol = toDisplayCoords(
                    r,
                    c,
                    boardFlipped
                )

                screen.blit(
                    IMAGES[piece],

                    p.Rect(
                        drawCol * SQ_SIZE,
                        drawRow * SQ_SIZE,
                        SQ_SIZE,
                        SQ_SIZE
                    )
                )


# ---------------------------------------------------------
# Move log
# ---------------------------------------------------------

def drawMoveLog(screen, gs, font
):

    moveLogRect = p.Rect(
        BOARD_WIDTH,
        0,
        MOVE_LOG_PANEL_WIDTH,
        MOVE_LOG_PANEL_HEIGHT
    )

    p.draw.rect(screen, p.Color('black'), moveLogRect)

    moveLog = gs.moveLog
    moveText = []

    for i in range(0, len(moveLog), 2):

        moveString = (
            str(i // 2 + 1)
            + ". "
            + str(moveLog[i])
            + " "
        )

        if i + 1 < len(moveLog):

            moveString += (
                str(moveLog[i + 1])
                + "  "
            )

        moveText.append(moveString)

    movesPerRow = 3
    padding = 5
    textY = padding
    lineSpacing = 2

    for i in range(0, len(moveText), movesPerRow):

        text = ""

        for j in range(movesPerRow):

            if (i + j < len(moveText)):

                text += (moveText[i + j])

        textObject = font.render(
            text,
            True,
            p.Color('White')
        )

        textLocation = (
            moveLogRect.move(padding, textY)
        )

        maxMoveLogY = (
            MOVE_LOG_PANEL_HEIGHT
            -
            CAPTURE_PANEL_HEIGHT
            -
            padding
        )

        if (textY + textObject.get_height() > maxMoveLogY):
            break

        screen.blit(textObject, textLocation)

        textY += (textObject.get_height() + lineSpacing)


def drawCapturedPieces(screen, gs, font):

    panelY = (MOVE_LOG_PANEL_HEIGHT - CAPTURE_PANEL_HEIGHT)

    panelRect = p.Rect(
        BOARD_WIDTH,
        panelY,
        MOVE_LOG_PANEL_WIDTH,
        CAPTURE_PANEL_HEIGHT
    )

    # Background
    p.draw.rect(screen, p.Color("lightgray"), panelRect)

    # Divider line
    p.draw.line(screen, p.Color("gray"), (BOARD_WIDTH, panelY),
        (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, panelY),
        2
    )

    # -----------------------------------------------------
    # Determine captured pieces
    # -----------------------------------------------------

    whiteCaptured = []
    blackCaptured = []

    for move in gs.moveLog:

        capturedPiece = move.pieceCaptured

        if capturedPiece == "--":
            continue

        if capturedPiece[0] == "b":
            whiteCaptured.append(capturedPiece)

        elif capturedPiece[0] == "w":
            blackCaptured.append(capturedPiece)


    captureOrder = {
        "Q": 0,
        "R": 1,
        "B": 2,
        "N": 3,
        "p": 4
    }

    whiteCaptured.sort(key=lambda piece: captureOrder[piece[1]])

    blackCaptured.sort(key=lambda piece: captureOrder[piece[1]])

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    title = font.render("Captured Pieces", True, p.Color("black"))

    screen.blit(
        title,
        (
            BOARD_WIDTH + 5,
            panelY + 5
        )
    )

    # -----------------------------------------------------
    # Draw one player's captures
    # -----------------------------------------------------

    def drawCaptureGroup(label, pieces, startY):

        labelSurface = font.render(
            label, True, p.Color("black")
        )

        screen.blit(
            labelSurface, (BOARD_WIDTH + 5, startY)
        )

        iconSize = 22

        startX = (BOARD_WIDTH + 100)

        for index, piece in enumerate(pieces):

            row = index // 6
            col = index % 6

            image = p.transform.scale(
                IMAGES[piece],
                (
                    iconSize, iconSize
                )
            )

            screen.blit(
                image,
                (
                    startX + col * iconSize,
                    startY + row * iconSize
                )
            )

    # -----------------------------------------------------
    # White captures
    # -----------------------------------------------------

    drawCaptureGroup("White:", whiteCaptured, panelY + 32)

    # -----------------------------------------------------
    # Black captures
    # -----------------------------------------------------

    drawCaptureGroup("Black:", blackCaptured, panelY + 88)

# ---------------------------------------------------------
# Move animation
# ---------------------------------------------------------

def animateMove(move, screen, board, clock, boardFlipped):

    dR = (move.endRow - move.startRow)

    dC = (move.endCol - move.startCol)

    framesPerSquare = 7

    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):

        r = (
            move.startRow + dR * frame / frameCount
        )

        c = (
            move.startCol + dC * frame / frameCount
        )

        if boardFlipped:

            displayR = 7 - r
            displayC = 7 - c

        else:

            displayR = r
            displayC = c

        drawBoard(screen)

        drawPieces(screen, board, boardFlipped)

        color = COLORS[(move.endRow + move.endCol) % 2]

        endDrawRow, endDrawCol = toDisplayCoords(
            move.endRow,
            move.endCol,
            boardFlipped
        )

        endSquare = p.Rect(
            endDrawCol * SQ_SIZE,
            endDrawRow * SQ_SIZE,
            SQ_SIZE,
            SQ_SIZE
        )

        p.draw.rect(screen, color, endSquare)

        if (move.pieceCaptured != '--'):

            if move.isEnpassantMove:

                enPassantRow = (
                    move.endRow + 1
                    if
                    move.pieceCaptured[0]
                    ==
                    'b'
                    else
                    move.endRow - 1
                )

                captureDrawRow, captureDrawCol = toDisplayCoords(
                    enPassantRow,
                    move.endCol,
                    boardFlipped
                )

                endSquare = p.Rect(
                    captureDrawCol * SQ_SIZE,
                    captureDrawRow * SQ_SIZE,
                    SQ_SIZE,
                    SQ_SIZE
                )

            screen.blit(
                IMAGES[move.pieceCaptured],
                endSquare
            )

        screen.blit(
            IMAGES[move.pieceMoved],
            p.Rect(
                displayC * SQ_SIZE,
                displayR * SQ_SIZE,
                SQ_SIZE,
                SQ_SIZE
            )
        )

        p.display.flip()

        clock.tick(60)


# ---------------------------------------------------------
# End game text
# ---------------------------------------------------------

def drawEndGameText(screen, text):

    font = p.font.SysFont('Helvetica', 35, True, False)

    textObject = font.render(text, True, p.Color('Gray'))

    textLocation = p.Rect(
        0,
        0,
        BOARD_WIDTH,
        BOARD_HEIGHT
    ).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2,
        BOARD_HEIGHT / 2 - textObject.get_height() / 2
    )

    screen.blit(textObject, textLocation)

    textObject = font.render(text, True, p.Color('Black'))

    screen.blit(
        textObject,
        textLocation.move(
            2,
            2
        )
    )