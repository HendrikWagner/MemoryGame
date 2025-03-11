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

from memory import initialize_game, is_match

ASSET_PATH = os.path.join("assets", "resized")
GRID_SIZE = 4
SLIDER_HEIGHT = 80
SLIDER_MIN = 0.5
SLIDER_MAX = 3.0
SLIDER_DEFAULT = 1.0

class CardButton(Button):
    def __init__(self, row, col, app, **kwargs):
        super().__init__(**kwargs)
        self.row, self.col = row, col
        self.app = app
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

class GameBoardWidget(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.grid = GridLayout(cols=GRID_SIZE, rows=GRID_SIZE, spacing=10, padding=10, size_hint=(None, None))
        self.add_widget(self.grid)
        self.cards = [[CardButton(row=i, col=j, app=app) for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]
        for row in self.cards:
            for card in row:
                card.bind(on_release=self.app.on_card_pressed)
                self.grid.add_widget(card)
        self.bind(size=self.update_grid_size)

    def update_grid_size(self, *args):
        side = max(0, min(self.size) - 20)
        self.grid.size = (side, side)
        self.grid.pos_hint = {"center_x": 0.5, "center_y": 0.5}

class MemoryApp(App):
    def build(self):
        screen_w, screen_h = Window.size
        short_side = min(screen_w, screen_h) * 0.8
        Window.size = (short_side, short_side + SLIDER_HEIGHT)

        self.delay_time = SLIDER_DEFAULT
        self.selected_cards = []
        self.locked = False

        root = BoxLayout(orientation="vertical")
        self.game_board_widget = GameBoardWidget(app=self, size_hint=(1, 1))
        root.add_widget(self.game_board_widget)

        slider_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=SLIDER_HEIGHT, padding=10)
        self.delay_slider = Slider(min=SLIDER_MIN, max=SLIDER_MAX, value=self.delay_time, step=0.1)
        self.delay_slider.bind(value=self.on_slider_value_changed)
        slider_container.add_widget(self.delay_slider)
        root.add_widget(slider_container)

        Clock.schedule_once(lambda dt: self.game_board_widget.update_grid_size(), 0.1)
        Clock.schedule_once(lambda dt: self.force_refresh(), 0.2)  # Erzwingt eine korrekte Skalierung nach Start

        self.reset_game()
        return root

    def force_refresh(self):
        print("🟢 Erzwinge Neuzeichnung des Spielfelds... (force_refresh aufgerufen)")
        
        # Manuelles Setzen der Fenstergröße, um das Resize-Event auszulösen
        Window.size = (Window.size[0] + 1, Window.size[1])  # +1 Pixel in der Breite
        Window.size = (Window.size[0] - 1, Window.size[1])  # Zurück auf die Originalgröße
        
        # Erzwinge Neuzeichnung
        self.game_board_widget.update_grid_size()
        Window.dispatch('on_resize', *Window.size)  # Löst eine Neuzeichnung des Fensters aus


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
        self.selected_cards = []
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

def run_gui_kivy():
    MemoryApp().run()

if __name__ == "__main__":
    run_gui_kivy()
