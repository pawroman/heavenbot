from datetime import date, datetime

import pendulum
from pytest import approx, fixture, raises

from src.weekend_plugin.utils import (
    get_weekend_progress, make_progressbar,
    get_next_non_weekend_holiday,
)


@fixture(scope="session")
def monday_10_am_utc():
    dt = pendulum.parse("2019-02-04T10:00:00", tz="UTC")
    pendulum.set_test_now(dt)

    yield dt

    pendulum.set_test_now()


def test_get_weekend_progress_friday():
    test_dt = datetime(2019, 2, 8, 15, 20)
    ratio, desc, period = get_weekend_progress(test_dt)

    assert ratio == approx(0.983974358)
    assert desc == "1 hour 40 minutes"
    assert period == pendulum.period(
        pendulum.datetime(2019, 2, 4, 9, tz="Europe/Warsaw"),
        pendulum.datetime(2019, 2, 8, 17, tz="Europe/Warsaw"),
    )


def test_get_weekend_progress_monday(monday_10_am_utc):
    ratio, desc, period = get_weekend_progress(tz=None)

    assert ratio == approx(0.0096153846)
    assert desc == "4 days 7 hours"
    assert period == pendulum.period(
        pendulum.datetime(2019, 2, 4, 9, tz="UTC"),
        pendulum.datetime(2019, 2, 8, 17, tz="UTC"),
    )


def test_get_weekend_progress_mid_week():
    dt = pendulum.parse("2019-02-20T13:00:00")
    assert dt.isoweekday() == 3

    ratio, desc, period = get_weekend_progress(dt)

    assert ratio == approx(0.5)
    assert desc == "2 days 4 hours"
    assert period == pendulum.period(
        pendulum.datetime(2019, 2, 18, 9, tz="Europe/Warsaw"),
        pendulum.datetime(2019, 2, 22, 17, tz="Europe/Warsaw"),
    )


def test_get_weekend_progress_friday_weekend():
    dt = pendulum.parse("2019-02-22T19:00:00")
    assert dt.isoweekday() == 5

    ratio, desc, period = get_weekend_progress(dt)

    assert ratio == approx(-0.96875)
    assert desc == "2 days 14 hours"
    assert period == pendulum.period(
        pendulum.datetime(2019, 2, 22, 17, tz="Europe/Warsaw"),
        pendulum.datetime(2019, 2, 25, 9, tz="Europe/Warsaw"),
    )


def test_get_weekend_progress_sunday():
    dt = pendulum.parse("2019-02-24T10:00:00")
    assert dt.isoweekday() == 7

    ratio, desc, period = get_weekend_progress(dt)

    assert ratio == approx(-0.359375)
    assert desc == "23 hours"
    assert period == pendulum.period(
        pendulum.datetime(2019, 2, 22, 17, tz="Europe/Warsaw"),
        pendulum.datetime(2019, 2, 25, 9, tz="Europe/Warsaw"),
    )


def test_make_progressbar():
    pbar_0_1 = make_progressbar(0.1, bars=10)
    assert pbar_0_1 == "[#---------]"

    pbar_half = make_progressbar(0.5, bars=5)
    assert pbar_half == "[##=--]"

    pbar_0_75_custom = make_progressbar(0.75, bars=5,
                                        full_char="@",
                                        half_char="/",
                                        empty_char=".")
    assert pbar_0_75_custom == "[@@@/.]"


def test_make_progressbar_invalid_values():
    with raises(ValueError, match="Invalid progressbar value"):
        _ = make_progressbar(1.2)

    with raises(ValueError, match="Invalid number of bars"):
        _ = make_progressbar(0.5, bars=-2)


def test_get_next_non_weekend_holiday():
    feb_8_2019 = datetime(2019, 2, 8)

    pl_date, pl_name = get_next_non_weekend_holiday(feb_8_2019, "PL")

    assert pl_date == date(2019, 4, 22)
    assert pl_name == "Poniedziałek Wielkanocny"

    ie_date, ie_name = get_next_non_weekend_holiday(feb_8_2019.date(), "IE")

    assert ie_date == date(2019, 3, 18)
    assert ie_name.startswith("St. Patrick's Day")

    with raises(AttributeError):
        _ = get_next_non_weekend_holiday(feb_8_2019, "BLAH")
