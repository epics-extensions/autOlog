# AutOlog

A python tool to create automatically a log into Phoebus-Olog server, and trigger by a PV value.

This tool needs to access the channel-access network where the EPICS IOC is running, and the Olog server.

See `example.toml` to know the exhaustive list of required variables.

The credentials data (username, password and url api of Olog server) can be entered manually by user.

Check the package registry to get a binary that could be run with `procserv` as a a background programme

Usage example:

`python src/autolog.py -c example/example.toml`

Help:

```bash
$ python src/autolog.py -h
usage: autolog.py [-h] [-c] config

A script to create automatically logs into Olog server

positional arguments:
  config             The configuration file with all the required data.

optional arguments:
  -h, --help         show this help message and exit
  -c, --credentials  Ask user for username, password and api_url
```