# ui_gui_kivy.py
# ----------------------------------------------
# Dieses Modul implementiert eine Kivy-GUI für das Memory-Spiel.
# ----------------------------------------------

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window

# Importiere die bestehende Spiellogik
from memory import initialize_game, is_match, reveal_card, hide_cards

# Pfad zu den Bilddateien
ASSET_PATH = os.path.join("assets", "resized")

# Spielfeldgröße (4x4)
GRID_SIZE = 4

# Höhe des Schiebereglers in Pixel
SLIDER_HEIGHT = 80

# Minimale / Maximale Verzögerung (in Sekunden) und Standardwert
SLIDER_MIN = 0.5
SLIDER_MAX = 3.0
SLIDER_DEFAULT = 1.0

# ------------------------------------------------------------
# CardButton: Repräsentiert eine Karte (Button) im Memory-Spiel
# ------------------------------------------------------------
class CardButton(Button):
    """
    Jede Karte ist ein Kivy-Button, der je nach Zustand (verdeckt/aufgedeckt)
    ein anderes Hintergrundbild zeigt.
    """
    def __init__(self, row, col, app, **kwargs):
        super().__init__(**kwargs)
        # Zeile und Spalte im Raster
        self.row = row
        self.col = col
        # Referenz auf die Haupt-App (MemoryApp), damit wir z. B. bei Klick
        # Methoden der App aufrufen können
        self.app = app

        # Wert der Karte (z. B. 1..8), passend zu image0.jpeg..image7.jpeg
        self.value = None
        # Zeigt an, ob die Karte gerade aufgedeckt ist
        self.revealed = False

        # Bild für die Rückseite
        self.back_source = os.path.join(ASSET_PATH, "back.jpeg")
        # Bild für die Vorderseite (wird erst nach set_value() gesetzt)
        self.front_source = ""

        # Aktualisiere das Aussehen (zunächst verdeckt)
        self.update_graphics()

    def set_value(self, value):
        """
        Weist der Karte einen Wert zu (z. B. 1..8).
        Die zugehörige Bilddatei heißt dann z. B. image0.jpeg für value=1 usw.
        """
        self.value = value
        self.front_source = os.path.join(ASSET_PATH, f"image{value - 1}.jpeg")

    def reveal(self):
        """
        Deckt die Karte auf (zeigt das Vorderseiten-Bild).
        """
        self.revealed = True
        self.update_graphics()

    def hide(self):
        """
        Verbirgt die Karte wieder (zeigt die Rückseite).
        """
        self.revealed = False
        self.update_graphics()

    def update_graphics(self):
        """
        Setzt die Hintergrundbilder abhängig vom Zustand (revealed / hidden).
        """
        if self.revealed:
            self.background_normal = self.front_source
            self.background_down = self.front_source
        else:
            self.background_normal = self.back_source
            self.background_down = self.back_source


# ------------------------------------------------------------
# GameBoardWidget: Widget, das das quadratische 4x4-Raster enthält
# ------------------------------------------------------------
class GameBoardWidget(BoxLayout):
    """
    Dieses Widget enthält das GridLayout mit den Karten.
    Wir sorgen dafür, dass das GridLayout immer quadratisch bleibt,
    indem wir in update_grid_size() die kleinere Seitenlänge verwenden.
    """
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        # Ein GridLayout mit 4x4 Zellen, etwas spacing und padding.
        # size_hint=(None, None) => wir steuern die Größe manuell.
        self.grid = GridLayout(cols=GRID_SIZE, rows=GRID_SIZE, spacing=10, padding=10,
                               size_hint=(None, None))
        self.add_widget(self.grid)

        # Array zum Speichern der Karten (CardButtons)
        self.cards = []
        for i in range(GRID_SIZE):
            row = []
            for j in range(GRID_SIZE):
                # Erstelle eine Karte und binde das on_release-Ereignis an die App
                card = CardButton(row=i, col=j, app=app)
                card.bind(on_release=self.app.on_card_pressed)
                row.append(card)
                self.grid.add_widget(card)
            self.cards.append(row)

        # Wenn sich die Größe dieses Widgets ändert, rufen wir update_grid_size() auf
        self.bind(size=self.update_grid_size)

    def update_grid_size(self, *args):
        """
        Erzwingt eine quadratische Größe des GridLayouts (self.grid),
        indem wir die kleinere Seitenlänge nehmen.
        """
        w, h = self.size
        # Etwas Puffer abziehen, damit nicht ganz am Rand
        side = min(w, h) - 20
        # Falls die Berechnung mal negativ wird (z. B. sehr kleines Fenster), fange das ab
        if side < 0:
            side = 0
        # Setze die Größe des Grids
        self.grid.size = (side, side)
        # Optionales Zentrieren innerhalb dieses Widgets
        self.grid.pos_hint = {"center_x": 0.5, "center_y": 0.5}


# ------------------------------------------------------------
# MemoryApp: Die Hauptklasse der Kivy-App
# ------------------------------------------------------------
class MemoryApp(App):
    """
    Die Haupt-Kivy-App:
    - Erstellt das Spielfeld (GameBoardWidget)
    - Enthält die Logik für Kartenklicks
    - Zeigt Popups an (Willkommens-Nachricht, Spielende, usw.)
    - Besitzt einen Schieberegler für die Verzögerungszeit
    """
    def build(self):
        # Optional: Hintergrundfarbe des Fensters ändern (z. B. weiß)
        # Window.clearcolor = (1, 1, 1, 1)

        # Bestimme eine initiale Fenstergröße: 80% der kürzeren Bildschirm-Seite + Platz für Schieberegler
        screen_w, screen_h = Window.size
        short_side = min(screen_w, screen_h) * 0.8
        Window.size = (short_side, short_side + SLIDER_HEIGHT)

        # Standard-Verzögerung in Sekunden
        self.delay_time = SLIDER_DEFAULT
        # Liste der aktuell aufgedeckten Karten (max. 2)
        self.selected_cards = []
        # Sperrt temporär Eingaben, wenn gerade 2 Karten offen sind und wir auf Verzögerung warten
        self.locked = False

        # Spiellogik initialisieren (Board generieren)
        #self.reset_game_logic()
        
        # Oberstes Layout: vertikale Anordnung (Spielfeld oben, Schieberegler unten)
        root = BoxLayout(orientation="vertical")

        # Das Spielfeld-Widget, soll den verbleibenden Platz (size_hint=(1,1)) einnehmen
        self.game_board_widget = GameBoardWidget(app=self, size_hint=(1, 1))
        root.add_widget(self.game_board_widget)

        # Unten ein Layout für den Schieberegler (feste Höhe)
        slider_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=SLIDER_HEIGHT, padding=10)
        self.slider_label = Label(text=f"Verzögerung: {self.delay_time:.1f}s", size_hint_x=0.3)
        self.delay_slider = Slider(min=SLIDER_MIN, max=SLIDER_MAX, value=self.delay_time, step=0.1)
        self.delay_slider.bind(value=self.on_slider_value_changed)

        slider_container.add_widget(self.slider_label)
        slider_container.add_widget(self.delay_slider)
        root.add_widget(slider_container)

        # Zeige ein Willkommens-Popup nach kurzer Verzögerung
        Clock.schedule_once(lambda dt: self.show_welcome_popup(), 0.5)

        # Spiellogik initialisieren (Board generieren)        
        self.reset_game()

        return root

    def on_slider_value_changed(self, instance, value):
        """
        Wird aufgerufen, wenn sich der Wert des Schiebereglers ändert.
        """
        self.delay_time = value
        self.slider_label.text = f"Verzögerung: {value:.1f}s"

    def on_card_pressed(self, card):
        """
        Wird aufgerufen, wenn eine Karte geklickt wird.
        """
        # Wenn das UI gesperrt ist oder die Karte schon aufgedeckt ist, nichts tun
        if self.locked or card.revealed:
            return

        # Karte aufdecken
        card.reveal()
        self.selected_cards.append(card)

        # Wenn 2 Karten aufgedeckt wurden, prüfen, ob sie zusammenpassen
        if len(self.selected_cards) == 2:
            first, second = self.selected_cards
            # Testen, ob das ein Paar ist
            if is_match(self.board, first.row, first.col, second.row, second.col):
                # Richtiger Treffer: Liste leeren und prüfen, ob das Spiel fertig ist
                self.selected_cards = []
                if self.check_game_complete():
                    # Kurze Verzögerung, dann Glückwunsch-Popup
                    Clock.schedule_once(lambda dt: self.show_game_complete_popup(), 0.5)
            else:
                # Falsches Paar: nach delay_time wieder umdrehen
                self.locked = True
                Clock.schedule_once(lambda dt: self.hide_selected_cards(), self.delay_time)

    def hide_selected_cards(self):
        """
        Versteckt die beiden zuletzt aufgedeckten Karten wieder.
        """
        for c in self.selected_cards:
            c.hide()
        self.selected_cards = []
        self.locked = False

    def check_game_complete(self):
        """
        Prüft, ob alle Karten im Raster aufgedeckt wurden.
        """
        for row in self.game_board_widget.cards:
            for card in row:
                if not card.revealed:
                    return False
        return True

    def show_welcome_popup(self):
        """
        Zeigt zu Spielbeginn ein Popup mit Willkommens-Text.
        """
        popup = Popup(
            title="Willkommen",
            content=Label(text="Liebe Inge! Viele Spaß beim Spielen. Dein Hendrik"),
            size_hint=(0.8, 0.5)
        )
        # Schließen bei beliebigem Klick ins Popup
        popup.bind(on_touch_down=lambda inst, touch: popup.dismiss())
        popup.open()

    def show_game_complete_popup(self):
        """
        Zeigt ein Popup an, wenn alle Paare gefunden wurden.
        Fragt, ob man noch einmal spielen will.
        """
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text="Noch einmal spielen?"))

        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        btn_yes = Button(text="Ja")
        btn_no = Button(text="Nein")
        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)

        content.add_widget(btn_layout)

        popup = Popup(title="Glückwunsch", content=content, size_hint=(0.8, 0.5))

        # Bei Klick auf "Ja" -> Spiel neustarten
        btn_yes.bind(on_release=lambda x: self.restart_game(popup))
        # Bei Klick auf "Nein" -> Popup schließen
        btn_no.bind(on_release=lambda x: popup.dismiss())

        popup.open()

    def reset_game(self):
        # 1) Logik neu erzeugen
        self.board, _ = initialize_game(GRID_SIZE)

        # 2) Alle Karten im UI neu belegen und verstecken
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                card = self.game_board_widget.cards[i][j]
                card.set_value(self.board[i][j])
                card.hide()

        # Sonstige Variablen zurücksetzen
        self.selected_cards = []
        self.locked = False
    
    def restart_game(self, popup):
        """
        Wird aufgerufen, wenn der Benutzer "Ja" wählt (noch einmal spielen).
        """
        popup.dismiss()
        self.reset_game()    

# ------------------------------------------------------------
# run_gui_kivy: Einstiegspunkt zum Starten der Kivy-Anwendung
# ------------------------------------------------------------
def run_gui_kivy():
    MemoryApp().run()


# Falls man das Modul direkt startet, kann man zum Testen hier aufrufen
if __name__ == "__main__":
    run_gui_kivy()
