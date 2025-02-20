import tomli

def read_data(file_input, credentials):
    """
    Read the configuration file given by user 
    """
    try:
        with open(file_input, "rb") as f:
            data = tomli.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"{file_input} not found")
    output = dict()

    try:
        # Extract credentials data
        if credentials:
            output["username"] = input("Enter username: ")
            output["password"] = input("Enter password: ")
            output["api_url"] = input ("Enter the HTTP url of the Olog API: ")
        else:
            #output['credendials'] = data['credentials']
            output["username"] = data['credentials']['username']
            output["password"] = data['credentials']['password']
            output["api_url"] = data['credentials']['api_url']

        # Extract autolog data
        output["autolog"] = data['autolog']
        output["title"] = data['autolog']['title']
        output["description"] = data['autolog']['description']
        output["level"] = data['autolog']['level']
        output["logbook"] = data['autolog']['logbook']

        # Extract pv data
        output["pv"] = data['pv']
        output["trigger_pv_name"] = data['pv']['trigger_pv_name']
        output['trigger_pv_value'] = data['pv']['trigger_pv_value']

        if 'check_time' in data['pv']:
            output['check_time'] = data['pv']['check_time']
        else:
            output['check_time'] = 5

        return output
    except KeyError as e:
        print(f"The variable: {e} is missing into the toml file")
        exit()