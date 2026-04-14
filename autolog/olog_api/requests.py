"""Manage Olog API request"""

import json
import logging
import mimetypes
import os
import uuid

import requests


def post_request(log_entry: dict, attachment_file_paths: list, credentials: dict):
    """
    Send a multipart/form-data request to the Olog server.
    """

    log_url = credentials["api_url"] + "/logs/multipart"
    username = credentials["username"]
    password = credentials["password"]

    multipart = []
    opened_files = []

    try:
        # Add one "files" part for each attachment
        for path in attachment_file_paths:
            f = open(path, "rb")
            opened_files.append(f)

            filename = os.path.basename(path)
            mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"

            multipart.append(
                (
                    "files",
                    (
                        filename,
                        f,
                        mime_type,
                    ),
                )
            )
            log_entry["attachments"].append(
                {
                    "id": str(uuid.uuid4()),
                    "filename": filename,
                    "fileMetadataDescription": mime_type,
                }
            )

        multipart.append(
            (
                "logEntry",
                (
                    None,
                    json.dumps(log_entry),
                    "application/json",
                ),
            )
        )
        logging.debug("Log entry: %s", json.dumps(log_entry, indent=2))

        response = requests.put(
            log_url,
            files=multipart,
            auth=(username, password),
            timeout=10,
        )

        if response.status_code == 200:
            logging.info("Log entry created successfully.")
            logging.info("Response: %s", response.json())
            logging.debug("The attachment files are not included in the response")

        elif response.status_code == 400:
            logging.error("Bad request.")
            logging.error(response.text)

        elif response.status_code == 413:
            logging.error("Payload too large.")
            logging.error(response.text)

        else:
            logging.error(
                "Failed to create log entry. Status code: %s",
                response.status_code,
            )
            logging.error(response.text)

    except FileNotFoundError as exc:
        logging.error("Attachment file not found: %s", exc)

    except requests.exceptions.RequestException as exc:
        logging.error("Request failed: %s", exc)

    finally:
        for f in opened_files:
            f.close()
