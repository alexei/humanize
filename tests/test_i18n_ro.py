"""Romanian translation tests.

Romanian has three plural forms: one (1), few (0, 2-19) and many (20+, which
takes "de": "20 de minute"). Most cases below cover all three.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterator

import pytest
from freezegun import freeze_time

import humanize

NOW = dt.datetime(2020, 2, 2, 12, 0, 0)


@pytest.fixture(autouse=True)
def romanian() -> Iterator[None]:
    try:
        humanize.activate("ro")
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    yield
    humanize.deactivate()


@pytest.mark.parametrize(
    "value, male, female",
    [
        (0, "al 0-lea", "a 0-a"),
        (1, "primul", "prima"),
        (2, "al 2-lea", "a 2-a"),
        (3, "al 3-lea", "a 3-a"),
        (4, "al 4-lea", "a 4-a"),
        (11, "al 11-lea", "a 11-a"),
        (12, "al 12-lea", "a 12-a"),
        (13, "al 13-lea", "a 13-a"),
        (21, "al 21-lea", "a 21-a"),
        (101, "al 101-lea", "a 101-a"),
        (111, "al 111-lea", "a 111-a"),
    ],
)
def test_ordinal(value: int, male: str, female: str) -> None:
    assert humanize.ordinal(value) == male
    assert humanize.ordinal(value, gender="female") == female


@pytest.mark.parametrize(
    "value, expected",
    [
        # Romanian says "o mie" or "1 mie", but "1,0" is how `intword` formats it.
        (1_000, "1,0 mie"),
        (1_200, "1,2 mii"),
        (20_000, "20,0 de mii"),
        (1_000_000, "1,0 milion"),
        (1_200_000, "1,2 milioane"),
        (20_000_000, "20,0 de milioane"),
        (1_000_000_000, "1,0 miliard"),
        (2_000_000_000, "2,0 miliarde"),
        (10**12, "1,0 bilion"),
        (10**15, "1,0 biliard"),
        (10**18, "1,0 trilion"),
        (10**21, "1,0 triliard"),
        (10**24, "1,0 cvadrilion"),
        (10**27, "1,0 cvadriliard"),
        (10**30, "1,0 cvintilion"),
        (10**33, "1,0 cvintiliard"),
        (10**100, "1,0 googol"),
        (-1_200_000, "-1,2 milioane"),
    ],
)
def test_intword(value: int, expected: str) -> None:
    assert humanize.intword(value) == expected


def test_apnumber() -> None:
    assert [humanize.apnumber(n) for n in range(10)] == [
        "zero",
        "unu",
        "doi",
        "trei",
        "patru",
        "cinci",
        "șase",
        "șapte",
        "opt",
        "nouă",
    ]


@pytest.mark.parametrize(
    "delta, expected",
    [
        (dt.timedelta(0), "un moment"),
        (dt.timedelta(seconds=1), "o secundă"),
        (dt.timedelta(seconds=2), "2 secunde"),
        (dt.timedelta(seconds=20), "20 de secunde"),
        (dt.timedelta(minutes=1), "un minut"),
        (dt.timedelta(minutes=2), "2 minute"),
        (dt.timedelta(minutes=20), "20 de minute"),
        (dt.timedelta(hours=1), "o oră"),
        (dt.timedelta(hours=2), "2 ore"),
        (dt.timedelta(hours=20), "20 de ore"),
        (dt.timedelta(days=1), "o zi"),
        (dt.timedelta(days=2), "2 zile"),
        (dt.timedelta(days=31), "o lună"),
        (dt.timedelta(days=62), "2 luni"),
        (dt.timedelta(days=365), "un an"),
        # Romanian would say "un an și o zi", but a single day uses the generic
        # "1 year, %d day" message. Months have a dedicated "1 year, 1 month"
        # message; days have no "1 year, 1 day" equivalent.
        (dt.timedelta(days=366), "un an și 1 zi"),
        (dt.timedelta(days=368), "un an și 3 zile"),
        (dt.timedelta(days=365 + 31), "un an și o lună"),
        (dt.timedelta(days=365 + 62), "un an și 2 luni"),
        (dt.timedelta(days=2 * 365), "2 ani"),
        (dt.timedelta(days=25 * 365), "25 de ani"),
        (dt.timedelta(days=1234 * 365), "1.234 de ani"),
    ],
)
def test_naturaldelta(delta: dt.timedelta, expected: str) -> None:
    assert humanize.naturaldelta(delta) == expected


@pytest.mark.parametrize(
    "value, unit, expected",
    [
        (dt.timedelta(microseconds=1), "microseconds", "1 microsecundă"),
        (dt.timedelta(microseconds=2), "microseconds", "2 microsecunde"),
        (dt.timedelta(microseconds=20), "microseconds", "20 de microsecunde"),
        (dt.timedelta(milliseconds=1), "milliseconds", "1 milisecundă"),
        (dt.timedelta(milliseconds=2), "milliseconds", "2 milisecunde"),
        (dt.timedelta(milliseconds=20), "milliseconds", "20 de milisecunde"),
    ],
)
def test_naturaldelta_minimum_unit(
    value: dt.timedelta,
    unit: str,
    expected: str,
) -> None:
    assert humanize.naturaldelta(value, minimum_unit=unit) == expected


@pytest.mark.parametrize(
    "delta, past, future",
    [
        (dt.timedelta(0), "acum", "acum"),
        (dt.timedelta(seconds=1), "acum o secundă", "peste o secundă"),
        (dt.timedelta(minutes=20), "acum 20 de minute", "peste 20 de minute"),
        (dt.timedelta(days=2), "acum 2 zile", "peste 2 zile"),
    ],
)
def test_naturaltime(delta: dt.timedelta, past: str, future: str) -> None:
    assert humanize.naturaltime(NOW - delta, when=NOW) == past
    assert humanize.naturaltime(NOW + delta, when=NOW) == future


@pytest.mark.parametrize(
    "delta, unit, expected",
    [
        (
            dt.timedelta(days=1, hours=2, minutes=3),
            "seconds",
            "1 zi, 2 ore și 3 minute",
        ),
        (dt.timedelta(seconds=90), "seconds", "1 minut și 30 de secunde"),
        (
            dt.timedelta(seconds=21, milliseconds=500),
            "milliseconds",
            "21 de secunde și 500 de milisecunde",
        ),
    ],
)
def test_precisedelta(delta: dt.timedelta, unit: str, expected: str) -> None:
    assert humanize.precisedelta(delta, minimum_unit=unit) == expected


@freeze_time(NOW)
@pytest.mark.parametrize("days, expected", [(-1, "ieri"), (0, "astăzi"), (1, "mâine")])
def test_naturalday(days: int, expected: str) -> None:
    assert humanize.naturalday(NOW.date() + dt.timedelta(days=days)) == expected


@pytest.mark.parametrize(
    "value, binary, expected",
    [
        (1, False, "1 octet"),
        (2, False, "2 octeți"),
        # Romanian would say "300 de octeți", but "%d Bytes" is not a plural
        # message, so the catalog can't pick the form with "de".
        (300, False, "300 octeți"),
        # Romanian would say "3,0 kB", but naturalsize ignores the locale's
        # decimal separator.
        (3_000, False, "3.0 kB"),
        (3_000, True, "2.9 KiB"),
    ],
)
def test_naturalsize(value: int, binary: bool, expected: str) -> None:
    assert humanize.naturalsize(value, binary=binary) == expected


@pytest.mark.parametrize("locale", ["ro", "ro_RO", "ro_MD"])
def test_locale_codes(locale: str) -> None:
    humanize.activate(locale)
    assert humanize.ordinal(1) == "primul"
    assert humanize.intcomma(1_234_567.89) == "1.234.567,89"
