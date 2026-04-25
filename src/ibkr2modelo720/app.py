import textual.app

from .screens import main_screen


class Modelo720App(textual.app.App):
    TITLE = "Modelo 720 — IBKR → AEAT"
    BINDINGS = [("q", "quit", "Quit")]

    def on_mount(self) -> None:
        self.push_screen(main_screen.MainScreen())
