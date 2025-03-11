import os
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window

from memory import initialize_game, is_match

ASSET_PATH = os.path.join("assets", "resized")
GRID_SIZE = 4
SLIDER_HEIGHT = 80
SLIDER_MIN = 0.5
SLIDER_MAX = 3.0
SLIDER_DEFAULT = 1.0

# ----------------------------
# CardButton: repräsentiert eine Karte
# ----------------------------
class CardButton(Button):
    def __init__(self, row, col, screen, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.screen = screen  # Referenz zum GameScreen für Event-Handling
        self.value = None
        self.revealed = False
        self.back_source = os.path.join(ASSET_PATH, "back.jpeg")
        self.front_source = ""
        self.update_graphics()

    def set_value(self, value):
        self.value = value
        self.front_source = os.path.join(ASSET_PATH, f"image{value - 1}.jpeg")

    def reveal(self):
        self.revealed = True
        self.update_graphics()

    def hide(self):
        self.revealed = False
        self.update_graphics()

    def update_graphics(self):
        self.background_normal = self.front_source if self.revealed else self.back_source
        self.background_down = self.background_normal

# ----------------------------
# GameBoardWidget: enthält das Spielfeld (GridLayout)
# ----------------------------
class GameBoardWidget(BoxLayout):
    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen
        # Wir setzen size_hint=(None,None) für das Grid, damit wir die Größe manuell steuern können
        self.grid = GridLayout(cols=GRID_SIZE, rows=GRID_SIZE, spacing=10, padding=10, size_hint=(None, None))
        self.add_widget(self.grid)
        self.cards = [[CardButton(row=i, col=j, screen=screen) for j in range(GRID_SIZE)]
                      for i in range(GRID_SIZE)]
        for row in self.cards:
            for card in row:
                card.bind(on_release=screen.on_card_pressed)
                self.grid.add_widget(card)
        self.bind(size=self.update_grid_size)

    def update_grid_size(self, *args):
        side = max(0, min(self.size) - 20)
        self.grid.size = (side, side)
        self.grid.pos_hint = {"center_x": 0.5, "center_y": 0.5}

# ----------------------------
# SplashScreen: interner SplashScreen
# ----------------------------
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        # Verwende eine höhere Auflösung, wenn vorhanden oder sorge für das Stretching
        splash_img = Image(
            source=os.path.join("assets", "resized", "back.jpeg"),
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True  # oder False, falls das Bild genau den Bildschirm füllen soll
        )
        layout.add_widget(splash_img)
        self.add_widget(layout)

    def on_enter(self):
        # Nach 1,5 Sekunden zum GameScreen wechseln
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'game'), 1.5)
        
# ----------------------------
# GameScreen: Hier findet das eigentliche Spiel statt
# ----------------------------
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.delay_time = SLIDER_DEFAULT
        self.selected_cards = []
        self.locked = False
        self.board = None

        # Hauptlayout: vertikal, mit Spielfeld oben und Slider unten
        self.layout = BoxLayout(orientation="vertical")
        self.game_board_widget = GameBoardWidget(screen=self, size_hint=(1, 1))
        self.layout.add_widget(self.game_board_widget)

        # Slider-Container
        self.slider_container = BoxLayout(orientation="horizontal",
                                          size_hint_y=None, height=SLIDER_HEIGHT, padding=10)
        self.delay_slider = Slider(min=SLIDER_MIN, max=SLIDER_MAX, value=self.delay_time, step=0.1)
        self.delay_slider.bind(value=self.on_slider_value_changed)
        self.slider_container.add_widget(self.delay_slider)
        self.layout.add_widget(self.slider_container)

        self.add_widget(self.layout)

        # Verzögert den Force-Refresh, um sicherzustellen, dass Kivy initialisiert ist
        Clock.schedule_once(lambda dt: self.force_refresh(), 0.5)
        # Starte das Spiel (reset_game) etwas später
        Clock.schedule_once(lambda dt: self.reset_game(), 0.6)

    def force_refresh(self):
        print("🟢 GameScreen: Erzwinge Neuzeichnung des Spielfelds... (force_refresh aufgerufen)")
        w, h = Window.size

        # Strategie: Explizite minimale Größenänderung und manuelles Auslösen des Resize-Events
        Window.size = (w + 1, h + 1)
        Clock.schedule_once(lambda dt: setattr(Window, 'size', (w, h)), 0.1)
        Clock.schedule_once(lambda dt: Window.dispatch('on_resize', *Window.size), 0.2)
        # Letzter Aufruf des Grid-Updates
        Clock.schedule_once(lambda dt: self.game_board_widget.update_grid_size(), 0.3)

    def on_slider_value_changed(self, instance, value):
        self.delay_time = value

    def on_card_pressed(self, card):
        if self.locked or card.revealed:
            return
        card.reveal()
        self.selected_cards.append(card)
        if len(self.selected_cards) == 2:
            first, second = self.selected_cards
            if is_match(self.board, first.row, first.col, second.row, second.col):
                self.selected_cards = []
                if self.check_game_complete():
                    Clock.schedule_once(lambda dt: self.show_game_complete_popup(), 0.5)
            else:
                self.locked = True
                Clock.schedule_once(lambda dt: self.hide_selected_cards(), self.delay_time)

    def hide_selected_cards(self):
        for c in self.selected_cards:
            c.hide()
        self.selected_cards.clear()
        self.locked = False

    def check_game_complete(self):
        return all(card.revealed for row in self.game_board_widget.cards for card in row)

    def show_game_complete_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text="Du hast alle Paare gefunden!"))
        btn_ok = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(btn_ok)
        popup = Popup(title="Glückwunsch", content=content, size_hint=(0.8, 0.5))
        btn_ok.bind(on_release=lambda x: (popup.dismiss(), self.reset_game()))
        popup.open()

    def reset_game(self):
        self.board, _ = initialize_game(GRID_SIZE)
        for i, row in enumerate(self.game_board_widget.cards):
            for j, card in enumerate(row):
                card.set_value(self.board[i][j])
                card.hide()
        self.selected_cards.clear()
        self.locked = False

# ----------------------------
# MemoryApp: Haupt-App, die den ScreenManager nutzt
# ----------------------------
class MemoryApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(GameScreen(name="game"))
        sm.current = "splash"
        return sm

def run_gui_kivy():
    MemoryApp().run()

if __name__ == "__main__":
    run_gui_kivy()
