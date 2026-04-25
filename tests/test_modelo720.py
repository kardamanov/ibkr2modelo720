import decimal

import ibkr2modelo720.csv_parser as csv_parser
import ibkr2modelo720.modelo720 as modelo720


def _make_config() -> modelo720.DeclarantConfig:
    return modelo720.DeclarantConfig(
        nif="Y1234567X",
        apellido1="GARCIA",
        apellido2="LOPEZ",
        nombre="JUAN",
        telefono="612345678",
        ejercicio=2025,
        origen="A",
        fecha_incorporacion="20250101",
        exchange_rate=1.0386,
        broker=modelo720.IBKR_IRELAND,
    )


def _make_position() -> csv_parser.Position:
    return csv_parser.Position(
        isin="US0378331005",
        description="APPLE INC",
        quantity=70,
        currency="USD",
        value=19030.20,
        asset_class="STK",
    )


class TestTipo2:
    def test_length_is_500(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert len(record) == modelo720.RECORD_LENGTH

    def test_starts_with_2720(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[:4] == "2720"

    def test_ejercicio(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[4:8] == "2025"

    def test_nif_position(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[8:17] == "Y1234567X"

    def test_clave_bien_is_V(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[101] == "V"

    def test_subclave_is_1(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[102] == "1"

    def test_country_code_is_broker(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[128:130] == "IE"

    def test_broker_name_in_entity_field(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[189:230].strip() == "INTERACTIVE BROKERS IRELAND LIMITED"

    def test_broker_tax_id(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[230:250].strip() == "657406"

    def test_broker_address(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert "NORTH DOCK ONE" in record[250:302]
        assert record[342:372].strip() == "DUBLIN"
        assert record[372:402].strip() == "DUBLIN"
        assert record[402:412].strip() == "D01 H7V7"
        assert record[412:414] == "IE"

    def test_isin_field(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[131:143].strip() == "US0378331005"

    def test_origen(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[422] == "A"

    def test_clave_representacion_valores(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[461] == "A"

    def test_porcentaje_participacion(self) -> None:
        config = _make_config()
        pos = _make_position()
        record = modelo720.generate_tipo2(config, pos)
        assert record[475:480] == "10000"


class TestTipo1:
    def test_length_is_500(self) -> None:
        config = _make_config()
        pos = _make_position()
        records = [modelo720.generate_tipo2(config, pos)]
        record = modelo720.generate_tipo1(config, records, [pos])
        assert len(record) == modelo720.RECORD_LENGTH

    def test_starts_with_1720(self) -> None:
        config = _make_config()
        pos = _make_position()
        records = [modelo720.generate_tipo2(config, pos)]
        record = modelo720.generate_tipo1(config, records, [pos])
        assert record[:4] == "1720"

    def test_record_count(self) -> None:
        config = _make_config()
        pos = _make_position()
        records = [modelo720.generate_tipo2(config, pos)]
        record = modelo720.generate_tipo1(config, records, [pos])
        assert record[135:144] == "000000001"

    def test_tipo_soporte(self) -> None:
        config = _make_config()
        pos = _make_position()
        records = [modelo720.generate_tipo2(config, pos)]
        record = modelo720.generate_tipo1(config, records, [pos])
        assert record[57] == "T"


class TestGenerateFile:
    def test_all_records_500(self) -> None:
        config = _make_config()
        positions = [_make_position()]
        records = modelo720.generate_file(config, positions)
        for r in records:
            assert len(r) == modelo720.RECORD_LENGTH

    def test_record_count_matches(self) -> None:
        config = _make_config()
        positions = [_make_position()]
        records = modelo720.generate_file(config, positions)
        assert len(records) == 2  # 1 tipo1 + 1 tipo2

    def test_first_record_is_tipo1(self) -> None:
        config = _make_config()
        positions = [_make_position()]
        records = modelo720.generate_file(config, positions)
        assert records[0][0] == "1"


class TestUsdToEur:
    def test_conversion(self) -> None:
        result = modelo720.usd_to_eur(103.86, 1.0386)
        assert abs(result - decimal.Decimal("100")) < decimal.Decimal("0.01")

    def test_conversion_real(self) -> None:
        result = modelo720.usd_to_eur(19030.20, 1.0386)
        expected = decimal.Decimal("19030.20") / decimal.Decimal("1.0386")
        assert abs(result - expected) < decimal.Decimal("0.01")


class TestCsvParser:
    def test_parse_ibkr_csv(self, tmp_path) -> None:
        csv_content = (
            '"ISIN","Description","Quantity","CurrencyPrimary",'
            '"PositionValue","AssetClass"\n'
            '"US0378331005","APPLE INC","70","USD","19030.2","STK"\n'
            '"ISIN","Description","Quantity","CurrencyPrimary",'
            '"PositionValue","AssetClass"\n'
            '"US0378331005","APPLE INC","30","USD","8155.8","STK"\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        positions = csv_parser.parse_ibkr_csv(csv_file)
        assert len(positions) == 1
        assert positions[0].isin == "US0378331005"
        assert positions[0].quantity == 100
        assert abs(positions[0].value - 27186.0) < 0.01

    def test_country_code_from_isin(self) -> None:
        pos = csv_parser.Position(
            isin="LR0008862868",
            description="ROYAL CARIBBEAN",
            quantity=2,
            currency="USD",
            value=557.84,
            asset_class="STK",
        )
        assert pos.country_code == "LR"
