from __future__ import annotations

import textual.app
import textual.containers
import textual.screen
import textual.widgets


class ResultScreen(textual.screen.Screen):
    CSS = """
    VerticalScroll {
        padding: 1 2;
        align: center middle;
    }
    .result-line {
        margin-top: 1;
    }
    #btn-quit {
        margin-top: 2;
    }
    """

    def __init__(
        self,
        output_path: str,
        record_count: int,
        total_eur: float,
    ) -> None:
        super().__init__()
        self._output_path = output_path
        self._record_count = record_count
        self._total_eur = total_eur

    def compose(self) -> textual.app.ComposeResult:
        yield textual.widgets.Header(show_clock=True)
        with textual.containers.VerticalScroll():
            yield textual.widgets.Label(
                "File created successfully!", classes="title"
            )

            yield textual.widgets.Static(
                f"Path: {self._output_path}",
                classes="result-line",
            )
            yield textual.widgets.Static(
                f"Records: {self._record_count} "
                f"(1 declarant + {self._record_count - 1} positions)",
                classes="result-line",
            )
            yield textual.widgets.Static(
                f"Total value: {self._total_eur:,.2f} EUR",
                classes="result-line",
            )

            yield textual.widgets.Button(
                "Quit", id="btn-quit", variant="primary"
            )
        yield textual.widgets.Footer()

    def on_button_pressed(
        self, event: textual.widgets.Button.Pressed
    ) -> None:
        if event.button.id == "btn-quit":
            self.app.exit()
