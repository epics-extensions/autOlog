# AutOlog

## Presentation

A python tool to create automatically logs into Phoebus-Olog server, triggered by EPICS PVs.

This tool needs to access the channel-access network where the EPICS IOCs are running, and the API of the Phoebus-Olog server.

This python tool could be generated as a binary and then integrated as a daemon using [`procserv`](https://github.com/ralphlange/procserv).

## Installation

### Using Poetry

First, install Poetry.
Refer to the [Poetry](https://duckduckgo.com) for instructions.

To build the project, run:

```bash
poetry install
```

To use it:

```bash
poetry run autolog -h
```

Or:

```bash
poetry run python -m autolog.autolog -h

```

### Using Binary

```bash
poetry run build
```

It is using PyInstaller to create a binary in **dist**

```bash
cd dist
autolog -h
```

## Usage

Usage example:

`autolog example/example.toml`

Help:

```bash
usage: autolog.py [-h] [-c] [-v {0,1,2,3,4,5}] config

A python tool to create automatically logs into Phoebus-Olog server, triggered by EPICS Process Variables.

positional arguments:
  config                The configuration file (TOML format) with required data.

optional arguments:
  -h, --help            show this help message and exit
  -c, --credentials     Ask user for username, password and api_url
  -v {0,1,2,3,4,5}, --verbosity {0,1,2,3,4,5}
                        decrease output verbosity. 5 (Critical), 4 (Error), 3 (Warning, default), 2 (Info), 1 (Debug)
```

## TOML file

See `example/example.toml` for complete example of a configuration file.

The result in Phoebus for autolog instance 1:

!["autolog instance 1"](doc/resources/autolog-1.png)

The result in the web client for autolog instance 2:

!["autolog instance 1"](doc/resources/autolog-2.png)

## Tests

`poetry run pytest`

Run unit test, for example to test log_content.py:
`poetry run pytest -m log_content`

## TOML Configuration Keys

The `example.toml` file provides an example configuration. It includes sections for credentials, main log information, and autolog instances.

### Table of Contents

1. [Credentials](#credentials)
2. [Main Log Information](#main-log-information)
3. [Autolog Instances](#autolog-instances)
   - [Trigger](#trigger)
   - [Condition](#condition)
   - [Context](#context)

### Credentials

Can be entered manually using the credentials argument.

```toml
[credentials]
  username = "<username>"
  password = "<password>"
  api_url = "<api_url>"
```

- **`username`**: The username for logging in Phoebus-Olog.
- **`password`**: The password for logging in Phoebus-Olog.
- **`api_url`**: The API URL of Phoebus-Olog as defined in Phoebus settings.

### Main Log Information

```toml
[main_log_info]
  title = "Here is the title of the log"
  description = "Here is the description of the log"
  level = "info"
  logbook = "controls"
  tags = ["Autolog","Test"] #not required
  check_time = 3 #not required. Loop time, default value: 5s
  attachment_files = [ "example/test.txt" ]  # absolute or relative path to the location where the script is being run



```

- **`title`** (required): The title of the log entry.
- **`description`** (required): A description of the log entry.
- **`level`** (required): The log level (e.g., `info`, `error`).
- **`logbook`** (required): The logbook to which the entry belongs.
- **`tags`** (optional): Tags associated with the log entry.
- **`check_time`** (optional): Loop time for checking conditions, default value is 5 seconds.
- **`attachment_files`** (optional): Files to attach to the log

### Autolog Instances

The `[[autolog]]` section can be repeated multiple times to define different autolog instances.

#### Trigger

```toml
[autolog.trigger]
  trigger_pv_name = "AUTOLOG-TEST:TRIGGER-LOG"
  on_change = true # Use either `on_change` or `trigger_pv_value`
  trigger_pv_value = [1, 2, 3, 4] # Use either `on_change` or `trigger_pv_value`
```

- **`trigger_pv_name`** (required): The name of the process variable (PV) that triggers the autolog.
- **`on_change`** (optional): If set to `true`, the autolog will trigger on any change in the trigger PV. Use either `on_change` or `trigger_pv_value`.
- **`trigger_pv_value`** (optional): The specific values of the trigger PV that should trigger the autolog. Use either `on_change` or `trigger_pv_value`.

#### Condition

The `[autolog.condition]` section is optional.
The `[[autolog.condition.pv]]` section is optional, and can be repeated multiple times to define different conditions.

```toml
[autolog.condition] #not required
  logical_condition = 'or' #'and' or 'or'. Default value: 'and'
  [[autolog.condition.pv]]
    condition_pv_name = "AUTOLOG-TEST:CONDITION-1"
    condition_pv_value = [0]

  [[autolog.condition.pv]]
    condition_pv_name = "AUTOLOG-TEST:CONDITION-2"
    condition_pv_value = [1]
```

- **`logical_condition`** (optional): The logical condition to apply to multiple PVs (`'and'` or `'or'`). Default value is `'and'`.
- **`condition_pv_name`** (optional): The name of the condition PV.
- **`condition_pv_value`** (optional): The specific values of the condition PV that should satisfy the condition.

#### Context

The `[[autolog.context]]` section is optional, and can be repeated multiple times to define different conditions.

```toml
[[autolog.context]] #not required
  description = "The context of the first autolog instance:"
  [autolog.context.pv]
    info_pv_name = "AUTOLOG-TEST:CONTEXT"
    info_pv_desc = true
    as_string = 'yes' #  Default value: 'no', options: 'yes', 'only'
```

- **`description`** (optional): A description for the context.
- **`attachment_file`** (optional): The path to an attachment file.
- **`info_pv_name`** (optional): The name of the context PV.
- **`as_string`** (optional): If set to `'yes'` or `'only'`, the PV value is treated as a string. Default value is `'no'`. Useful for mbbi/mbbo PVs, for example.
- **`info_pv_desc`** (optional): If set to `true`, includes the description of the PV.
