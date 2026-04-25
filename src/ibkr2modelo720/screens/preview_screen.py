from __future__ import annotations

import textual.app
import textual.containers
import textual.screen
import textual.widgets

from .. import csv_parser, modelo720, writer


class PreviewScreen(textual.screen.Screen):
    CSS = """
    VerticalScroll {
        padding: 1 2;
    }
    DataTable {
        height: auto;
        max-height: 70%;
    }
    #summary {
        margin-top: 1;
        color: $success;
    }
    .btn-row {
        margin-top: 1;
        height: 3;
    }
    .btn-row Button {
        margin-right: 1;
    }
    #status {
        margin-top: 1;
    }
    """

    def __init__(
        self,
        config: modelo720.DeclarantConfig,
        positions: list[csv_parser.Position],
        records: list[str],
        output_path: str,
    ) -> None:
        super().__init__()
        self._config = config
        self._positions = positions
        self._records = records
        self._output_path = output_path

    def compose(self) -> textual.app.ComposeResult:
        yield textual.widgets.Header(show_clock=True)
        with textual.containers.VerticalScroll():
            yield textual.widgets.Label(
                "Position Preview", classes="title"
            )
            yield textual.widgets.DataTable(id="positions-table")

            total_usd = sum(p.value for p in self._positions)
            total_eur = sum(
                float(
                    modelo720.usd_to_eur(p.value, self._config.exchange_rate)
                )
                for p in self._positions
            )
            yield textual.widgets.Static(
                f"Positions: {len(self._positions)} | "
                f"Total USD: {total_usd:,.2f} | "
                f"Total EUR: {total_eur:,.2f} | "
                f"Rate: 1 EUR = {self._config.exchange_rate} USD",
                id="summary",
            )

            yield textual.widgets.Static("", id="status")

            with textual.containers.Horizontal(classes="btn-row"):
                yield textual.widgets.Button(
                    "Save file", id="btn-save", variant="primary"
                )
                yield textual.widgets.Button(
                    "Back", id="btn-back", variant="default"
                )

        yield textual.widgets.Footer()

    def on_mount(self) -> None:
        table = self.query_one(
            "#positions-table", textual.widgets.DataTable
        )
        table.add_columns(
            "ISIN", "Name", "Qty", "USD", "EUR", "Country"
        )

        for pos in self._positions:
            eur = float(
                modelo720.usd_to_eur(pos.value, self._config.exchange_rate)
            )
            table.add_row(
                pos.isin,
                pos.description[:30],
                f"{pos.quantity:,.0f}",
                f"{pos.value:,.2f}",
                f"{eur:,.2f}",
                pos.country_code,
            )

    def on_button_pressed(
        self, event: textual.widgets.Button.Pressed
    ) -> None:
        if event.button.id == "btn-save":
            self._save()
        elif event.button.id == "btn-back":
            self.app.pop_screen()

    def _save(self) -> None:
        status = self.query_one("#status", textual.widgets.Static)
        try:
            path = writer.write_modelo720(
                self._records, self._output_path
            )
            from . import result_screen

            self.app.push_screen(
                result_screen.ResultScreen(
                    output_path=str(path),
                    record_count=len(self._records),
                    total_eur=sum(
                        float(
                            modelo720.usd_to_eur(
                                p.value, self._config.exchange_rate
                            )
                        )
                        for p in self._positions
                    ),
                )
            )
        except Exception as e:
            status.update(f"Error saving file: {e}")
