from __future__ import annotations

import pathlib

RECORD_LENGTH = 500
ENCODING = "iso-8859-1"


def write_modelo720(
    records: list[str], output_path: str | pathlib.Path
) -> pathlib.Path:
    """Write a Modelo 720 file in the AEAT-required format.

    - Encoding: ISO-8859-1
    - Each line is exactly 500 bytes
    - Line separator: CRLF
    """
    path = pathlib.Path(output_path)

    for i, record in enumerate(records):
        encoded = record.encode(ENCODING)
        if len(encoded) != RECORD_LENGTH:
            raise ValueError(
                f"Record {i} is {len(encoded)} bytes, expected {RECORD_LENGTH}"
            )

    with open(path, "wb") as f:
        for record in records:
            f.write(record.encode(ENCODING))
            f.write(b"\r\n")

    return path
