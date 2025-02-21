# ui_gui.py

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from memory import initialize_game, is_match, reveal_card, hide_cards
import sys, os

def resource_path(relative_path):
    """Gibt den absoluten Pfad zu einer Ressource zurück, auch wenn sie in einer PyInstaller-Exe gepackt wurde."""
    try:
        # PyInstaller erstellt einen temporären Ordner und speichert den Pfad in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.getcwd()
    return os.path.join(base_path, relative_path)

def run_gui():
    # SPIEL-FENSTER ERSTELLEN
    root = tk.Tk()
    root.title("Memory-Spiel")

    # SPIELGRÖSSE
    size = 4  # 4x4 Spielfeld
    board, revealed = initialize_game(size)
    remaining_pairs = (size * size) // 2

    # ABSOLUTER PFAD ZUM BILDER-ORDNER
    # base_path = os.getcwd()  # Holt das aktuelle Arbeitsverzeichnis
    # image_folder = os.path.join(base_path, "assets/resized")  # Absolute Pfadangabe
    image_folder = resource_path("assets/resized")


    # Rückseiten-Bild für verdeckte Karten (150x150 Pixel)
    backside_image = ImageTk.PhotoImage(
        Image.open(os.path.join(image_folder, "back.jpeg")).resize((150, 150))
    )

    # Lade Frontbilder anhand der Nummern im Spielbrett
    # Die Dateien heißen image0.jpeg bis image7.jpeg, daher wird 1 abgezogen.
    card_images = {}
    for num in range(1, remaining_pairs + 1):
        path = os.path.join(image_folder, f"image{num - 1}.jpeg")
        card_images[num] = ImageTk.PhotoImage(
            Image.open(path).resize((150, 150))
        )

    # --- Schieberegler für die Verzögerung ---
    slider_frame = tk.Frame(root)
    slider_frame.grid(row=0, column=0, columnspan=size, pady=10)
    
    delay_label = tk.Label(slider_frame, text="Verzögerung (ms):")
    delay_label.pack(side=tk.LEFT, padx=(0, 5))
    
    delay_slider = tk.Scale(slider_frame, from_=500, to=3000, orient=tk.HORIZONTAL)
    delay_slider.set(1000)
    delay_slider.pack(side=tk.LEFT)

    # --- Spielfeld-Frame ---
    board_frame = tk.Frame(root)
    board_frame.grid(row=1, column=0, columnspan=size)

    # SPIEL-LOGIK in der GUI
    buttons = []
    selected = []

    def on_click(x, y):
        nonlocal selected, remaining_pairs
        if revealed[x][y] or len(selected) == 2:
            return

        reveal_card(revealed, x, y)
        buttons[x][y].config(image=card_images[board[x][y]])
        selected.append((x, y))

        if len(selected) == 2:
            root.after(delay_slider.get(), check_match)

    def check_match():
        nonlocal selected, remaining_pairs
        x1, y1 = selected[0]
        x2, y2 = selected[1]

        if is_match(board, x1, y1, x2, y2):
            remaining_pairs -= 1
            if remaining_pairs == 0:
                if messagebox.askyesno("Glückwunsch!", "Du hast alle Paare gefunden!\nMöchtest du nochmal spielen?"):
                    reset_game()
        else:
            hide_cards(revealed, x1, y1, x2, y2)
            buttons[x1][y1].config(image=backside_image)
            buttons[x2][y2].config(image=backside_image)

        selected.clear()

    def reset_game():
        nonlocal board, revealed, remaining_pairs, selected
        board, revealed = initialize_game(size)
        remaining_pairs = (size * size) // 2
        selected.clear()
        for i in range(size):
            for j in range(size):
                buttons[i][j].config(image=backside_image)

    # Erstelle das Button-Gitter für das Spielfeld
    for i in range(size):
        row_buttons = []
        for j in range(size):
            btn = tk.Button(board_frame, image=backside_image, command=lambda i=i, j=j: on_click(i, j))
            btn.grid(row=i, column=j, padx=5, pady=5)
            row_buttons.append(btn)
        buttons.append(row_buttons)

    # Begrüßungsnachricht anzeigen, sobald das Fenster initialisiert und sichtbar ist
    def show_welcome():
        messagebox.showinfo("Willkommen", "Liebe Inge! Viel Spaß beim Spielen. Dein Hendrik")
    
    # Warte 100ms, damit das Fenster vollständig aufgebaut ist, und zeige dann die Nachricht
    root.after(100, show_welcome)

    root.mainloop()
