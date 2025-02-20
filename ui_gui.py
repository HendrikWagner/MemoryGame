# ui_gui.py

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from memory import initialize_game, is_match, reveal_card, hide_cards

def run_gui():
    # SPIELGRÖSSE
    size = 4  # 4x4 Spielfeld
    board, revealed = initialize_game(size)
    remaining_pairs = (size * size) // 2

    # GUI-FENSTER ERSTELLEN
    root = tk.Tk()
    root.title("Memory-Spiel")

    # ABSOLUTER PFAD ZUM BILDER-ORDNER
    base_path = os.getcwd()  # Holt das aktuelle Arbeitsverzeichnis
    image_folder = os.path.join(base_path, "assets/resized")  # Absolute Pfadangabe

    # Rückseiten-Bild für verdeckte Karten
    backside_image = ImageTk.PhotoImage(
        Image.open(os.path.join(image_folder, "back.jpeg")).resize((150, 150))
    )

    # Lade Frontbilder anhand der Nummern im Spielbrett
    # Da board Werte von 1 bis remaining_pairs liefert und die Dateien von image0.jpeg bis image7.jpeg heißen,
    # wird hier 1 von der Nummer abgezogen.
    card_images = {}
    for num in range(1, remaining_pairs + 1):
        path = os.path.join(image_folder, f"image{num - 1}.jpeg")
        card_images[num] = ImageTk.PhotoImage(
            Image.open(path).resize((150, 150))
        )

    # SPIEL-LOGIK in der GUI
    buttons = []
    selected = []

    def on_click(x, y):
        nonlocal selected, remaining_pairs
        # Verhindere Klicks auf bereits aufgedeckte Karten oder wenn schon zwei Karten ausgewählt wurden
        if revealed[x][y] or len(selected) == 2:
            return

        # Karte aufdecken
        reveal_card(revealed, x, y)
        # Bild basierend auf der Nummer im board laden
        buttons[x][y].config(image=card_images[board[x][y]])
        selected.append((x, y))

        if len(selected) == 2:
            root.after(1000, check_match)  # Nach 1 Sekunde prüfen

    def check_match():
        nonlocal selected, remaining_pairs
        x1, y1 = selected[0]
        x2, y2 = selected[1]

        if is_match(board, x1, y1, x2, y2):
            # Korrektes Paar – dauerhaft aufgedeckt lassen
            remaining_pairs -= 1
            if remaining_pairs == 0:
                messagebox.showinfo("Gewonnen!", "Du hast alle Paare gefunden!")
        else:
            # Falsches Paar – wieder verdecken
            hide_cards(revealed, x1, y1, x2, y2)
            buttons[x1][y1].config(image=backside_image)
            buttons[x2][y2].config(image=backside_image)

        selected.clear()  # Auswahl zurücksetzen

    # Erstelle das Button-Gitter für das Spielfeld
    for i in range(size):
        row = []
        for j in range(size):
            btn = tk.Button(root, image=backside_image, command=lambda i=i, j=j: on_click(i, j))
            btn.grid(row=i, column=j, padx=5, pady=5)
            row.append(btn)
        buttons.append(row)

    root.mainloop()
