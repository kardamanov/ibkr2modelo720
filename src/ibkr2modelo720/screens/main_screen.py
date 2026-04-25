from __future__ import annotations

import pathlib

import textual
import textual.app
import textual.containers
import textual.screen
import textual.widgets

from .. import ecb_rates, modelo720


class MainScreen(textual.screen.Screen):
    CSS = """
    VerticalScroll {
        padding: 1 2;
    }
    .field-label {
        margin-top: 1;
        color: $text-muted;
    }
    .section-header {
        margin-top: 2;
        text-style: bold;
        color: $primary;
    }
    Input {
        margin-bottom: 0;
    }
    Select {
        margin-bottom: 0;
    }
    RadioSet {
        margin-bottom: 1;
        height: auto;
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
        color: $warning;
    }
    """

    def compose(self) -> textual.app.ComposeResult:
        yield textual.widgets.Header(show_clock=True)
        with textual.containers.VerticalScroll():
            yield textual.widgets.Label(
                "Modelo 720 — Declaration Generator", classes="title"
            )

            # --- Declarant section ---
            yield textual.widgets.Label(
                "-- Declarant --", classes="section-header"
            )

            yield textual.widgets.Label("NIE / NIF:", classes="field-label")
            yield textual.widgets.Input(placeholder="Y1234567X", id="nif")

            yield textual.widgets.Label("First name:", classes="field-label")
            yield textual.widgets.Input(placeholder="JUAN", id="nombre")

            yield textual.widgets.Label("Surname 1:", classes="field-label")
            yield textual.widgets.Input(placeholder="GARCIA", id="apellido1")

            yield textual.widgets.Label(
                "Surname 2 (optional):", classes="field-label"
            )
            yield textual.widgets.Input(placeholder="LOPEZ", id="apellido2")

            yield textual.widgets.Label(
                "Phone (9 digits):", classes="field-label"
            )
            yield textual.widgets.Input(
                placeholder="612345678", id="telefono"
            )

            # --- Broker section ---
            yield textual.widgets.Label(
                "-- Broker --", classes="section-header"
            )

            broker_options = [
                (name, name) for name in modelo720.BROKER_PRESETS
            ]
            broker_options.append(("Custom", "Custom"))
            yield textual.widgets.Label(
                "Broker preset:", classes="field-label"
            )
            yield textual.widgets.Select(
                broker_options,
                value="IBKR Ireland",
                id="broker_preset",
            )

            yield textual.widgets.Label(
                "Broker name:", classes="field-label"
            )
            yield textual.widgets.Input(
                value=modelo720.IBKR_IRELAND.name, id="broker_name"
            )

            yield textual.widgets.Label(
                "Broker tax ID:", classes="field-label"
            )
            yield textual.widgets.Input(
                value=modelo720.IBKR_IRELAND.tax_id, id="broker_tax_id"
            )

            yield textual.widgets.Label(
                "Broker country (2-letter code):", classes="field-label"
            )
            yield textual.widgets.Input(
                value=modelo720.IBKR_IRELAND.country_code,
                id="broker_country",
            )

            yield textual.widgets.Label(
                "Broker street:", classes="field-label"
            )
            yield textual.widgets.Input(
                value=modelo720.IBKR_IRELAND.street, id="broker_street"
            )

            yield textual.widgets.Label(
                "Broker city:", classes="field-label"
            )
            yield textual.widgets.Input(
                value=modelo720.IBKR_IRELAND.city, id="broker_city"
            )

            yield textual.widgets.Label(
                "Broker province:", classes="field-label"
            )
            yield textual.widgets.Input(
                value=modelo720.IBKR_IRELAND.province, id="broker_province"
            )

            yield textual.widgets.Label(
                "Broker postal code:", classes="field-label"
            )
            yield textual.widgets.Input(
                value=modelo720.IBKR_IRELAND.postal_code,
                id="broker_postal_code",
            )

            # --- Filing section ---
            yield textual.widgets.Label(
                "-- Filing --", classes="section-header"
            )

            yield textual.widgets.Label(
                "Fiscal year:", classes="field-label"
            )
            yield textual.widgets.Input(value="2025", id="ejercicio")

            yield textual.widgets.Label(
                "IBKR CSV file:", classes="field-label"
            )
            yield textual.widgets.Input(
                value="~/Downloads/IBKR_2025.csv", id="csv_path"
            )

            yield textual.widgets.Label(
                "EUR/USD rate (1 EUR = ? USD):", classes="field-label"
            )
            yield textual.widgets.Input(
                placeholder="1.0386", id="exchange_rate"
            )
            with textual.containers.Horizontal(classes="btn-row"):
                yield textual.widgets.Button(
                    "Fetch from ECB", id="btn-ecb", variant="default"
                )

            yield textual.widgets.Label(
                "Asset origin:", classes="field-label"
            )
            with textual.widgets.RadioSet(id="origen"):
                yield textual.widgets.RadioButton(
                    "A — New assets", value=True, id="origen_a"
                )
                yield textual.widgets.RadioButton(
                    "M — Previously declared", id="origen_m"
                )

            yield textual.widgets.Label(
                "Incorporation date (YYYYMMDD):", classes="field-label"
            )
            yield textual.widgets.Input(
                value="20250101", id="fecha_incorporacion"
            )

            yield textual.widgets.Label(
                "Output file:", classes="field-label"
            )
            yield textual.widgets.Input(
                value="", id="output_path", placeholder="{NIF}.720"
            )

            yield textual.widgets.Static("", id="status")

            with textual.containers.Horizontal(classes="btn-row"):
                yield textual.widgets.Button(
                    "Generate", id="btn-generate", variant="primary"
                )
                yield textual.widgets.Button(
                    "Quit", id="btn-quit", variant="error"
                )

        yield textual.widgets.Footer()

    def on_select_changed(
        self, event: textual.widgets.Select.Changed
    ) -> None:
        if event.select.id != "broker_preset":
            return
        preset_name = str(event.value)
        if preset_name not in modelo720.BROKER_PRESETS:
            return
        broker = modelo720.BROKER_PRESETS[preset_name]
        self.query_one("#broker_name", textual.widgets.Input).value = (
            broker.name
        )
        self.query_one("#broker_tax_id", textual.widgets.Input).value = (
            broker.tax_id
        )
        self.query_one("#broker_country", textual.widgets.Input).value = (
            broker.country_code
        )
        self.query_one("#broker_street", textual.widgets.Input).value = (
            broker.street
        )
        self.query_one("#broker_city", textual.widgets.Input).value = (
            broker.city
        )
        self.query_one("#broker_province", textual.widgets.Input).value = (
            broker.province
        )
        self.query_one(
            "#broker_postal_code", textual.widgets.Input
        ).value = broker.postal_code

    def on_button_pressed(
        self, event: textual.widgets.Button.Pressed
    ) -> None:
        if event.button.id == "btn-ecb":
            self._fetch_ecb_rate()
        elif event.button.id == "btn-generate":
            self._generate()
        elif event.button.id == "btn-quit":
            self.app.exit()

    @textual.work(thread=True)
    def _fetch_ecb_rate(self) -> None:
        status = self.query_one("#status", textual.widgets.Static)
        ejercicio_input = self.query_one("#ejercicio", textual.widgets.Input)
        rate_input = self.query_one("#exchange_rate", textual.widgets.Input)

        try:
            year = int(ejercicio_input.value.strip())
            self.app.call_from_thread(
                status.update, "Fetching rate from ECB..."
            )
            rate = ecb_rates.fetch_usd_eur_rate(year)
            self.app.call_from_thread(
                rate_input.__setattr__, "value", f"{rate:.4f}"
            )
            self.app.call_from_thread(
                status.update, f"Rate fetched: 1 EUR = {rate:.4f} USD"
            )
        except Exception as e:
            self.app.call_from_thread(status.update, f"Error: {e}")

    def _get_form_data(self) -> dict | None:
        status = self.query_one("#status", textual.widgets.Static)

        nif = self.query_one("#nif", textual.widgets.Input).value.strip()
        if not nif:
            status.update("Error: NIF/NIE is required")
            return None

        nombre = self.query_one(
            "#nombre", textual.widgets.Input
        ).value.strip()
        apellido1 = self.query_one(
            "#apellido1", textual.widgets.Input
        ).value.strip()
        apellido2 = self.query_one(
            "#apellido2", textual.widgets.Input
        ).value.strip()
        if not all([nombre, apellido1]):
            status.update("Error: first name and surname 1 are required")
            return None

        telefono = self.query_one(
            "#telefono", textual.widgets.Input
        ).value.strip()
        if not telefono.isdigit() or len(telefono) != 9:
            status.update("Error: phone must be 9 digits")
            return None

        # Broker fields
        broker_name = self.query_one(
            "#broker_name", textual.widgets.Input
        ).value.strip()
        broker_tax_id = self.query_one(
            "#broker_tax_id", textual.widgets.Input
        ).value.strip()
        broker_country = self.query_one(
            "#broker_country", textual.widgets.Input
        ).value.strip()
        broker_street = self.query_one(
            "#broker_street", textual.widgets.Input
        ).value.strip()
        broker_city = self.query_one(
            "#broker_city", textual.widgets.Input
        ).value.strip()
        broker_province = self.query_one(
            "#broker_province", textual.widgets.Input
        ).value.strip()
        broker_postal_code = self.query_one(
            "#broker_postal_code", textual.widgets.Input
        ).value.strip()

        if not all([broker_name, broker_country]):
            status.update("Error: broker name and country are required")
            return None

        ejercicio = self.query_one(
            "#ejercicio", textual.widgets.Input
        ).value.strip()
        if not ejercicio.isdigit() or len(ejercicio) != 4:
            status.update("Error: fiscal year must be 4 digits")
            return None

        csv_path = pathlib.Path(
            self.query_one("#csv_path", textual.widgets.Input).value.strip()
        ).expanduser()
        if not csv_path.exists():
            status.update(f"Error: file not found: {csv_path}")
            return None

        rate_str = self.query_one(
            "#exchange_rate", textual.widgets.Input
        ).value.strip()
        try:
            rate = float(rate_str)
        except ValueError:
            status.update("Error: invalid EUR/USD rate")
            return None

        radio_set = self.query_one("#origen", textual.widgets.RadioSet)
        origen = "A" if radio_set.pressed_index == 0 else "M"

        fecha = self.query_one(
            "#fecha_incorporacion", textual.widgets.Input
        ).value.strip()
        if not fecha.isdigit() or len(fecha) != 8:
            status.update("Error: date must be in YYYYMMDD format")
            return None

        output_path = self.query_one(
            "#output_path", textual.widgets.Input
        ).value.strip()
        if not output_path:
            output_path = f"{nif.upper()}.720"

        return {
            "nif": nif,
            "apellido1": apellido1,
            "apellido2": apellido2,
            "nombre": nombre,
            "telefono": telefono,
            "ejercicio": int(ejercicio),
            "csv_path": str(csv_path),
            "exchange_rate": rate,
            "origen": origen,
            "fecha_incorporacion": fecha,
            "output_path": output_path,
            "broker": modelo720.BrokerInfo(
                name=broker_name,
                tax_id=broker_tax_id,
                country_code=broker_country,
                street=broker_street,
                city=broker_city,
                province=broker_province,
                postal_code=broker_postal_code,
            ),
        }

    def _generate(self) -> None:
        data = self._get_form_data()
        if data is None:
            return

        from .. import csv_parser
        from .preview_screen import PreviewScreen

        status = self.query_one("#status", textual.widgets.Static)

        try:
            positions = csv_parser.parse_ibkr_csv(data["csv_path"])
            if not positions:
                status.update("Error: CSV contains no positions")
                return

            config = modelo720.DeclarantConfig(
                nif=data["nif"],
                apellido1=data["apellido1"],
                apellido2=data["apellido2"],
                nombre=data["nombre"],
                telefono=data["telefono"],
                ejercicio=data["ejercicio"],
                origen=data["origen"],
                fecha_incorporacion=data["fecha_incorporacion"],
                exchange_rate=data["exchange_rate"],
                broker=data["broker"],
            )

            records = modelo720.generate_file(config, positions)
            self.app.push_screen(
                PreviewScreen(config, positions, records, data["output_path"])
            )
        except Exception as e:
            status.update(f"Error: {e}")
