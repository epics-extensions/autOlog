"""Autolog main script"""
import time
import argparse
import logging
from autolog.olog_api.requests import post_request
from autolog.olog_api.olog import define_body
from autolog.config import read_data
from autolog.utils import trigger_action, check_multiple_condition

def argparser():
    """
    Argument parser
    """
    parser = argparse.ArgumentParser(description=
    "A python tool to create automatically logs into Phoebus-Olog server, triggered by EPICS Process Variable.")
    parser.add_argument("config", type=str,
    help="The configuration file (TOML format) with required data.")

    parser.add_argument("-c", "--credentials", action='store_true',
    help="Ask user for username, password and api_url")

    parser.add_argument(
        "-v",
        "--verbosity",
        type=int,
        choices=[0, 1, 2, 3, 4, 5],
        help="""
    decrease output verbosity. 5 (Critical), 4 (Error), 3 (Warning, default), 2 (Info), 1 (Debug)
    """,  # noqa: E501
        default=2,
    )

    return parser.parse_args()

def start_loop(user_data: dict):
    """
    Main thread
    """
    autolog = user_data['autolog']
    credentials = user_data['credentials']
    logging.debug("Autolog %s", autolog )
    # Main thread
    while True:
        for index, autolog_instance in enumerate(autolog):
            autolog_trigger = autolog_instance['trigger']
            logging.info("Handling Autolog %s of %s",{index + 1}, {len(autolog)} )
            if autolog_instance.get('condition'):
                condition = check_multiple_condition(autolog_instance['condition'])
                if not condition:
                    print("\n")
                    break
            order = trigger_action(autolog_trigger)
            if order:
                if not autolog_instance.get('created_once'):
                    autolog_content = define_body(credentials['username'],
                                                  autolog_trigger['trigger_pv_name'],
                                                  user_data['main_log_info'],
                                                  autolog_instance['context'])
                    post_request(autolog_content, credentials)
                    autolog_instance.update({'created_once': True})
                else:
                    logging.warning("Already created once")
            else:
                autolog_instance.update({'created_once': False})
            print("\n")
        time.sleep(user_data['main_log_info']['check_time'])

def main() -> None:
    """
    Main function
    """

    args = argparser()

    arg_debug = logging.WARNING if args.verbosity is None else args.verbosity * 10
    logging.basicConfig(level=arg_debug, format='%(levelname)s:  %(message)s')

    user_data = read_data(args.config, args.credentials)
    start_loop(user_data)

if __name__ == "__main__":
    main()
