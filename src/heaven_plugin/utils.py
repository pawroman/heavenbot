import datetime
import math

from datetime import timedelta
from typing import Optional, Tuple, Union

import holidays
import pendulum
from tzlocal import get_localzone


PROGRESSBAR_BAR_EMPTY = "-"
PROGRESSBAR_BAR_HALF = "="
PROGRESSBAR_BAR_FULL = "#"

PROGRESSBAR_FORMAT = "[{bars}]"


def get_weekend_progress(
    now: Optional[datetime.datetime] = None,
    tz="Europe/Warsaw",
    weekend_start_hour=17, weekend_end_hour=9
) -> Tuple[float, str, pendulum.Period]:
    """
    Get the current week progress in respect to weekend start and end times.

    Return a triple:
    progress_ratio, remaining_duration, total_duration

    progress_ratio [0.0, 1.0)  - when it's not weekend (progress towards weekend)
                   (-1.0, 0.0) - when it's weekend (progress towards weekend end)

    Parameters:

    now:    the "now" time for progress calculation.
    tzname: the timezone name for which to perform calculation. If None,
            assume local timezone.

    Weekend begins on Friday, at `weekend_start_hour`, and ends on Monday, at
    `weekend_end_hour`:

              MONDAY                             FRIDAY                MONDAY
    weekend_end_hour                             weekend_start_hour    | ...end
                   |                             |                     |
                   |<--progress--->|             |                     |
                   |               |             |                     |
    ---------------|---------- >> now >> --------|---------------------|----...
                   |                             |                     |
    ----WEEKEND--->|---work days (NOT WEEKEND)-->|-------WEEKEND------>|----...

    """
    # TODO: support holidays
    # TODO better weekend calculations + configurability

    if not tz:
        tz = get_localzone()

    if now:
        # don't perform TZ conversion, just set it as is
        now = pendulum.instance(now).set(tz=tz)
    else:
        now = pendulum.now(tz=tz)

    weekday = now.isoweekday()

    if weekday == 1:
        weekend = now < (now.start_of("day") + timedelta(hours=weekend_end_hour))
        end_day = now
        start_day = now.previous(pendulum.FRIDAY) if weekend else now.next(pendulum.FRIDAY)
    elif weekday == 5:
        weekend = now >= (now.start_of("day") + timedelta(hours=weekend_start_hour))
        end_day = now.next(pendulum.MONDAY) if weekend else now.previous(pendulum.MONDAY)
        start_day = now
    elif 1 < weekday < 5:
        weekend = False
        end_day = now.previous(pendulum.MONDAY)
        start_day = now.next(pendulum.FRIDAY)
    else:
        weekend = True
        end_day = now.next(pendulum.MONDAY)
        start_day = now.previous(pendulum.FRIDAY)

    end = end_day.start_of("day") + timedelta(hours=weekend_end_hour)
    start = start_day.start_of("day") + timedelta(hours=weekend_start_hour)

    if weekend:
        progress = end - now
        remaining_duration = end - now
        period: pendulum.Period = end - start
    else:
        progress = now - end
        remaining_duration = start - now
        period: pendulum.Period = start - end

    progress_ratio = progress.total_seconds() / period.total_seconds()

    if weekend:
        progress_ratio *= -1.0

    return progress_ratio, remaining_duration.in_words(), period


def make_progressbar(value: float, bars: int = 10,
                     full_char: str = PROGRESSBAR_BAR_FULL,
                     half_char: str = PROGRESSBAR_BAR_HALF,
                     empty_char: str = PROGRESSBAR_BAR_EMPTY) -> str:
    """
    Make a simple ASCII progressbar for a value between 0.0 and 1.0, inclusive.

    bars: The number of progressbar "bars" / blocks (positive int).
    """
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"Invalid progressbar value: {value}")

    if not bars > 0:
        raise ValueError(f"Invalid number of bars: {bars}")

    percent = value * 100.0
    bar_step = 100.0 / bars

    ratio = percent / bar_step

    full_bars = math.floor(ratio)
    half_bar = (percent / bar_step) - full_bars >= 0.5
    empty_bars = bars - full_bars - half_bar

    bars_str = (
        # "str" * 2 -> "strstr"
        # "str" * 0 -> ""
        full_char * full_bars
        + half_char * half_bar
        + empty_char * empty_bars
    )

    return PROGRESSBAR_FORMAT.format(bars=bars_str)


def get_next_non_weekend_holiday(now: Union[datetime.datetime, datetime.date],
                                 country_code: str) -> Tuple[datetime.date, str]:
    this_year = now.year
    today = now.date() if isinstance(now, datetime.datetime) else now

    country_holidays = getattr(holidays, country_code)
    hols = country_holidays(years=[this_year, this_year + 1]).items()

    next_date, next_name = next(
        (date, name)
        for date, name in hols
        # holidays are iterated in sorted order (by date)
        if date >= today and date.isoweekday() not in (6, 7)
    )

    return next_date, next_name
