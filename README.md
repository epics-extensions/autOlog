# AutOlog

## Presentation

A python tool to create automatically logs into Phoebus-Olog server, triggered by a PV value.

This tool needs to access the channel-access network where the EPICS IOC is running, and the API of the Phoebus-Olog server.

Check the package registry to get a binary that could be run with `procserv` as a a background programme.

## autolog/

Code source with `poetry`

## doc/

Documentation

## Installation

### Using Poetry

First, install Poetry.
Refer to the [Poetry](https://duckduckgo.com) for instructions.

To build the project,
you can run:

``` bash
poetry install
poetry run build
```

It is using PyInstaller to create a binary in **dist**

## Execution

### Using Poetry

To run the script from anywhere in the directory execute

``` bash
poetry shell
```

Then you can call the script from anywhere

``` bash
autolog -c example/example.toml
```

### Using Binary

If you have build the binary you can

``` bash
> cd dist
> autolog -h
```

## Usage

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

## TOML file

descriptino
