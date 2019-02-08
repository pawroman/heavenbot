# -*- coding: utf-8 -*-

from collections import defaultdict

import logging
import re

import pendulum

from irc3.plugins.command import command
from irc3.plugins.cron import cron
from irc3.utils import IrcString

import irc3

from .utils import (
    get_weekend_progress, make_progressbar,
    get_next_non_weekend_holiday,
)


@irc3.plugin
class WeekendPlugin:
    requires = [
        "irc3.plugins.core",
        "irc3.plugins.userlist",
        "irc3.plugins.command",
    ]

    def __init__(self, context):
        self.context = context
        self.config = self.context.config["weekend_plugin"]

        # registry of +o modes {"channel": True/False, ...}
        self.ops = defaultdict(bool)

        self.log = logging.getLogger("irc3")

    def connection_lost(self):
        """
        Triggered when connection is lost.
        """
        self.ops.clear()

    @property
    def weekend_topic_format(self):
        return self.config.get("weekend_topic_format")

    @property
    def weekend_topic_re(self):
        return self.config.get("weekend_topic_re").strip("\"")

    @property
    def weekday_topic_format(self):
        return self.config.get("weekday_topic_format")

    @property
    def weekday_topic_re(self):
        return self.config.get("weekday_topic_re").strip("\"")

    @irc3.event(irc3.rfc.JOIN)
    def on_join(self, channel=None, **kwargs):
        """
        Joined a channel.
        """
        self.ops[channel] = False

    @irc3.event(irc3.rfc.MODE)
    def on_mode_changed(self, target=None, modes=None, data=None, **kwargs):
        """
        User list has changed somehow.

        Cheer for +o if enabled and register channels where the bot is the operator in ``self.ops``.
        """
        if not (target and modes and data):
            return

        users = data.split()
        parsed_modes = irc3.utils.parse_modes(modes, users)

        my_mode = next(
            (
                (flag, mode_char)
                for (flag, mode_char, nick) in parsed_modes
                if nick == self.context.nick
            ),
            None
        )

        if not self.ops.get(target) and my_mode == ("+", "o"):
            self.ops[target] = True
            self.log.info("Got OP on {}".format(target))

            if self.config.get("enable_cheer_for_op"):
                return self.cheer_for_op(target)

            self.set_weekend_topic(target, self.context.channels[target].topic)

        elif target in self.ops and my_mode == ("-", "o"):
            self.ops[target] = False
            self.log.info("OP lost on {}".format(target))

    def cheer_for_op(self, target):
        """
        Cheer when offered +o mode.
        """
        message = self.config.get("cheer_for_op_message")
        if message:
            self.context.privmsg(target, message)

    @irc3.event(irc3.rfc.TOPIC)
    def on_topic_changed(self, channel=None, data=None, mask=None, **kw):
        """
        The topic has changed.
        """
        nick = IrcString(mask).nick     # who set the topic?

        if nick == self.context.nick:
            # don't change the topic that we just set
            return

        self.set_weekend_topic(channel, data)

    def set_weekend_topic(self, channel, raw_topic):
        user_topic = self.parse_user_topic(raw_topic)
        adj_topic = self.weekend_topic(user_topic)

        if self.context.channels[channel].topic != adj_topic:
            self.context.channels[channel].topic = adj_topic
            self.context.topic(channel, adj_topic)

    def parse_user_topic(self, raw_topic):
        user_topic = raw_topic

        for pattern in (self.weekend_topic_re, self.weekday_topic_re):
            if re.match(pattern, raw_topic):
                user_topic = re.sub(pattern, "", raw_topic).strip()
                break

        return user_topic

    def weekend_topic(self, user_topic):
        progress, duration, total_duration = get_weekend_progress(
            weekend_start_hour=int(self.config.get("weekend_start_hour", 17)),
            weekend_end_hour=int(self.config.get("weekend_end_hour", 9))
        )

        fmt_params = dict(
            progress=int(round(progress * 100)),
            progressbar=make_progressbar(abs(progress)),
            user_topic=user_topic,
        )

        if progress < 0:
            return self.weekend_topic_format.format(**fmt_params)
        else:
            return self.weekday_topic_format.format(**fmt_params)

    @command(permission="view", name="topic")
    def topic_cmd(self, mask, target, args):
        """
        Set the channel topic, prefixing the weekend progressbar.
        You need to be an operator to use this.

            %%topic <topic>...
        """
        nick = IrcString(mask).nick

        self.log.info("Topic command: {mask}, {target}, {args}".format(
            mask=mask, target=target, args=args)
        )

        # Someone set the topic. Check if they are permitted to do so.
        if nick in self.context.channels[target].modes["@"]:
            if self.context.nick in self.context.channels[target].modes["@"]:
                self.set_weekend_topic(target, " ".join(args["<topic>"]))
                self.log.info("Topic command succeeded")
            else:
                self.context.privmsg(
                    nick,
                    "I can't set a topic unless I have '+o' mode on {}.".format(target)
                )
                self.log.info("Topic command refused (no op)")
        else:
            self.context.privmsg(
                nick,
                "Get a '+o' on {} first to use the !topic command.".format(target)
            )

    @command(permission="view", name="weekend", public=False)
    def weekend_cmd(self, mask, target, args):
        """
            %%weekend [<options>...]
        """
        progress, duration, total_duration = get_weekend_progress()

        # TODO move these to config

        if progress < 0:
            yield ("It's WEEKEND, and there's {} ({:.2f}%) of it remaining!"
                   .format(duration, abs(progress) * 100))
        else:
            yield ("{} remaining until weekend... {:.2f}% {}"
                   .format(duration, abs(progress) * 100, make_progressbar(progress, 20)))

    @command(permission="view", name="holiday", public=True)
    def holiday_cmd(self, mask, target, args):
        """
        Show the upcoming non-weekend holidays
        for all countries in config.

            %%holiday
        """
        country_codes = self.config.get("holiday_countries")

        if not country_codes:
            return

        now = pendulum.now(tz=self.config.get("default_timezone"))

        for country_code in country_codes.split(","):
            date, name = get_next_non_weekend_holiday(now, country_code)

            remaining_days = (
                pendulum.date(date.year, date.month, date.day)
                - now
            ).in_days()

            plural = "" if remaining_days == 1 else "s"

            yield (
                f"Next holiday for {country_code}:"
                f" {date.isoformat()} ({name}"
                f", in {remaining_days} day{plural})"
            )

    # TODO better cron / periodic updates (+ config)

    @cron("0 0,7,9,11,13,15,17,20 * * *")
    def update_topic_periodically(self):
        # update all the channels

        for channel in self.ops:
            topic = self.context.channels[channel].topic
            self.set_weekend_topic(channel, topic)

