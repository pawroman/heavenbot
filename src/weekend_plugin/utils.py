import math
from datetime import timedelta

import delorean
from tzlocal import get_localzone


PROGRESSBAR_BAR_EMPTY = "-"
PROGRESSBAR_BAR_HALF  = "="
PROGRESSBAR_BAR_FULL  = "#"

PROGRESSBAR_FORMAT    = "[{bars}]"


def get_weekend_progress(now=None, tzname="Europe/Warsaw",
                         weekend_start_hour=17, weekend_end_hour=9):
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

    if not tzname:
        tzname = str(get_localzone())

    now     = delorean.Delorean(datetime=now, timezone=tzname)

    now_dt  = now.datetime
    weekday = now_dt.isoweekday()

    if weekday == 1:
        weekend   = now_dt < (now.midnight + timedelta(hours=weekend_end_hour))
        end_day   = now
        start_day = now.last_friday() if weekend else now.next_friday()
    elif weekday == 5:
        weekend   = now_dt >= (now.midnight + timedelta(hours=weekend_start_hour))
        end_day   = now.next_monday() if weekend else now.last_monday()
        start_day = now
    elif 1 < weekday < 5:
        weekend   = False
        end_day   = now.last_monday()
        start_day = now.next_friday()
    else:
        weekend   = True
        end_day   = now.next_monday()
        start_day = now.last_friday()

    end      = end_day.midnight   + timedelta(hours=weekend_end_hour)
    start    = start_day.midnight + timedelta(hours=weekend_start_hour)
    duration = start - end

    if not weekend:
        progress = now_dt - end
        remaining_duration = start - now_dt
    else:
        progress = end - now_dt
        remaining_duration = end - now_dt

    progress_ratio = progress.total_seconds() / duration.total_seconds()

    return progress_ratio, remaining_duration, duration


def make_progressbar(value, bars=10):
    """
    Make a simple ASCII progressbar for a value between 0.0 and 1.0, inclusive.

    bars: The number of progressbar "bars" / blocks (positive int).
    """
    if not 0.0 <= value <= 1.0:
        raise ValueError("Invalid progressbar value: {}".format(value))

    if not bars > 0:
        raise ValueError("Invalid bars number: {}".format(bars))

    # HACK when multiplied * 100, has fewer rounding errors
    percent    = value * 100

    bar_step   = 100.0 / bars
    ratio      = percent / bar_step

    full_bars  = math.floor(ratio)
    half_bar   = (percent / bar_step) - full_bars >= 0.5
    empty_bars = bars - full_bars - half_bar

    bars_str = (
        # "str" * 2 -> "strstr"
        # "str" * 0 -> ""
        PROGRESSBAR_BAR_FULL    * full_bars
        + PROGRESSBAR_BAR_HALF  * half_bar
        + PROGRESSBAR_BAR_EMPTY * empty_bars
    )

    return PROGRESSBAR_FORMAT.format(bars=bars_str)
