# heavenbot - a Python IRC bot built using irc3

[![Build Status](https://cloud.drone.io/api/badges/pawroman/heavenbot/status.svg)](https://cloud.drone.io/pawroman/heavenbot)
[![codecov](https://codecov.io/gh/pawroman/heavenbot/branch/master/graph/badge.svg)](https://codecov.io/gh/pawroman/heavenbot)
![](https://img.shields.io/badge/Python-3.7-blue.svg)
[![Docker](https://img.shields.io/docker/pulls/heavenbot/heavenbot.svg?style=flat)](https://hub.docker.com/r/heavenbot/heavenbot)

Current features:

* weekend command - shows progress towards the weekend in channel topic
* holiday command - shows upcoming holidays

## Running

To run, you need to create a config file first.
You can use a sample one in  `sample-config.ini`
as a starting point.

Refer to irc3 documentation for more details:
https://irc3.readthedocs.io/en/latest/

### Docker

Using Docker is the simplest way to run the bot.

The images are available for x86_64 and ARM.
Find them here: https://hub.docker.com/r/heavenbot/heavenbot

The Docker image uses volume `/heavenbot/data`
to store bot's configs and other data.

All you need to get started is to have docker
on your system and a directory to mount as the
volume:

```bash
$ mkdir /abs-path-to/heavenbot-data
```

#### Optional: generate sample config file

You can generate a sample config file (assuming local
directory `/abs-path-to/heavenbot-data` will hold the bot data) like so:

```bash
$ docker run \ 
    -v /abs-path-to/heavenbot-data:/heavenbot/data \
    heavenbot/heavenbot \
    generate-config
```

This will create a `config.ini` file which you
should tweak for your purpose.

#### Run it

Using local directory `/abs-path-to/heavenbot-data`
for the volume mount:

```bash
$ docker run \ 
    -v /abs-path-to/heavenbot-data:/heavenbot/data \
    heavenbot/heavenbot
```

To run in background, use the `-d` flag:

```bash
$ docker run -d \ 
    -v /abs-path-to/heavenbot-data:/heavenbot/data \
    heavenbot/heavenbot
```

Note that if `config.ini` doesn't exist, it will error out.

### No Docker

The target compatibility is Python **3.6 and newer** only.
It might work with older versions, but they are
not supported.

* `pip install -r requirements.txt`
* `irc3 path/to/your-config.ini`

If you can't install Python 3.6 globally on your machine, you can try using *pyvenv*
https://github.com/yyuu/pyenv

## Development

See `requirements.txt` and `requirements-to-freeze.txt`. A virtualenv is recommended.

heavenbot tries to follow a better PIP workflow as descibed by Kenneth Reitz:
http://www.kennethreitz.org/essays/a-better-pip-workflow

In short:

* keep all installed requirements versioned (pip freeze) in `requirements.txt`

* keep the "top-level" requirements unversioned in `requirements-to-freeze.txt`

### Testing

First, install the test requirements:

```
$ pip install -r requirements-test.txt 
```

Then, run `pytest`:

```
$ pytest
```

## License

MIT. See the `LICENSE` file.
