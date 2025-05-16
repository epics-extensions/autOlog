"""Module to check and load data from a TOML configuration file, exit if not correct"""
import sys
import tomli
import cerberus


schema = {
    'credentials': {
        'type': 'dict',
        'schema': {
            'username': {'type': 'string', 'required': False},
            'password': {'type': 'string', 'required': False},
            'api_url': {'type': 'string', 'required': False},
        }

},
    'autolog': {
        'type': 'dict',
        'schema': {
            'title': {'type': 'string', 'required': True},
            'description': {'type': 'string', 'required': True},
            'level': {'type': 'string', 'required': True},
            'logbook': {'type': 'string', 'required': True},
            'attachment_file': {'type': 'string', 'required': False},

        }

},
    'pv': {
        'type': 'dict',
        'schema': {
            'check_time': {'type': 'integer', 'required': False, 'default': 5},
            'trigger_pv_name': {'type': 'string', 'required': True},
            'trigger_pv_value': {'type': 'list', 'required': True, 'schema': {'type': 'integer'}},
            'condition': {
                'type': 'dict',
                'schema': {
                    'condition_pv_name': {'type': 'string', 'required': False},
                    'condition_pv_value': {'type': 'list', 'required': False, 
                                           'schema': {'type': 'integer'}},
                    }
                },
            'context': {
                'type': 'dict',
                'schema': {
                    'info_pv_name': {'type': 'string', 'required': False},
                    }
                }
            }
    }
}

def read_data(file_input, credentials):
    """
    Read the configuration file given by user and return a dict
    """
    try:
        with open(file_input, "rb") as f:
            data = tomli.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"{file_input} not found") from e

    if credentials:
        data["credentials"]["username"] = input("Enter username: ")
        data["credentials"]["password"] = input("Enter password: ")
        data["credentials"]["api_url"] = input ("Enter the HTTP url of the Olog API: ")
    v = cerberus.Validator()
    if v.validate(data, schema): #type: ignore
        return v.validated(data) #type: ignore
    print("Schema validation failed:", v.errors) #type: ignore
    print("Configuration is invalid, please refer to README to know the parameters")
    sys.exit()
