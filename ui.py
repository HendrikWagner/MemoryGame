def print_board(board, revealed):
    """Zeigt das Spielfeld an, mit verdeckten Karten"""
    for i in range(len(board)):
        for j in range(len(board[i])):
            if revealed[i][j]:
                print(f"{board[i][j]:2}", end=" ")
            else:
                print("X ", end=" ")
        print()

def get_coordinates(size):
    """Fragt den Nutzer nach Kartenkoordinaten"""
    while True:
        try:
            x, y = map(int, input("Gib Zeile und Spalte ein (z. B. 1 2): ").split())
            if 0 <= x < size and 0 <= y < size:
                return x, y
            else:
                print("Koordinaten außerhalb des Spielfelds!")
        except ValueError:
            print("Ungültige Eingabe!")
