from cards import create_board

def initialize_game(size=4):
    """Initialisiert das Spiel"""
    board = create_board(size)
    revealed = [[False] * size for _ in range(size)]
    return board, revealed

def is_match(board, x1, y1, x2, y2):
    """Prüft, ob zwei Karten übereinstimmen"""
    return board[x1][y1] == board[x2][y2]

def reveal_card(revealed, x, y):
    """Deckt eine Karte auf"""
    revealed[x][y] = True

def hide_cards(revealed, x1, y1, x2, y2):
    """Versteckt zwei Karten wieder"""
    revealed[x1][y1] = False
    revealed[x2][y2] = False
