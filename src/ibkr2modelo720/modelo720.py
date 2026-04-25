from __future__ import annotations

import dataclasses as dcs
import decimal

from . import csv_parser

RECORD_LENGTH = 500


@dcs.dataclass
class BrokerInfo:
    """Broker identification and address for Tipo 2 records."""
    name: str  # e.g. "INTERACTIVE BROKERS IRELAND LIMITED"
    tax_id: str  # e.g. "657406"
    country_code: str  # e.g. "IE"
    street: str  # e.g. "NORTH DOCK ONE, 91/92 NORTH WALL QUAY"
    city: str  # e.g. "DUBLIN"
    province: str  # e.g. "DUBLIN"
    postal_code: str  # e.g. "D01 H7V7"


# Pre-configured broker profiles
IBKR_IRELAND = BrokerInfo(
    name="INTERACTIVE BROKERS IRELAND LIMITED",
    tax_id="657406",
    country_code="IE",
    street="NORTH DOCK ONE, 91/92 NORTH WALL QUAY",
    city="DUBLIN",
    province="DUBLIN",
    postal_code="D01 H7V7",
)

IBKR_LLC = BrokerInfo(
    name="INTERACTIVE BROKERS LLC",
    tax_id="13-3863700",
    country_code="US",
    street="ONE PICKWICK PLAZA",
    city="GREENWICH",
    province="CONNECTICUT",
    postal_code="06830",
)

BROKER_PRESETS: dict[str, BrokerInfo] = {
    "IBKR Ireland": IBKR_IRELAND,
    "IBKR LLC (US)": IBKR_LLC,
}


@dcs.dataclass
class DeclarantConfig:
    nif: str
    apellido1: str
    apellido2: str
    nombre: str
    telefono: str
    ejercicio: int
    origen: str  # "A" or "M"
    fecha_incorporacion: str  # YYYYMMDD
    exchange_rate: float  # USD per 1 EUR
    broker: BrokerInfo

    @property
    def apellidos_nombre(self) -> str:
        """Format as 'APELLIDO1 APELLIDO2 NOMBRE' per AEAT spec."""
        parts = [self.apellido1]
        if self.apellido2:
            parts.append(self.apellido2)
        parts.append(self.nombre)
        return " ".join(parts).upper()

    @property
    def nif_formatted(self) -> str:
        """NIF right-justified to 9 characters."""
        return self.nif.upper().rjust(9)


def _alpha(value: str, length: int) -> str:
    """Alphanumeric field: left-justified, space-padded, uppercased."""
    return value.upper().ljust(length)[:length]


def _numeric(value: int, length: int) -> str:
    """Numeric field: right-justified, zero-padded."""
    return str(value).zfill(length)[-length:]


def _amount_fields(
    euros: decimal.Decimal, int_len: int, dec_len: int
) -> tuple[str, str]:
    """Split a EUR amount into sign char and integer+decimal string."""
    cents = euros.quantize(
        decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP
    )
    sign = cents < 0
    abs_cents = abs(cents)
    integer_part = int(abs_cents)
    decimal_part = int((abs_cents - integer_part) * 100)
    sign_char = "N" if sign else " "
    return sign_char, _numeric(integer_part, int_len) + _numeric(
        decimal_part, dec_len
    )


def usd_to_eur(usd: float, rate: float) -> decimal.Decimal:
    """Convert USD to EUR. ``rate`` is how many USD equal 1 EUR."""
    return decimal.Decimal(str(usd)) / decimal.Decimal(str(rate))


def generate_tipo2(
    config: DeclarantConfig,
    position: csv_parser.Position,
) -> str:
    """Generate a single Tipo 2 (detail) record for one position."""
    eur_value = usd_to_eur(position.value, config.exchange_rate)
    sign1, amount1 = _amount_fields(eur_value, 12, 2)
    broker = config.broker

    parts = [
        "2",                                            # 1:     Record type
        "720",                                          # 2-4:   Model
        _numeric(config.ejercicio, 4),                  # 5-8:   Fiscal year
        config.nif_formatted,                           # 9-17:  Declarant NIF
        config.nif_formatted,                           # 18-26: Declared party NIF
        " " * 9,                                        # 27-35: Legal rep NIF
        _alpha(config.apellidos_nombre, 40),            # 36-75: Name
        "1",                                            # 76:    Condition (titular)
        " " * 25,                                       # 77-101: Ownership type
        "V",                                            # 102:   Asset type (valores)
        "1",                                            # 103:   Sub-type
        " " * 25,                                       # 104-128: Real estate right
        _alpha(broker.country_code, 2),                 # 129-130: Broker country
        "1",                                            # 131:   ID key (ISIN)
        _alpha(position.isin, 12),                      # 132-143: ISIN
        " ",                                            # 144:   Account ID key
        " " * 11,                                       # 145-155: BIC
        " " * 34,                                       # 156-189: Account code
        _alpha(broker.name, 41),                        # 190-230: Broker name
        _alpha(broker.tax_id, 20),                      # 231-250: Broker tax NIF
        _alpha(broker.street, 52),                      # 251-302: Address: street
        " " * 40,                                       # 303-342: Address: extra
        _alpha(broker.city, 30),                        # 343-372: Address: city
        _alpha(broker.province, 30),                    # 373-402: Address: province
        _alpha(broker.postal_code, 10),                 # 403-412: Postal code
        _alpha(broker.country_code, 2),                 # 413-414: Country code
        config.fecha_incorporacion,                     # 415-422: Incorporation date
        config.origen.upper(),                          # 423:   Origin
        "0" * 8,                                        # 424-431: Extinction date
        sign1,                                          # 432:   Valuation 1 sign
        amount1,                                        # 433-446: Valuation 1
        " ",                                            # 447:   Valuation 2 sign
        "0" * 14,                                       # 448-461: Valuation 2
        "A",                                            # 462:   Securities repr.
        _numeric(int(position.quantity), 10),           # 463-472: Num securities int
        _numeric(0, 2),                                 # 473-474: Num securities dec
        " ",                                            # 475:   Real estate type
        _numeric(100, 3),                               # 476-478: Participation % int
        _numeric(0, 2),                                 # 479-480: Participation % dec
    ]

    record = "".join(parts)
    padding = RECORD_LENGTH - len(record)
    assert padding >= 0, f"Tipo 2 record exceeds {RECORD_LENGTH}: {len(record)}"
    return record + " " * padding


def generate_tipo1(
    config: DeclarantConfig,
    tipo2_records: list[str],
    positions: list[csv_parser.Position],
) -> str:
    """Generate a Tipo 1 (declarant summary) record."""
    total_val1 = sum(
        usd_to_eur(p.value, config.exchange_rate) for p in positions
    )
    total_val2 = decimal.Decimal("0")

    sign1, amount1 = _amount_fields(total_val1, 15, 2)
    sign2, amount2 = _amount_fields(total_val2, 15, 2)

    parts = [
        "1",                                            # 1:     Record type
        "720",                                          # 2-4:   Model
        _numeric(config.ejercicio, 4),                  # 5-8:   Fiscal year
        config.nif_formatted,                           # 9-17:  NIF
        _alpha(config.apellidos_nombre, 40),            # 18-57: Surnames and name
        "T",                                            # 58:    Support type
        _numeric(int(config.telefono), 9),              # 59-67: Phone
        _alpha(config.apellidos_nombre, 40),            # 68-107: Contact person
        "720" + _numeric(0, 10),                        # 108-120: Declaration ID
        "  ",                                           # 121-122: Compl./Subst.
        "0" * 13,                                       # 123-135: Prior decl. ID
        _numeric(len(tipo2_records), 9),                # 136-144: Record count
        sign1,                                          # 145:   Valuation 1 sign
        amount1,                                        # 146-162: Valuation 1 sum
        sign2,                                          # 163:   Valuation 2 sign
        amount2,                                        # 164-180: Valuation 2 sum
    ]

    record = "".join(parts)
    padding = RECORD_LENGTH - len(record)
    assert padding >= 0, f"Tipo 1 record exceeds {RECORD_LENGTH}: {len(record)}"
    return record + " " * padding


def generate_file(
    config: DeclarantConfig,
    positions: list[csv_parser.Position],
) -> list[str]:
    """Generate a complete set of Modelo 720 records."""
    tipo2_records = [generate_tipo2(config, pos) for pos in positions]
    tipo1_record = generate_tipo1(config, tipo2_records, positions)
    return [tipo1_record] + tipo2_records
