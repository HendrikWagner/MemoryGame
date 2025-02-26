from memory import initialize_game, is_match, reveal_card, hide_cards
from ui import print_board, get_coordinates
#from ui_gui import run_gui
from ui_gui_kivy import run_gui_kivy


def play_game(size=4):
    """Memory-Spiel starten"""
    board, revealed = initialize_game(size)
    remaining_pairs = (size * size) // 2

    while remaining_pairs > 0:
        print_board(board, revealed)
        
        x1, y1 = get_coordinates(size)
        x2, y2 = get_coordinates(size)

        if (x1, y1) == (x2, y2):
            print("Du kannst nicht zweimal dieselbe Karte wählen!")
            continue

        # Karten aufdecken
        reveal_card(revealed, x1, y1)
        reveal_card(revealed, x2, y2)
        print_board(board, revealed)

        # Prüfen, ob die Karten übereinstimmen
        if is_match(board, x1, y1, x2, y2):
            print("Paar gefunden!")
            remaining_pairs -= 1
        else:
            print("Kein Paar! Karten werden wieder verdeckt.")
            hide_cards(revealed, x1, y1, x2, y2)
        
    print("Glückwunsch! Du hast alle Paare gefunden!")

#if __name__ == "__main__":
#    play_game()

# if __name__ == '__main__':
#     run_gui()

if __name__ == '__main__':
         run_gui_kivy()
