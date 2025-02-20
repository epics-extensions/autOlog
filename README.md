# AutOlog

A python tool to create automatically logs into Phoebus-Olog server, triggered by a PV value.

This tool needs to access the channel-access network where the EPICS IOC is running, and the API of the Phoebus-Olog server.

See `example.toml` to know the exhaustive list of variables.

The credentials data `username`, `password` and `api_url` (as provided in the phoebus `settings.ini` file) can be entered manually by user.

Check the package registry to get a binary that could be run with `procserv` as a a background programme.

Usage example:

`python src/autolog.py -c example/example.toml`

Help:

```bash
usage: autolog.py [-h] [-c] config

A python tool to create automatically logs into Phoebus-Olog server, triggered by a PV value.

positional arguments:
  config             The configuration file with all the required data.

optional arguments:
  -h, --help         show this help message and exit
  -c, --credentials  Ask user for username, password and api_url
```
